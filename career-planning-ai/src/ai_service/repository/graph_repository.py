from neo4j import GraphDatabase
import json
import uuid
from datetime import datetime
import numpy as np
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
    GraphNodeCompetency,
    GraphEdgeRequires,
    JobCompetency,
    GraphEdgeEvolve,
    JobEvolution,
)
from collections import defaultdict
from typing import Literal, Dict, Tuple, List, Any
from sklearn.metrics.pairwise import cosine_similarity, manhattan_distances
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
        cypher = """
        MERGE (r:BuildRun {id: $run_id})
        ON CREATE SET r.created_at = $ts
        SET r.updated_at = $ts,
            r.status = $status,
            r.meta_json = $meta_json,
            r.jaccard_threshold = coalesce($jaccard_threshold, r.jaccard_threshold),
            r.coarse_resolution = coalesce($coarse_resolution, r.coarse_resolution),
            r.fine_resolution = coalesce($fine_resolution, r.fine_resolution)
        """

        with self.driver.session() as session:
            session.run(
                cypher,
                run_id=run_id,
                status=status,
                ts=ts,
                meta_json=meta_json,
                jaccard_threshold=meta.get("params", {}).get("jaccard_threshold"),
                coarse_resolution=meta.get("params", {}).get("coarse_resolution"),
                fine_resolution=meta.get("params", {}).get("fine_resolution"),
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
    def fetch_counts_for_idf(self):
        with self.driver.session() as session:
            # 只需要 job_id 和能力名即可算出全局分布
            result = session.run(
                """
                MATCH (j:Job)-[:REQUIRES]->(c:Competency)
                RETURN j.id AS job_id, c.name AS comp_name
            """
            )
            return result.data()

    # 从图数据库中取出所有岗位和能力的权重关系，只提取加权杰卡德相似度需要的字段
    def fetch_all_for_jaccard(self):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (j:Job)-[r:REQUIRES]->(c:Competency)
                RETURN j.id AS job_id, c.name AS comp_name, r.weight AS weight
            """
            )
            return result.data()

    # 捞取所有Job节点结构化属性（缺省值保护）
    def get_all_jobs(self) -> Dict[str, Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                    MATCH (j:Job)
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
            """
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
        SET e.jaccard_high = data.edge_props.jaccard_high,
            e.cos_low = data.edge_props.cos_low,
            e.salary_gain = data.edge_props.salary_gain,
            e.transfer_cost = data.edge_props.transfer_cost,
            e.final_routing_cost = data.edge_props.final_routing_cost,
            e.pareto_rank = coalesce(data.edge_props.pareto_rank, 0),
            e.is_cross_macro = coalesce(data.edge_props.is_cross_macro, false),
            e.is_cross_micro = coalesce(data.edge_props.is_cross_micro, false),
            e.build_run_id = data.edge_props.build_run_id,
            e.lineage_json = data.edge_props.lineage_json,
            e.base_attraction = data.edge_props.base_attraction,
            e.rank_penalty = data.edge_props.rank_penalty,
            e.cross_penalty = data.edge_props.cross_penalty,
            e.pareto_group_size = coalesce(data.edge_props.pareto_group_size, 0),
            e.pareto_front_size = coalesce(data.edge_props.pareto_front_size, 0)
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
            job_props = jc.from_job.model_dump(exclude={"id"}, exclude_none=True)
            if build_run_id:
                job_props["last_build_run_id"] = build_run_id
            if build_ts:
                job_props["last_build_ts"] = build_ts

            batch_data.append(
                {
                    "job_id": jc.from_job.id,
                    # 使用 model_dump() 兼容 Pydantic V2，剔除 id 避免重复赋值
                    "job_props": job_props,
                    "comp_name": jc.to_competency.name,
                    "comp_category": jc.to_competency.category,
                    "weight": jc.edge.weight,
                    "min_score": jc.edge.min_score,
                    "context": jc.edge.context,
                    "build_run_id": build_run_id,
                    "build_ts": build_ts,
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
        SET c.category = row.comp_category,
            c.last_build_run_id = coalesce(row.build_run_id, c.last_build_run_id),
            c.last_build_ts = coalesce(row.build_ts, c.last_build_ts)

        // 3. MERGE 关系并写入长文本与权重
        MERGE (j)-[r:REQUIRES]->(c)
        SET r.weight = row.weight,
            r.min_score = row.min_score,
            r.context = row.context,
            r.build_run_id = row.build_run_id,
            r.build_ts = row.build_ts
        """

        # ==========================================
        # 3. 分批执行（防止单次事务撑爆 Neo4j 内存）
        # ==========================================
        batch_size = 2000  # 建议每批 2000-5000 条

        with self.driver.session() as session:
            for i in range(0, len(batch_data), batch_size):
                chunk = batch_data[i : i + batch_size]

                # 推荐使用 execute_write 来管理写入事务（比 run 更安全）
                session.execute_write(lambda tx: tx.run(cypher, batch=chunk))

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
        # 批量回写到 Neo4j (将权重固化到 [:REQUIRES] 边上)
        # 注意：这里我们把全局 IDF 存到线上。
        # 如果边上原来有 AI 提取的 local_weight，你可以在 Cypher 里直接相乘！
        update_cypher = """
        UNWIND $batch AS row
        MATCH ()-[r:REQUIRES]->(c:Competency {name: row.comp_name})
        // 1) 尽量保留“局部权重”的血缘：只有当原 weight 非0 且 local_weight 为空时才缓存
        SET r.local_weight = coalesce(
                r.local_weight,
                CASE WHEN r.weight IS NOT NULL AND r.weight <> 0 THEN r.weight END
            )

        // 2) 固化全局稀缺度证据（Agent 可直接引用：df/覆盖率/idf）
        SET r.idf_weight = row.idf_weight,
            r.df = row.df,
            r.total_jobs = row.total_jobs,
            r.prevalence = row.prevalence,
            r.idf_run_id = $build_run_id,
            r.idf_ts = $build_ts,
            c.idf_weight = row.idf_weight,
            c.df = row.df,
            c.total_jobs = row.total_jobs,
            c.prevalence = row.prevalence,
            c.idf_run_id = $build_run_id,
            c.idf_ts = $build_ts

        // 3) 兼容现有计算：当前用于 Jaccard 的 weight 仍采用全局 IDF
        SET r.weight = row.idf_weight
        """

        # 批量执行更新
        with self.driver.session() as session:
            # 分批提交防止事务内存炸裂 (这里假设几千个技能，一次性提交也行)
            session.run(
                update_cypher,
                batch=idf_weights,
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
        # ======================================================================
        print("🧮 计算综合背景相似度 cos_low（语义70% + 属性30%）...")

        # 1. 拼接软素质文本
        all_texts = []
        for jid in all_job_ids:
            txt = " ".join(
                [
                    job_data[jid][f]
                    for f in ["comm_desc", "team_desc", "logic_desc", "learn_desc"]
                ]
            )
            all_texts.append(txt)

        # 2. 批量生成文本Embedding（离线计算，用完即弃）
        if self.model is None:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = self.model.encode(all_texts, convert_to_numpy=True)

        # 3. 结构化属性归一化矩阵
        MAX_DEGREE = 4.0  # 博士
        MAX_EXP = 10.0  # 假设10年为封顶
        MAX_SALARY_RANK = 3.0

        # 3. 结构化属性归一化矩阵
        attr_matrix = np.array(
            [
                [
                    job_data[jid]["min_degree"] / MAX_DEGREE,
                    job_data[jid]["min_experience"] / MAX_EXP,
                    job_data[jid]["salary_rank"] / MAX_SALARY_RANK,
                ]
                for jid in all_job_ids
            ]
        )

        # 4. 计算双相似度矩阵
        # 提示：embeddings 加上微小值是为了防止某些极端全0向量导致除零错误
        text_sim_matrix = cosine_similarity(embeddings)
        attr_dist_matrix = manhattan_distances(attr_matrix)

        # Manhattan 距离最大值是维度数 (这里是3)，所以除以 shape[1] 得到 0-1 之间的平均差异
        attr_sim_matrix = 1.0 - (attr_dist_matrix / attr_matrix.shape[1])

        # 5. 加权融合 = 最终 cos_low 矩阵
        final_context_sim_matrix = (text_sim_matrix * 0.7) + (attr_sim_matrix * 0.3)

        # 【清理不再需要的中间大矩阵】
        del text_sim_matrix, attr_dist_matrix, attr_sim_matrix, embeddings, attr_matrix

        complete_edges = {}
        print(f"⚡ 开始批量处理 {len(jaccard_map)} 条候选边...")

        for (job_a, job_b), jaccard_score in jaccard_map.items():
            if job_a not in job_data or job_b not in job_data:
                continue

            job_a_info = job_data[job_a]
            job_b_info = job_data[job_b]

            # ======================
            # 指标1：最终版 cos_low（O(1) 取值）
            # ======================
            idx_a = job_id_to_idx[job_a]
            idx_b = job_id_to_idx[job_b]
            cos_low = round(float(final_context_sim_matrix[idx_a, idx_b]), 4)

            # ======================
            # 指标2：salary_gain（不变）
            # ======================
            raw_gain = job_b_info["salary_rank"] - job_a_info["salary_rank"]
            salary_gain = round(max(raw_gain, 0.0) / 2.0, 4)

            # ======================
            # 指标3：transfer_cost（不变）
            # ======================
            exp_diff = abs(job_a_info["min_experience"] - job_b_info["min_experience"])
            degree_diff = abs(job_a_info["min_degree"] - job_b_info["min_degree"])
            major_diff = 0 if job_a_info["major"] == job_b_info["major"] else 1
            transfer_cost = round((exp_diff + degree_diff + major_diff) / 10.0, 4)

            complete_edges[(job_a, job_b)] = {
                "jaccard_high": jaccard_score,
                "cos_low": cos_low,
                "salary_gain": salary_gain,
                "transfer_cost": transfer_cost,
            }

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
            return

        # 3. 从图数据库中取出已固化的岗位-能力关系，计算IDF权重，并更新回图数据库
        idf_data = self.fetch_counts_for_idf()

        idf_weights = GraphAlgorithms.get_idf_weights(idf_data)
        if not idf_weights:
            log.error("IDF权重计算失败,未获取到有效数据!")
            return
        self.update_idf_weights(
            idf_weights, build_run_id=build_run_id, build_ts=build_started_at
        )
        if not GraphRepository.manual_confirm(
            "IDF权重更新完成",
            "图数据库中的岗位-能力边已经更新了全局IDF权重，是否开始演化边构建？（建议先人工确认IDF权重是否合理，再继续后续计算）",
        ):
            return

        # 4. 计算加权杰卡德相似度，建立岗位间的候选EVOLVE关系(注入所有参数)
        data = self.fetch_all_for_jaccard()
        jaccard_threshold = 0.1
        jaccard_map = GraphAlgorithms.calculate_weighted_jaccard(
            data, threshold=jaccard_threshold
        )

        # 准备岗位属性数据（包含软素质文本和结构化属性）用于后续的cos_low计算和聚类分析
        job_data = self.get_all_jobs()
        is_valid = GraphRepository._validate_input_data(job_data)
        if not is_valid:
            log.error(
                "输入数据校验失败，存在非数字类型的关键字段！请检查日志中的错误详情并修正数据后重试。"
            )
            return

        all_job_ids = list(job_data.keys())
        edge_info_map = self.build_evolve_edges(job_data, jaccard_map)

        clustering_data = {
            "coarse_resolution": 0.1,
            "coarse_isolation_threshold": 0.1,
            "fine_resolution": 1.0,
            "fine_isolation_threshold": 0.05,
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
            return

        # 5.用加权杰卡德跑第一次粗聚类
        coarse_community_map, coarse_cluster_stats = GraphAlgorithms.run_clustering(
            edge_score_map=jaccard_map,
            nodes=all_job_ids,
            resolution=clustering_data["coarse_resolution"],
            isolation_threshold=clustering_data["coarse_isolation_threshold"],
            return_stats=True,
        )

        # 展示第一次粗聚类的社区划分结果
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
            return

        # 6.进行多目标计算+局部帕累托剪枝，得到第一、二层前沿边
        pareto_skeleton_edges, pareto_stats = GraphAlgorithms.run_pareto_sparsification(
            community_map=coarse_community_map,
            multi_objective_dict=multi_objective_dict,
            edge_info_map=edge_info_map,
            keep_fronts=2,
            return_stats=True,
        )

        # 展示帕累托筛选后的边数和之前的对比
        log.info(f"原始候选边数: {len(jaccard_map)}")
        log.info(f"帕累托筛选后的边数: {len(pareto_skeleton_edges)}")

        # 根据帕累托等级和跨社区标识，重新修正 Dijkstra 寻路成本
        log.info("正在根据帕累托等级与跨社区标识修正最终寻路权重...")
        for (a, b), m in pareto_skeleton_edges.items():
            # 基础吸引力 (Jaccard + Cosine + Salary)
            base_attraction = (
                (m["jaccard_high"] * 0.5)
                + (m["cos_low"] * 0.3)
                + (m["salary_gain"] * 0.2)
            )

            # 1. 增加等级惩罚：第二前沿（rank 1）比第一前沿（rank 0）更难走
            rank_penalty = m["pareto_rank"] * 0.15

            # 2. 增加跨界惩罚：物理上的跨行业难度
            cross_penalty = 0.5 if m["is_cross_community"] else 0.0

            # 3. 最终坍缩：成本 = (1 - 吸引力) + 各种惩罚
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

            # 固化关键中间量（用于在线解释“这条边为什么被认为更优/更难走”）
            m["base_attraction"] = round(float(base_attraction), 4)
            m["rank_penalty"] = round(float(rank_penalty), 4)
            m["cross_penalty"] = round(float(cross_penalty), 4)
            m["build_run_id"] = build_run_id

        GraphRepository.manual_confirm(
            "帕累托筛选与权重更新完成",
            "是否开始第二次细聚类？（建议先人工确认社区划分结果是否合理，再继续后续构建）",
        )
        # 7.用final_routing_cost和帕累托剪枝后的边跑第二次细聚类（仅在第一层前沿边上跑)
        fine_community_map, fine_cluster_stats = GraphAlgorithms.run_clustering(
            edge_score_map={
                (a, b): v["final_routing_cost"]
                for (a, b), v in pareto_skeleton_edges.items()
            },
            nodes=all_job_ids,
            resolution=clustering_data["fine_resolution"],
            isolation_threshold=clustering_data["fine_isolation_threshold"],
            weight_transform_fn=lambda x: (1.0 / (max(x, 0) + 0.1)) ** 2,
            return_stats=True,
        )

        # 8. 将最终的社区划分结果注入到岗位属性中（字段以 GraphNodeJob 为准）
        for job_id in all_job_ids:
            job_data[job_id]["macro_community_id"] = coarse_community_map.get(
                job_id, -1
            )
            job_data[job_id]["micro_community_id"] = fine_community_map.get(job_id, -1)

        # 给所有evolve边注入跨社区标识（第一层粗社区，第二层细社区）
        for (a, b), m in pareto_skeleton_edges.items():
            m["is_cross_macro"] = (
                job_data[a]["macro_community_id"] != job_data[b]["macro_community_id"]
            )
            m["is_cross_micro"] = (
                job_data[a]["micro_community_id"] != job_data[b]["micro_community_id"]
            )

            # 生成“被选中理由”的决策快照（不可嵌套结构用 JSON 存在关系属性上）
            lineage = {
                "selected_by": "pareto_sparsification",
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
                        "jaccard_high": 0.5,
                        "cos_low": 0.3,
                        "salary_gain": 0.2,
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

        # 展示最终的社区划分结果
        community_counts = defaultdict(int)
        for job_id in all_job_ids:
            coarse_id = job_data[job_id]["macro_community_id"]
            micro_id = job_data[job_id]["micro_community_id"]
            community_counts[(coarse_id, micro_id)] += 1

        log.info("最终社区划分结果:")
        for (coarse_id, micro_id), count in community_counts.items():
            log.info(f"  社区 {coarse_id}-{micro_id}: {count} 个岗位")

        if not GraphRepository.manual_confirm(
            "演化边筛选完成",
            "是否继续将最终的演化边写入图数据库？（建议先人工确认候选边的多维度相似度指标是否合理，再继续后续构建）",
        ):
            return

        # 9. 将最终的数据包装成给规范的JobEvolution写回图数据库
        job_evolve_list = []
        for (a, b), metrics in pareto_skeleton_edges.items():
            # 去掉 is_cross_community 字段, 兼容GraphEdgeEvolve类
            metrics.pop("is_cross_community", None)
            metrics.pop("cross_community_penalty", None)
            from_job: GraphNodeJob = GraphNodeJob(**job_data[a])
            to_job: GraphNodeJob = GraphNodeJob(**job_data[b])
            edge: GraphEdgeEvolve = GraphEdgeEvolve(**metrics)
            job_evolve = JobEvolution(from_job=from_job, to_job=to_job, edge=edge)
            job_evolve_list.append(job_evolve)
        self.save_job_evolve(job_evolve_list)

        deleted_old_edges = 0
        if cleanup_old_evolve_edges:
            deleted_old_edges = self.cleanup_old_evolve_edges(build_run_id)
            log.info(f"版本清理完成，已删除旧 EVOLVE_TO 边数：{deleted_old_edges}")

        build_completed_at = datetime.now().isoformat(timespec="seconds")

        # 将本次离线建图的全局运行快照固化到图上（Run级别，避免每条边重复存大对象）
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
                "fine_isolation_threshold": clustering_data["fine_isolation_threshold"],
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
        }
        self.upsert_build_run(
            run_id=build_run_id,
            status="completed",
            meta=run_meta,
            ts=build_completed_at,
        )

    # 清空图数据库中的所有数据（慎用！）
    def clear_graph(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("图数据库已清空！")

    # 关闭连接
    def close(self):
        self.driver.close()
