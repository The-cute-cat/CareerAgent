from neo4j import GraphDatabase
import json
import uuid
from datetime import datetime
import numpy as np
from config import settings
from ai_service.models.struct_job_txt import (
    JDAnalysisResult,
    Profiles,
    BasicRequirements,
    ProfessionalSkills,
    ProfessionalLiteracy,
    DevelopmentPotential,
    JobAttributes,
)
from ai_service.models.graph import (
    GraphNodeJob,
    JobCompetency,
    GraphEdgeEvolve,
    JobEvolution,
    GraphRequiresIdfEvidence,
    GraphNodeBuildRun,
)
from collections import defaultdict
from typing import Literal, Dict, Tuple, List, Any
from sentence_transformers import SentenceTransformer
from ai_service.services.graph_algorithms import GraphAlgorithms
from ai_service.services import log


class GraphRepository:
    def __init__(self, url: str, user: str, password: str, *, load_model: bool = True):
        self.driver = GraphDatabase.driver(url, auth=(user, password))
        self.model = (
            SentenceTransformer("all-MiniLM-L6-v2") if load_model else None
        )  # 用于文本Embedding的轻量级模型（可按需加载）

    def init_constraints(self):
        with self.driver.session() as session:
            # 1. 确保岗位 ID 唯一，并加速 WHERE j.id = '...' 查询
            session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (j:Job) REQUIRE j.id IS UNIQUE"
            )
            # 2. 确保能力节点名字唯一，并加速 MERGE (c:Competency {name: '...'})
            session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Competency) REQUIRE c.name IS UNIQUE"
            )
            # 3. 确保每次离线建图Run可被追溯
            session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (r:BuildRun) REQUIRE r.id IS UNIQUE"
            )
            print("物理约束与索引创建完毕！")

    def upsert_build_run(self, run_id: str, status: str, meta: Dict[str, Any], ts: str):
        """将离线建图的全局参数/统计快照固化到 Neo4j，供在线推理回溯。"""
        meta_json = json.dumps(meta, ensure_ascii=False)

        # 通过 graph.py 的模型约束写入字段，避免 BuildRun 节点属性漂移
        run_node = GraphNodeBuildRun(
            id=run_id,
            created_at=ts,
            updated_at=ts,
            status=status,
            meta_json=meta_json,
            jaccard_threshold=meta.get("params", {}).get("jaccard_threshold"),
            coarse_resolution=meta.get("params", {}).get("coarse_resolution"),
            fine_resolution=meta.get("params", {}).get("fine_resolution"),
        )

        created_at = run_node.model_dump(include={"created_at"}, exclude_none=True).get(
            "created_at"
        )
        update_props = run_node.model_dump(
            exclude={"id", "created_at"}, exclude_none=True
        )

        cypher = """
        MERGE (r:BuildRun {id: $run_id})
        ON CREATE SET r.created_at = $created_at
        SET r += $update_props
        """

        with self.driver.session() as session:
            session.run(
                cypher,
                run_id=run_id,
                created_at=created_at,
                update_props=update_props,
            )

    def cleanup_old_evolve_edges(self, keep_run_id: str) -> int:
        """只保留指定 run_id 生成/更新过的 EVOLVE_TO，其余旧边全部删除。

        目的：避免周期性重跑后图中残留旧边，导致在线寻路（Dijkstra）被历史路线污染。
        """

        cypher = """
        MATCH ()-[e:EVOLVE_TO]->()
        WHERE e.build_run_id IS NULL OR e.build_run_id <> $keep_run_id
        DELETE e
        """

        with self.driver.session() as session:
            result = session.run(cypher, keep_run_id=keep_run_id)
            summary = result.consume()

            # Neo4j Python Driver: summary.counters.relationships_deleted
            deleted = getattr(
                getattr(summary, "counters", None), "relationships_deleted", 0
            )
            return int(deleted or 0)

    # 输入数据类型安全校验
    @staticmethod
    def _validate_input_data(job_data: dict) -> bool:
        """
        严格校验job_data中的关键字段是否为数字类型
        """
        required_numeric_fields = ["salary_rank", "min_degree", "min_experience"]
        for job_id, info in job_data.items():
            for field in required_numeric_fields:
                if field in info:
                    value = info[field]
                    if not isinstance(value, (int, float)):
                        log.error(
                            f"🚨 输入数据类型错误！\n"
                            f"岗位 {job_id} 的字段 '{field}' 不是数字类型，当前值：{value}，类型：{type(value)}\n"
                            f"请确保在传入 job_data 之前，已经将 '本科'、'高'、'1-3年' 等字符串转换为数字！"
                        )
                        return False
        return True

    # 从图数据库中取出已固化的岗位-能力关系(全量)， 直接返回cypher查询结果
    def get_all_job_competencies(self) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
            MATCH (j:Job)-[r:REQUIRES]->(c:Competency)
            RETURN j.id AS job_id, j.job_name AS job_name, c.name AS comp_name, c.category AS comp_category,
                   r.weight AS weight,
                   r.local_weight AS local_weight,
                   r.idf_weight AS idf_weight,
                   r.df AS df,
                   r.total_jobs AS total_jobs,
                   r.prevalence AS prevalence,
                   r.min_score AS min_score, r.context AS context
            """
            )
            return result.data()

    # 从图数据库中取出已固化的岗位-能力关系, 只提取IDF计算需要的字段（job_id和comp_name）
    def fetch_counts_for_idf(self, build_run_id: str | None = None):
        with self.driver.session() as session:
            # 只需要 job_id 和能力名即可算出全局分布
            result = session.run(
                """
                MATCH (j:Job)-[r:REQUIRES]->(c:Competency)
                WHERE $build_run_id IS NULL OR r.build_run_id = $build_run_id
                RETURN j.id AS job_id, c.name AS comp_name
            """,
                build_run_id=build_run_id,
            )
            return result.data()

    # 从图数据库中取出所有岗位和能力的权重关系，只提取加权杰卡德相似度需要的字段
    def fetch_all_for_jaccard(self, build_run_id: str | None = None):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (j:Job)-[r:REQUIRES]->(c:Competency)
                WHERE $build_run_id IS NULL OR r.build_run_id = $build_run_id
                RETURN j.id AS job_id, c.name AS comp_name, r.weight AS weight
            """,
                build_run_id=build_run_id,
            )
            return result.data()

    # 捞取所有Job节点结构化属性（缺省值保护）
    def get_all_jobs(self, build_run_id: str | None = None) -> Dict[str, Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                    MATCH (j:Job)
                    WHERE $build_run_id IS NULL OR j.last_build_run_id = $build_run_id
                        RETURN j.id AS id,
                            j.id AS job_id,
                            coalesce(j.job_name, '') AS job_name,
                            coalesce(j.macro_community_id, 0) AS macro_community_id,
                            coalesce(j.micro_community_id, 0) AS micro_community_id,
                            j.last_build_run_id AS last_build_run_id,
                            j.last_build_ts AS last_build_ts,
                            coalesce(j.salary_rank, 1) AS salary_rank,
                            coalesce(j.min_experience, 0) AS min_experience,
                            coalesce(j.min_degree, 0) AS min_degree,
                            coalesce(j.major, '') AS major,
                            coalesce(j.demand_rank, 2) AS demand_rank,
                            coalesce(j.trend_rank, 0) AS trend_rank,
                            coalesce(j.industry, '') AS industry,
                            coalesce(j.career_orientation, '') AS career_orientation,
                            // 软素质文本（用于cos_low语义计算）
                            coalesce(j.comm_desc, '') AS comm_desc,
                            coalesce(j.stress_desc, '') AS stress_desc,
                            coalesce(j.team_desc, '') AS team_desc,
                            coalesce(j.logic_desc, '') AS logic_desc,
                            // 发展潜力文本（用于cos_low语义计算）
                            coalesce(j.learn_desc, '') AS learn_desc,
                            coalesce(j.innov_desc, '') AS innov_desc,
                            coalesce(j.lead_desc, '') AS lead_desc,
                            coalesce(j.adapt_desc, '') AS adapt_desc,
                            coalesce(j.ethics_desc, '') AS ethics_desc,
                            // 项目&实习需求文本（用于Agent阅读）
                            coalesce(j.project_reqs, '') AS project_reqs,
                            coalesce(j.intern_reqs, '') AS intern_reqs,
                            // 特殊要求文本（用于Agent阅读）
                            coalesce(j.special_reqs, '') AS special_reqs
            """,
                build_run_id=build_run_id,
            )
            return {item["job_id"]: item for item in result.data()}

    # 将list[JobEvolution]存进图数据库
    def save_job_evolve(self, job_evolve_list: List[JobEvolution]):
        """
        高性能批量写入 JobEvolution 到 Neo4j
        - 自动 MERGE Job 节点（避免重复创建）
        - 自动更新节点的社区标签等新属性
        - 精准 SET EVOLVE_TO 关系属性，无冗余污染
        """
        if not job_evolve_list:
            log.warning("⚠️ job_evolve_list 为空，跳过写入")
            return

        log.info(f"🔹 开始批量写入 JobEvolution，总数：{len(job_evolve_list)}")

        # 1. 将 Pydantic 模型列表转换为 Neo4j 批量写入的 Payload
        batch_payload = []
        for job_evolve in job_evolve_list:
            # 转换为字典，exclude_none=True 跳过空值，节省空间
            from_node_dict = job_evolve.from_job.model_dump(exclude_none=True)
            to_node_dict = job_evolve.to_job.model_dump(exclude_none=True)
            edge_dict = job_evolve.edge.model_dump(exclude_none=True)

            batch_payload.append(
                {
                    "from_node": from_node_dict,
                    "to_node": to_node_dict,
                    "edge_props": edge_dict,
                }
            )

        # 2. 高性能 UNWIND 批量写入 Cypher
        # 核心逻辑：
        # - MERGE 确保节点存在，同时更新所有属性（包括新注入的社区标签）
        # - 精准 SET 关系属性，只存 GraphEdgeEvolve 里的业务指标
        cypher = """
        UNWIND $batch_payload AS data

        // 处理起点 Job 节点
        MERGE (from_job:Job {id: data.from_node.id})
        SET from_job += data.from_node

        // 处理终点 Job 节点
        MERGE (to_job:Job {id: data.to_node.id})
        SET to_job += data.to_node

        // 处理 EVOLVE_TO 关系
        MERGE (from_job)-[e:EVOLVE_TO]->(to_job)
        SET e += data.edge_props

        // 缺省保护（部分字段可能不存在于 edge_props；缺省时写入 0）
        SET e.pareto_rank = coalesce(e.pareto_rank, 0),
            e.pareto_group_size = coalesce(e.pareto_group_size, 0),
            e.pareto_front_size = coalesce(e.pareto_front_size, 0)
        """

        # 3. 执行 Cypher
        with self.driver.session() as session:
            session.run(cypher, batch_payload=batch_payload)

        # 4. 最终校验（可选，给你定心丸）
        with self.driver.session() as session:
            node_count = session.run("MATCH (j:Job) RETURN count(j) AS cnt").single()[
                "cnt"
            ]
            edge_count = session.run(
                "MATCH ()-[e:EVOLVE_TO]->() RETURN count(e) AS cnt"
            ).single()["cnt"]

        log.info("🎉 ==============================================")
        log.info("🎉 JobEvolution 批量写入完成！")
        log.info(f"✅ 总 Job 节点数：{node_count}")
        log.info(f"✅ 总 EVOLVE_TO 边数：{edge_count}")
        log.info("🎉 ==============================================")

    # 将list[JobCompetency]存进图数据库
    def save_job_competencies(
        self,
        job_competencies: List[JobCompetency],
        build_run_id: str | None = None,
        build_ts: str | None = None,
    ):
        # ==========================================
        # 1. 数据预处理：将 Pydantic 对象降维成字典列表
        # ==========================================
        batch_data = []
        for jc in job_competencies:
            # 注意：社区标签由后续聚类阶段产出；此处不应把旧标签重置为 0，否则会破坏跨 Run 的稳定性对比。
            job_props = jc.from_job.model_dump(
                exclude={"id", "macro_community_id", "micro_community_id"},
                exclude_none=True,
            )
            if build_run_id:
                job_props["last_build_run_id"] = build_run_id
            if build_ts:
                job_props["last_build_ts"] = build_ts

            comp_props = jc.to_competency.model_dump(
                exclude={"name"}, exclude_none=True
            )

            edge = jc.edge
            if build_run_id or build_ts:
                edge = edge.model_copy(
                    update={
                        "build_run_id": build_run_id,
                        "build_ts": build_ts,
                    }
                )
            edge_props = edge.model_dump(exclude_none=True)

            batch_data.append(
                {
                    "job_id": jc.from_job.id,
                    # 使用 model_dump() 兼容 Pydantic V2，剔除 id 避免重复赋值
                    "job_props": job_props,
                    "comp_name": jc.to_competency.name,
                    "comp_props": comp_props,
                    "edge_props": edge_props,
                }
            )

        # ==========================================
        # 2. 核心 Cypher：三合一的 UNWIND 批量语句
        # ==========================================
        cypher = """
        // 展开 Python 传进来的大列表，每行命名为 row
        UNWIND $batch AS row

        // 1. MERGE 岗位节点并批量设置属性
        MERGE (j:Job {id: row.job_id})
        SET j += row.job_props

        // 2. MERGE 能力节点并设置二级维度标签
        MERGE (c:Competency {name: row.comp_name})
        SET c += row.comp_props,
            c.last_build_run_id = coalesce($build_run_id, c.last_build_run_id),
            c.last_build_ts = coalesce($build_ts, c.last_build_ts)

        // 3. MERGE 关系并写入长文本与权重
        MERGE (j)-[r:REQUIRES]->(c)
        SET r += row.edge_props
        """

        # ==========================================
        # 3. 分批执行（防止单次事务撑爆 Neo4j 内存）
        # ==========================================
        batch_size = 2000  # 建议每批 2000-5000 条

        with self.driver.session() as session:
            for i in range(0, len(batch_data), batch_size):
                chunk = batch_data[i : i + batch_size]

                # 推荐使用 execute_write 来管理写入事务（比 run 更安全）
                session.execute_write(
                    lambda tx: tx.run(
                        cypher,
                        batch=chunk,
                        build_run_id=build_run_id,
                        build_ts=build_ts,
                    )
                )

                print(
                    f"✅ 已成功灌入 {min(i + batch_size, len(batch_data))} / {len(batch_data)} 条语义边..."
                )

        print("🎉 全部岗位-能力语义图谱构建完成！")

    # 自动校验
    @staticmethod
    def auto_check(check_name: str, condition: bool, error_msg: str):
        """自动校验：不满足直接终止任务"""
        if not condition:
            raise Exception(f"❌ 自动校验失败【{check_name}】：{error_msg}")
        print(f"✅ 自动校验通过【{check_name}】")

    # 人工确认
    @staticmethod
    def manual_confirm(stage_name: str, tips: str) -> bool:
        """人工确认：输入y继续，n终止任务"""
        print(f"\n===== 【关键阶段确认】{stage_name} =====")
        print(f"提示：{tips}")
        res = input("请确认是否继续？(y/n)：").strip().lower()
        return res == "y"

    # 将计算好的IDF权重更新回图数据库
    def update_idf_weights(
        self,
        idf_weights: List[Dict],
        build_run_id: str | None = None,
        build_ts: str | None = None,
    ):
        # 将算法输出的 dict 规范化为“写库契约模型”，避免字段漂移
        idf_payload = [
            GraphRequiresIdfEvidence.model_validate(item).model_dump()
            for item in idf_weights
        ]

        # 批量回写到 Neo4j (将权重固化到 [:REQUIRES] 边上)
        # 注意：这里我们把全局 IDF 存到线上。
        # 如果边上原来有 AI 提取的 local_weight，你可以在 Cypher 里直接相乘！
        update_cypher = """
        UNWIND $batch AS row
        MATCH ()-[r:REQUIRES]->(c:Competency {name: row.comp_name})
        WHERE $build_run_id IS NULL OR r.build_run_id = $build_run_id
        // 1) 固化全局稀缺度证据（Agent 可直接引用：df/覆盖率/idf）
        SET r.idf_weight = row.idf_weight,
            r.df = row.df,
            r.total_jobs = row.total_jobs,
            r.prevalence = row.prevalence,
            r.idf_run_id = coalesce($build_run_id, r.idf_run_id),
            r.idf_ts = coalesce($build_ts, r.idf_ts),
            c.idf_weight = row.idf_weight,
            c.df = row.df,
            c.total_jobs = row.total_jobs,
            c.prevalence = row.prevalence,
            c.idf_run_id = coalesce($build_run_id, c.idf_run_id),
            c.idf_ts = coalesce($build_ts, c.idf_ts)

        // 2) 最终用于 Jaccard 的权重：TF(=local_weight) * IDF
        // local_weight 在离线 payload 阶段写入（Categorical TF），若缺失则按 1.0 兜底。
        SET r.weight = row.idf_weight * coalesce(r.local_weight, 1.0)
        """

        # 批量执行更新
        with self.driver.session() as session:
            # 分批提交防止事务内存炸裂 (这里假设几千个技能，一次性提交也行)
            session.run(
                update_cypher,
                batch=idf_payload,
                build_run_id=build_run_id,
                build_ts=build_ts,
            )

        print("IDF weights successfully written back to Neo4j [:REQUIRES] edges!")

    # 建立岗位间的EVOLVE关系(注入所有参数)，输入是岗位属性列表+各岗位对应的有向加权杰卡德地图，输出的是候选的演化边列表
    def build_evolve_edges(
        self, job_data: Dict[str, Dict], jaccard_map: Dict[Tuple[str, str], float]
    ) -> Dict[Tuple[str, str], Dict]:
        """
        建立岗位间的EVOLVE关系(注入所有参数)，输入是语义图（岗位-能力）列表，输出的是候选的演化边列表
        """
        # 1. 捞取所有Job节点结构化属性
        all_job_ids = list(job_data.keys())

        # 建立 ID 到 矩阵 Index 的映射表，O(1) 寻址
        job_id_to_idx = {job_id: idx for idx, job_id in enumerate(all_job_ids)}

        # ======================================================================
        #  cos_low 加权融合逻辑（语义+结构化）
        #  P0 优化：不再构建 NxN 相似度矩阵；只在候选边上计算。
        # ======================================================================
        text_w = float(settings.graph_build.cos_low.text_weight)
        attr_w = float(settings.graph_build.cos_low.attr_weight)
        w_sum = text_w + attr_w
        if w_sum <= 0:
            text_w, attr_w = 0.7, 0.3
            w_sum = 1.0
        text_w /= w_sum
        attr_w /= w_sum
        print(
            f"🧮 计算综合背景相似度 cos_low（语义{text_w:.2f} + 属性{attr_w:.2f}）..."
        )

        # 1) 拼接软素质文本
        all_texts: list[str] = []
        for jid in all_job_ids:
            txt = " ".join(
                [
                    job_data[jid][f]
                    for f in ["comm_desc", "team_desc", "logic_desc", "learn_desc"]
                ]
            )
            all_texts.append(txt)

        # 2) 批量生成文本 Embedding（离线计算，用完即弃）
        if self.model is None:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = self.model.encode(all_texts, convert_to_numpy=True)
        embeddings = embeddings.astype(np.float32, copy=False)

        # 3) 预归一化：cosine = dot(u, v)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-12)
        emb_norm = embeddings / norms

        # 4) 结构化属性归一化（仅 3 维，后续逐边计算 L1 相似度）
        MAX_DEGREE = 4.0  # 博士
        MAX_EXP = 10.0  # 假设10年为封顶
        MAX_SALARY_RANK = 3.0
        attr_matrix = np.array(
            [
                [
                    job_data[jid]["min_degree"] / MAX_DEGREE,
                    job_data[jid]["min_experience"] / MAX_EXP,
                    job_data[jid]["salary_rank"] / MAX_SALARY_RANK,
                ]
                for jid in all_job_ids
            ],
            dtype=np.float32,
        )

        def _pair_cos_low(idx_a: int, idx_b: int) -> float:
            text_cos = float(np.dot(emb_norm[idx_a], emb_norm[idx_b]))
            # 平均绝对差异 -> 相似度
            attr_sim = 1.0 - float(
                np.mean(np.abs(attr_matrix[idx_a] - attr_matrix[idx_b]))
            )
            return (text_cos * text_w) + (attr_sim * attr_w)

        complete_edges = {}
        print(
            f"⚡ 开始批量处理 {len(jaccard_map)} 个无向候选对（将展开为双向有向候选边）..."
        )

        for (job_a, job_b), jaccard_score in jaccard_map.items():
            if job_a not in job_data or job_b not in job_data:
                continue

            job_a_info = job_data[job_a]
            job_b_info = job_data[job_b]

            # ======================
            # 指标1：最终版 cos_low（O(1) 取值，双向一致）
            # ======================
            idx_a = job_id_to_idx[job_a]
            idx_b = job_id_to_idx[job_b]
            cos_low = round(float(_pair_cos_low(idx_a, idx_b)), 4)

            # ======================
            # 指标2：salary_gain（有向）
            # 说明：相似度本身无向，但“演化/跃迁”应具有方向性；
            # 因此对每个无向候选对，生成 (a->b) 与 (b->a) 两条候选边。
            # ======================
            raw_gain_ab = job_b_info["salary_rank"] - job_a_info["salary_rank"]
            salary_gain_ab = round(max(raw_gain_ab, 0.0) / 2.0, 4)
            raw_gain_ba = job_a_info["salary_rank"] - job_b_info["salary_rank"]
            salary_gain_ba = round(max(raw_gain_ba, 0.0) / 2.0, 4)

            # ======================
            # 指标3：transfer_cost（双向一致）
            # ======================
            exp_diff = abs(job_a_info["min_experience"] - job_b_info["min_experience"])
            degree_diff = abs(job_a_info["min_degree"] - job_b_info["min_degree"])
            major_a = str(job_a_info.get("major") or "").strip()
            major_b = str(job_b_info.get("major") or "").strip()
            major_unknown = {"", "未提及", "未知"}
            if major_a in major_unknown or major_b in major_unknown:
                major_diff = 1
            else:
                major_diff = 0 if major_a == major_b else 1
            transfer_cost = round((exp_diff + degree_diff + major_diff) / 10.0, 4)

            complete_edges[(job_a, job_b)] = {
                "jaccard_high": jaccard_score,
                "cos_low": cos_low,
                "salary_gain": salary_gain_ab,
                "transfer_cost": transfer_cost,
            }
            complete_edges[(job_b, job_a)] = {
                "jaccard_high": jaccard_score,
                "cos_low": cos_low,
                "salary_gain": salary_gain_ba,
                "transfer_cost": transfer_cost,
            }

        # 兜底：如果某些岗位在 Jaccard 阈值下没有任何候选边，会导致聚类出现大量孤立社区，
        # 也会让“跨社区边保留”无从谈起。
        # 这里对 degree=0 的岗位，按 cos_low(语义+属性) 取 TopK 近邻补充候选边。
        from collections import defaultdict

        undirected_degree = defaultdict(int)
        for a, b in jaccard_map.keys():
            undirected_degree[a] += 1
            undirected_degree[b] += 1

        degree_zero_jobs = [
            jid for jid in all_job_ids if undirected_degree.get(jid, 0) == 0
        ]
        if degree_zero_jobs:
            log.warning(
                f"⚠️ Jaccard候选边过稀疏：degree=0 的岗位数={len(degree_zero_jobs)}/{len(all_job_ids)}；"
                "将用 cos_low TopK 近邻补充候选边以降低孤立社区。"
            )

            top_k = int(settings.graph_build.degree_zero_fallback.top_k)
            for jid in degree_zero_jobs:
                i = job_id_to_idx.get(jid)
                if i is None:
                    continue

                # 仅为 degree=0 的点做 TopK 文本近邻检索（避免 NxN 矩阵）
                if emb_norm.shape[0] <= 1:
                    continue

                sims = np.dot(emb_norm, emb_norm[int(i)])
                sims[int(i)] = -1.0

                k = min(top_k, int(sims.shape[0] - 1))
                nbr_idx = np.argpartition(sims, -k)[-k:]
                nbr_idx = nbr_idx[np.argsort(-sims[nbr_idx])]

                for j in nbr_idx:
                    other = all_job_ids[int(j)]
                    if other == jid:
                        continue

                    # 最终 cos_low 仍按“语义+属性”融合（邻居候选按语义检索得到）
                    cos_low = round(float(_pair_cos_low(int(i), int(j))), 4)

                    a_info = job_data[jid]
                    b_info = job_data[other]

                    exp_diff = abs(a_info["min_experience"] - b_info["min_experience"])
                    degree_diff = abs(a_info["min_degree"] - b_info["min_degree"])
                    major_a = str(a_info.get("major") or "").strip()
                    major_b = str(b_info.get("major") or "").strip()
                    major_unknown = {"", "未提及", "未知"}
                    if major_a in major_unknown or major_b in major_unknown:
                        major_diff = 1
                    else:
                        major_diff = 0 if major_a == major_b else 1
                    transfer_cost = round(
                        (exp_diff + degree_diff + major_diff) / 10.0, 4
                    )

                    raw_gain_ab = b_info["salary_rank"] - a_info["salary_rank"]
                    salary_gain_ab = round(max(raw_gain_ab, 0.0) / 2.0, 4)
                    raw_gain_ba = a_info["salary_rank"] - b_info["salary_rank"]
                    salary_gain_ba = round(max(raw_gain_ba, 0.0) / 2.0, 4)

                    # 对兜底边：如果 Jaccard 阈值下未命中，则置为 0.0（仍可作为跨社区“保底可走边”）
                    jaccard_high = 0.0

                    complete_edges.setdefault(
                        (jid, other),
                        {
                            "jaccard_high": jaccard_high,
                            "cos_low": cos_low,
                            "salary_gain": salary_gain_ab,
                            "transfer_cost": transfer_cost,
                        },
                    )
                    complete_edges.setdefault(
                        (other, jid),
                        {
                            "jaccard_high": jaccard_high,
                            "cos_low": cos_low,
                            "salary_gain": salary_gain_ba,
                            "transfer_cost": transfer_cost,
                        },
                    )

        # 校验 + 确认
        self.auto_check("边指标计算", len(complete_edges) > 0, "无有效边")
        tips = f"✅ 所有EVOLVE边指标计算完成\n总有效边数：{len(complete_edges)}"
        if not self.manual_confirm("EVOLVE边指标", tips):
            exit("❌ 任务终止")

        print("🎉 EVOLVE 边全指标计算完成！")
        return complete_edges

    # 完成所有离线图谱构建的主函数，输入是JDAnalysisResult列表，输出是构建好的图数据库
    def build_graph_from_jobs(
        self,
        jobs: list[JDAnalysisResult],
        cleanup_old_evolve_edges: bool = True,
    ):
        build_run_id = uuid.uuid4().hex
        build_started_at = datetime.now().isoformat(timespec="seconds")

        def _abort_run(stage: str, reason: str) -> None:
            ts = datetime.now().isoformat(timespec="seconds")
            self.upsert_build_run(
                run_id=build_run_id,
                status="aborted",
                meta={
                    "run_id": build_run_id,
                    "started_at": build_started_at,
                    "aborted_at": ts,
                    "stage": stage,
                    "reason": reason,
                },
                ts=ts,
            )

        def _fail_run(stage: str, err: Exception) -> None:
            ts = datetime.now().isoformat(timespec="seconds")
            self.upsert_build_run(
                run_id=build_run_id,
                status="failed",
                meta={
                    "run_id": build_run_id,
                    "started_at": build_started_at,
                    "failed_at": ts,
                    "stage": stage,
                    "error": str(err),
                },
                ts=ts,
            )

        self.upsert_build_run(
            run_id=build_run_id,
            status="running",
            meta={
                "run_id": build_run_id,
                "started_at": build_started_at,
                "stage": "save_job_competencies",
            },
            ts=build_started_at,
        )

        try:
            # 1. 将JDAnalysisResult列表转为图数据库批量导入的 payload
            job_competencies = JobCompetency.transform_jobs_to_graph_payload(jobs)

            # 2. 将payload存进图数据库
            self.save_job_competencies(
                job_competencies,
                build_run_id=build_run_id,
                build_ts=build_started_at,
            )
            if not GraphRepository.manual_confirm(
                "原始关系构建完成",
                "是否开始计算Require边的IDF逆文档频率权重?（建议先人工确认样本数据是否正确，再继续后续计算）",
            ):
                _abort_run("save_job_competencies", "manual_confirm_declined")
                return

            # 3. 计算 IDF（按本次 Run 口径）并回写
            idf_data = self.fetch_counts_for_idf(build_run_id=build_run_id)
            idf_weights = GraphAlgorithms.get_idf_weights(idf_data)
            if not idf_weights:
                log.error("IDF权重计算失败,未获取到有效数据!")
                _fail_run("idf", ValueError("idf_weights_empty"))
                return

            self.update_idf_weights(
                idf_weights,
                build_run_id=build_run_id,
                build_ts=build_started_at,
            )
            if not GraphRepository.manual_confirm(
                "IDF权重更新完成",
                "图数据库中的岗位-能力边已经更新了全局IDF权重，是否开始演化边构建？（建议先人工确认IDF权重是否合理，再继续后续计算）",
            ):
                _abort_run("idf", "manual_confirm_declined")
                return

            # 4. 计算加权杰卡德相似度（按本次 Run 口径）
            data = self.fetch_all_for_jaccard(build_run_id=build_run_id)
            jaccard_threshold = float(settings.graph_build.jaccard.threshold)
            jaccard_map = GraphAlgorithms.calculate_weighted_jaccard(
                data,
                threshold=jaccard_threshold,
                blocking_min_jobs=int(settings.graph_build.jaccard.blocking_min_jobs),
                blocking_top_m=int(settings.graph_build.jaccard.blocking_top_m),
            )

            # 准备岗位属性数据（包含软素质文本和结构化属性）用于后续的cos_low计算和聚类分析
            job_data = self.get_all_jobs(build_run_id=build_run_id)
            if not job_data:
                _fail_run("get_all_jobs", ValueError("job_data_empty"))
                return

            # BuildRun 回归基线：保存上一轮社区标签（用于稳定性指标）。
            prev_macro_labels = {
                jid: int(job_data[jid].get("macro_community_id", -1))
                for jid in job_data
            }
            prev_micro_labels = {
                jid: int(job_data[jid].get("micro_community_id", -1))
                for jid in job_data
            }

            is_valid = GraphRepository._validate_input_data(job_data)
            if not is_valid:
                _fail_run("validate_input", ValueError("invalid_input_data"))
                return

            all_job_ids = list(job_data.keys())
            edge_info_map = self.build_evolve_edges(job_data, jaccard_map)

            log.info(
                "候选边口径：无向候选对数(jaccard_map)=%s，有向候选边数(edge_info_map)=%s",
                len(jaccard_map),
                len(edge_info_map),
            )

            clustering_data = {
                "coarse_resolution": float(
                    settings.graph_build.clustering.coarse_resolution
                ),
                "coarse_isolation_threshold": float(
                    settings.graph_build.clustering.coarse_isolation_threshold
                ),
                "fine_resolution": float(
                    settings.graph_build.clustering.fine_resolution
                ),
                "fine_isolation_threshold": float(
                    settings.graph_build.clustering.fine_isolation_threshold
                ),
                "fine_weight_transform_offset": float(
                    settings.graph_build.clustering.fine_weight_transform_offset
                ),
                "fine_weight_transform_power": float(
                    settings.graph_build.clustering.fine_weight_transform_power
                ),
            }
            multi_objective_dict: Dict[str, Literal[0, 1]] = {
                "jaccard_high": 1,
                "cos_low": 1,
                "salary_gain": 1,
                "transfer_cost": 0,
            }

            if not GraphRepository.manual_confirm(
                "数据准备完成",
                "是否进行第一次粗聚类+帕累托前沿筛选？（建议先人工确认候选边的多维度相似度指标是否合理，再继续后续构建）",
            ):
                _abort_run("prepare_data", "manual_confirm_declined")
                return

            # 5. 第一次粗聚类
            coarse_community_map, coarse_cluster_stats = GraphAlgorithms.run_clustering(
                edge_score_map=jaccard_map,
                nodes=all_job_ids,
                resolution=clustering_data["coarse_resolution"],
                isolation_threshold=clustering_data["coarse_isolation_threshold"],
                return_stats=True,
            )

            community_counts = defaultdict(int)
            for job_id in all_job_ids:
                community_id = coarse_community_map.get(job_id, -1)
                community_counts[community_id] += 1

            log.info("第一次粗聚类社区划分结果:")
            for community_id, count in community_counts.items():
                log.info(f"  社区 {community_id}: {count} 个岗位")

            if not GraphRepository.manual_confirm(
                "第一次粗聚类完成",
                "是否继续进行帕累托前沿筛选？（建议先人工确认社区划分结果是否合理，再继续后续构建）",
            ):
                _abort_run("coarse_clustering", "manual_confirm_declined")
                return

            # 6. 多目标 + 局部帕累托剪枝
            keep_fronts = int(settings.graph_build.pareto.keep_fronts)
            cross_community_penalty = float(
                settings.graph_build.pareto.cross_community_penalty
            )
            pareto_skeleton_edges, pareto_stats = (
                GraphAlgorithms.run_pareto_sparsification(
                    community_map=coarse_community_map,
                    multi_objective_dict=multi_objective_dict,
                    edge_info_map=edge_info_map,
                    cross_community_penalty=cross_community_penalty,
                    keep_fronts=keep_fronts,
                    return_stats=True,
                )
            )

            log.info(
                "帕累托输入/输出：无向候选对数(jaccard_map)=%s，有向候选边数(edge_info_map)=%s，保留有向边数(pareto)=%s",
                len(jaccard_map),
                len(edge_info_map),
                len(pareto_skeleton_edges),
            )

            # 6.1 跨社区保边兜底
            existing_cross_pairs: set[tuple[int, int]] = set()
            for (a, b), _m in pareto_skeleton_edges.items():
                ca = coarse_community_map.get(a)
                cb = coarse_community_map.get(b)
                if ca is None or cb is None or ca == cb:
                    continue
                existing_cross_pairs.add(tuple(sorted((int(ca), int(cb)))))

            best_cross_edge_by_pair: dict[
                tuple[int, int], tuple[float, str, str, dict]
            ] = {}
            for (a, b), metrics in edge_info_map.items():
                ca = coarse_community_map.get(a)
                cb = coarse_community_map.get(b)
                if ca is None or cb is None or ca == cb:
                    continue

                pair = tuple(sorted((int(ca), int(cb))))

                w = settings.graph_build.routing.attraction_weights
                base_attraction = (
                    (metrics["jaccard_high"] * float(w.get("jaccard_high", 0.5)))
                    + (metrics["cos_low"] * float(w.get("cos_low", 0.3)))
                    + (metrics["salary_gain"] * float(w.get("salary_gain", 0.2)))
                )
                rank_penalty = keep_fronts * float(
                    settings.graph_build.routing.rank_penalty_per_rank
                )
                cross_penalty = float(settings.graph_build.routing.cross_penalty)
                provisional_cost = round(
                    max(
                        1.0
                        - base_attraction
                        + metrics["transfer_cost"]
                        + rank_penalty
                        + cross_penalty,
                        0.001,
                    ),
                    6,
                )

                cur = best_cross_edge_by_pair.get(pair)
                if cur is None or provisional_cost < cur[0]:
                    best_cross_edge_by_pair[pair] = (provisional_cost, a, b, metrics)

            added_guardrail = 0
            for pair, (_cost, a, b, metrics) in best_cross_edge_by_pair.items():
                if pair in existing_cross_pairs:
                    continue
                if (a, b) in pareto_skeleton_edges:
                    continue

                m = metrics.copy()
                m["pareto_rank"] = keep_fronts
                m["is_cross_community"] = True
                m["cross_community_penalty"] = cross_community_penalty
                m["selected_by"] = "cross_community_guardrail"
                pareto_skeleton_edges[(a, b)] = m
                added_guardrail += 1

            if added_guardrail:
                log.info(f"跨社区保边兜底：新增跨社区边数={added_guardrail}")
                log.info(
                    "跨社区保边后：最终保留有向边数=%s",
                    len(pareto_skeleton_edges),
                )

            # 根据帕累托等级和跨社区标识，修正 Dijkstra 寻路成本
            log.info("正在根据帕累托等级与跨社区标识修正最终寻路权重...")
            for (a, b), m in pareto_skeleton_edges.items():
                w = settings.graph_build.routing.attraction_weights
                base_attraction = (
                    (m["jaccard_high"] * float(w.get("jaccard_high", 0.5)))
                    + (m["cos_low"] * float(w.get("cos_low", 0.3)))
                    + (m["salary_gain"] * float(w.get("salary_gain", 0.2)))
                )

                rank_penalty = m["pareto_rank"] * float(
                    settings.graph_build.routing.rank_penalty_per_rank
                )
                cross_penalty = (
                    float(settings.graph_build.routing.cross_penalty)
                    if m.get("is_cross_community")
                    else 0.0
                )

                m["final_routing_cost"] = round(
                    max(
                        1.0
                        - base_attraction
                        + m["transfer_cost"]
                        + rank_penalty
                        + cross_penalty,
                        0.001,
                    ),
                    4,
                )
                m["base_attraction"] = round(float(base_attraction), 4)
                m["rank_penalty"] = round(float(rank_penalty), 4)
                m["cross_penalty"] = round(float(cross_penalty), 4)
                m["build_run_id"] = build_run_id

            # 关键修复：该确认点必须生效
            if not GraphRepository.manual_confirm(
                "帕累托筛选与权重更新完成",
                "是否开始第二次细聚类？（建议先人工确认社区划分结果是否合理，再继续后续构建）",
            ):
                _abort_run("pareto", "manual_confirm_declined")
                return

            # 7. 第二次细聚类（无向化 + 成本->权重变换）
            fine_undirected_cost: Dict[Tuple[str, str], float] = {}
            for (a, b), v in pareto_skeleton_edges.items():
                pair = tuple(sorted((a, b)))
                cost = float(v.get("final_routing_cost", 0.0) or 0.0)
                prev = fine_undirected_cost.get(pair)
                if prev is None or cost < prev:
                    fine_undirected_cost[pair] = cost

            fine_offset = float(clustering_data["fine_weight_transform_offset"])
            fine_power = float(clustering_data["fine_weight_transform_power"])

            fine_community_map, fine_cluster_stats = GraphAlgorithms.run_clustering(
                edge_score_map=fine_undirected_cost,
                nodes=all_job_ids,
                resolution=clustering_data["fine_resolution"],
                isolation_threshold=clustering_data["fine_isolation_threshold"],
                weight_transform_fn=lambda x: (1.0 / (max(x, 0) + fine_offset))
                ** fine_power,
                return_stats=True,
            )

            # 8. 注入社区标签
            for job_id in all_job_ids:
                job_data[job_id]["macro_community_id"] = coarse_community_map.get(
                    job_id, -1
                )
                job_data[job_id]["micro_community_id"] = fine_community_map.get(
                    job_id, -1
                )

            # 注入跨社区标识 + lineage_json
            for (a, b), m in pareto_skeleton_edges.items():
                m["is_cross_macro"] = (
                    job_data[a]["macro_community_id"]
                    != job_data[b]["macro_community_id"]
                )
                m["is_cross_micro"] = (
                    job_data[a]["micro_community_id"]
                    != job_data[b]["micro_community_id"]
                )

                lineage = {
                    "selected_by": m.get("selected_by", "pareto_sparsification"),
                    "thresholds": {"jaccard_threshold": jaccard_threshold},
                    "pareto": {
                        "rank": m.get("pareto_rank"),
                        "group_size": m.get("pareto_group_size"),
                        "front_size": m.get("pareto_front_size"),
                        "keep_fronts": pareto_stats.get("keep_fronts"),
                        "objectives": {
                            **{
                                k: ("max" if v == 1 else "min")
                                for k, v in multi_objective_dict.items()
                            },
                            "cross_community_penalty": "min",
                        },
                        "is_cross_community": bool(m.get("is_cross_community", False)),
                        "cross_community_penalty": m.get("cross_community_penalty"),
                    },
                    "routing": {
                        "base_attraction": m.get("base_attraction"),
                        "components": {
                            "jaccard_high": float(
                                settings.graph_build.routing.attraction_weights.get(
                                    "jaccard_high", 0.5
                                )
                            ),
                            "cos_low": float(
                                settings.graph_build.routing.attraction_weights.get(
                                    "cos_low", 0.3
                                )
                            ),
                            "salary_gain": float(
                                settings.graph_build.routing.attraction_weights.get(
                                    "salary_gain", 0.2
                                )
                            ),
                        },
                        "rank_penalty": m.get("rank_penalty"),
                        "cross_penalty": m.get("cross_penalty"),
                        "transfer_cost": m.get("transfer_cost"),
                        "final_routing_cost": m.get("final_routing_cost"),
                    },
                    "communities": {
                        "coarse": {
                            "from": job_data[a]["macro_community_id"],
                            "to": job_data[b]["macro_community_id"],
                        },
                        "fine": {
                            "from": job_data[a]["micro_community_id"],
                            "to": job_data[b]["micro_community_id"],
                        },
                    },
                }
                m["lineage_json"] = json.dumps(
                    lineage, ensure_ascii=False, separators=(",", ":")
                )

            # 展示最终社区划分结果
            final_counts = defaultdict(int)
            for job_id in all_job_ids:
                coarse_id = job_data[job_id]["macro_community_id"]
                micro_id = job_data[job_id]["micro_community_id"]
                final_counts[(coarse_id, micro_id)] += 1

            log.info("最终社区划分结果:")
            for (coarse_id, micro_id), count in final_counts.items():
                log.info(f"  社区 {coarse_id}-{micro_id}: {count} 个岗位")

            if not GraphRepository.manual_confirm(
                "演化边筛选完成",
                "是否继续将最终的演化边写入图数据库？（建议先人工确认候选边的多维度相似度指标是否合理，再继续后续构建）",
            ):
                _abort_run("evolve_selection", "manual_confirm_declined")
                return

            # 9. 写入 EVOLVE_TO
            job_evolve_list = []
            for (a, b), metrics in pareto_skeleton_edges.items():
                metrics.pop("is_cross_community", None)
                metrics.pop("cross_community_penalty", None)
                metrics.pop("selected_by", None)
                from_job: GraphNodeJob = GraphNodeJob(**job_data[a])
                to_job: GraphNodeJob = GraphNodeJob(**job_data[b])
                edge: GraphEdgeEvolve = GraphEdgeEvolve(**metrics)
                job_evolve_list.append(
                    JobEvolution(from_job=from_job, to_job=to_job, edge=edge)
                )

            self.save_job_evolve(job_evolve_list)

            deleted_old_edges = 0
            if cleanup_old_evolve_edges:
                deleted_old_edges = self.cleanup_old_evolve_edges(build_run_id)
                log.info(f"版本清理完成，已删除旧 EVOLVE_TO 边数：{deleted_old_edges}")

            build_completed_at = datetime.now().isoformat(timespec="seconds")

            # =====================================================
            # BuildRun 报表指标
            # =====================================================
            report: Dict[str, Any] = {}
            try:
                from collections import defaultdict as _dd
                from sklearn.metrics import (
                    adjusted_rand_score,
                    normalized_mutual_info_score,
                )

                prev_macro = []
                prev_micro = []
                new_macro = []
                new_micro = []
                for jid in all_job_ids:
                    prev_macro.append(int(prev_macro_labels.get(jid, -1)))
                    prev_micro.append(int(prev_micro_labels.get(jid, -1)))
                    new_macro.append(int(job_data[jid].get("macro_community_id", -1)))
                    new_micro.append(int(job_data[jid].get("micro_community_id", -1)))

                stability = {
                    "macro_ari": round(
                        float(adjusted_rand_score(prev_macro, new_macro)), 6
                    ),
                    "macro_nmi": round(
                        float(normalized_mutual_info_score(prev_macro, new_macro)), 6
                    ),
                    "micro_ari": round(
                        float(adjusted_rand_score(prev_micro, new_micro)), 6
                    ),
                    "micro_nmi": round(
                        float(normalized_mutual_info_score(prev_micro, new_micro)), 6
                    ),
                }

                parent = {jid: jid for jid in all_job_ids}

                def _find(x: str) -> str:
                    while parent[x] != x:
                        parent[x] = parent[parent[x]]
                        x = parent[x]
                    return x

                def _union(a0: str, b0: str) -> None:
                    ra, rb = _find(a0), _find(b0)
                    if ra != rb:
                        parent[rb] = ra

                undirected_degree = _dd(int)
                for a0, b0 in pareto_skeleton_edges.keys():
                    if a0 in parent and b0 in parent:
                        _union(a0, b0)
                        undirected_degree[a0] += 1
                        undirected_degree[b0] += 1

                comp_sizes = _dd(int)
                for jid in all_job_ids:
                    comp_sizes[_find(jid)] += 1

                components = len(comp_sizes)
                largest_cc = max(comp_sizes.values()) if comp_sizes else 0
                isolated_nodes = sum(
                    1 for jid in all_job_ids if undirected_degree.get(jid, 0) == 0
                )
                connectivity = {
                    "components": int(components),
                    "largest_component": int(largest_cc),
                    "largest_component_ratio": round(
                        (largest_cc / len(all_job_ids)) if all_job_ids else 0.0, 6
                    ),
                    "isolated_nodes": int(isolated_nodes),
                    "isolated_ratio": round(
                        (isolated_nodes / len(all_job_ids)) if all_job_ids else 0.0, 6
                    ),
                }

                candidate_macro_pairs: set[tuple[int, int]] = set()
                candidate_micro_pairs: set[tuple[int, int]] = set()
                for a0, b0 in edge_info_map.keys():
                    ca0 = int(coarse_community_map.get(a0, -1))
                    cb0 = int(coarse_community_map.get(b0, -1))
                    if ca0 != cb0 and ca0 >= 0 and cb0 >= 0:
                        candidate_macro_pairs.add(tuple(sorted((ca0, cb0))))

                    ca1 = int(fine_community_map.get(a0, -1))
                    cb1 = int(fine_community_map.get(b0, -1))
                    if ca1 != cb1 and ca1 >= 0 and cb1 >= 0:
                        candidate_micro_pairs.add(tuple(sorted((ca1, cb1))))

                kept_macro_pairs: set[tuple[int, int]] = set()
                kept_micro_pairs: set[tuple[int, int]] = set()
                kept_cross_macro_edges = 0
                kept_cross_micro_edges = 0
                for (a0, b0), _m in pareto_skeleton_edges.items():
                    mac_a = int(job_data[a0].get("macro_community_id", -1))
                    mac_b = int(job_data[b0].get("macro_community_id", -1))
                    mic_a = int(job_data[a0].get("micro_community_id", -1))
                    mic_b = int(job_data[b0].get("micro_community_id", -1))

                    if mac_a != mac_b and mac_a >= 0 and mac_b >= 0:
                        kept_macro_pairs.add(tuple(sorted((mac_a, mac_b))))
                        kept_cross_macro_edges += 1
                    if mic_a != mic_b and mic_a >= 0 and mic_b >= 0:
                        kept_micro_pairs.add(tuple(sorted((mic_a, mic_b))))
                        kept_cross_micro_edges += 1

                cross_community = {
                    "candidate_macro_pairs": int(len(candidate_macro_pairs)),
                    "kept_macro_pairs": int(len(kept_macro_pairs)),
                    "macro_pair_coverage": round(
                        (
                            (len(kept_macro_pairs) / len(candidate_macro_pairs))
                            if candidate_macro_pairs
                            else 0.0
                        ),
                        6,
                    ),
                    "candidate_micro_pairs": int(len(candidate_micro_pairs)),
                    "kept_micro_pairs": int(len(kept_micro_pairs)),
                    "micro_pair_coverage": round(
                        (
                            (len(kept_micro_pairs) / len(candidate_micro_pairs))
                            if candidate_micro_pairs
                            else 0.0
                        ),
                        6,
                    ),
                    "kept_cross_macro_edges": int(kept_cross_macro_edges),
                    "kept_cross_micro_edges": int(kept_cross_micro_edges),
                    "kept_edges": int(len(pareto_skeleton_edges)),
                    "kept_cross_macro_edge_ratio": round(
                        (
                            (kept_cross_macro_edges / len(pareto_skeleton_edges))
                            if pareto_skeleton_edges
                            else 0.0
                        ),
                        6,
                    ),
                    "kept_cross_micro_edge_ratio": round(
                        (
                            (kept_cross_micro_edges / len(pareto_skeleton_edges))
                            if pareto_skeleton_edges
                            else 0.0
                        ),
                        6,
                    ),
                }

                adj: Dict[str, list[str]] = _dd(list)
                for a0, b0 in pareto_skeleton_edges.keys():
                    adj[a0].append(b0)

                max_hops = 2
                sample_nodes = all_job_ids
                if len(sample_nodes) > 5000:
                    import random

                    rng = random.Random(42)
                    sample_nodes = rng.sample(
                        sample_nodes, k=min(2000, len(sample_nodes))
                    )

                any_reach = 0
                cross_macro_reach = 0
                cross_micro_reach = 0

                macro_by_job = {
                    jid: int(job_data[jid].get("macro_community_id", -1))
                    for jid in all_job_ids
                }
                micro_by_job = {
                    jid: int(job_data[jid].get("micro_community_id", -1))
                    for jid in all_job_ids
                }

                for s in sample_nodes:
                    s_macro = macro_by_job.get(s, -1)
                    s_micro = micro_by_job.get(s, -1)

                    seen = {s}
                    frontier = [s]
                    found_any = False
                    found_cross_macro = False
                    found_cross_micro = False

                    for _ in range(max_hops):
                        nxt = []
                        for u in frontier:
                            for v in adj.get(u, []):
                                if v in seen:
                                    continue
                                seen.add(v)
                                nxt.append(v)

                                if v != s:
                                    found_any = True
                                v_macro = macro_by_job.get(v, -1)
                                v_micro = micro_by_job.get(v, -1)
                                if v_macro >= 0 and s_macro >= 0 and v_macro != s_macro:
                                    found_cross_macro = True
                                if (
                                    v_macro >= 0
                                    and s_macro >= 0
                                    and v_macro == s_macro
                                    and v_micro >= 0
                                    and s_micro >= 0
                                    and v_micro != s_micro
                                ):
                                    found_cross_micro = True

                                if (
                                    found_any
                                    and found_cross_macro
                                    and found_cross_micro
                                ):
                                    break
                            if found_any and found_cross_macro and found_cross_micro:
                                break
                        frontier = nxt
                        if not frontier:
                            break

                    any_reach += 1 if found_any else 0
                    cross_macro_reach += 1 if found_cross_macro else 0
                    cross_micro_reach += 1 if found_cross_micro else 0

                reachability = {
                    "max_hops": max_hops,
                    "sample_size": int(len(sample_nodes)),
                    "any_reachable_rate": round(
                        (any_reach / len(sample_nodes)) if sample_nodes else 0.0,
                        6,
                    ),
                    "cross_macro_reachable_rate": round(
                        (
                            (cross_macro_reach / len(sample_nodes))
                            if sample_nodes
                            else 0.0
                        ),
                        6,
                    ),
                    "cross_micro_reachable_rate": round(
                        (
                            (cross_micro_reach / len(sample_nodes))
                            if sample_nodes
                            else 0.0
                        ),
                        6,
                    ),
                }

                report = {
                    "stability": stability,
                    "connectivity": connectivity,
                    "cross_community": cross_community,
                    "reachability": reachability,
                }
            except Exception as e:
                report = {"error": f"report_generation_failed: {e}"}

            run_meta = {
                "run_id": build_run_id,
                "started_at": build_started_at,
                "completed_at": build_completed_at,
                "params": {
                    "jaccard_threshold": jaccard_threshold,
                    "coarse_resolution": clustering_data["coarse_resolution"],
                    "coarse_isolation_threshold": clustering_data[
                        "coarse_isolation_threshold"
                    ],
                    "fine_resolution": clustering_data["fine_resolution"],
                    "fine_isolation_threshold": clustering_data[
                        "fine_isolation_threshold"
                    ],
                    "multi_objective": multi_objective_dict,
                },
                "counts": {
                    "jobs": len(all_job_ids),
                    "candidate_edges": len(jaccard_map),
                    "kept_edges": len(pareto_skeleton_edges),
                    "deleted_old_evolve_edges": deleted_old_edges,
                },
                "stats": {
                    "coarse_cluster": coarse_cluster_stats,
                    "fine_cluster": fine_cluster_stats,
                    "pareto": pareto_stats,
                },
                "report": report,
            }
            self.upsert_build_run(
                run_id=build_run_id,
                status="completed",
                meta=run_meta,
                ts=build_completed_at,
            )
        except Exception as e:
            _fail_run("build_graph_from_jobs", e)
            raise

    # 清空图数据库中的所有数据（慎用！）
    def clear_graph(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("图数据库已清空！")

    # 关闭连接
    def close(self):
        self.driver.close()
