import logging
from typing import List, Dict, Optional, Any
from neo4j import GraphDatabase, Query

from ai_service.models.graph import GraphNodeJob

log = logging.getLogger(__name__)


class CareerRepository:
    def __init__(self, url: str, username: str, password: str):
        """初始化 Neo4j 驱动"""
        self.driver = GraphDatabase.driver(url, auth=(username, password))
        log.info("✅ CareerRepository 数据库连接已初始化。")

    def close(self):
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
            log.info("🔒 CareerRepository 数据库连接已关闭。")

    def get_build_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """获取一次离线建图 Run 的快照（供在线解释阈值/统计口径）。"""

        query = """
        MATCH (r:BuildRun {id: $run_id})
        RETURN r.id AS run_id,
               r.status AS status,
               r.meta_json AS meta_json
        """

        try:
            with self.driver.session() as session:
                record = session.run(query, run_id=run_id).single()
                return dict(record) if record else None
        except Exception as e:
            log.error(f"❌ 获取BuildRun失败: {e}")
            return None

    def get_job_brief(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取岗位基础信息（用于 bundle 起点展示与社区约束）。"""

        query = """
        MATCH (j:Job {id: $job_id})
        RETURN j.id AS job_id,
               j.job_name AS job_name,
               j.macro_community_id AS macro_cid,
               j.micro_community_id AS micro_cid
        """

        try:
            with self.driver.session() as session:
                record = session.run(query, job_id=job_id).single()
                return dict(record) if record else None
        except Exception as e:
            log.error(f"❌ 获取岗位简要信息失败: {e}")
            return None

    def get_required_skill_names(self, job_id: str) -> List[str]:
        """返回某岗位的 REQUIRES 技能集合（Competency.name 列表）。"""

        query = """
        MATCH (:Job {id: $job_id})-[:REQUIRES]->(c:Competency)
        RETURN collect(DISTINCT c.name) AS skills
        """

        try:
            with self.driver.session() as session:
                record = session.run(query, job_id=job_id).single()
                if not record:
                    return []
                return list(record["skills"] or [])
        except Exception as e:
            log.error(f"❌ 获取岗位技能集合失败: {e}")
            return []

    def find_vertical_promotion_paths(
        self,
        start_id: str,
        max_hops: int = 5,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """垂直晋升：同 micro 社区；每跳不跨 micro/macro 且 salary_gain > 0。"""

        # Neo4j 不支持在变长关系模式中使用参数（例如 *1..$max_hops）。
        # 这里将 max_hops 内联为字面量，且 max_hops 仅由服务端常量传入，避免注入风险。
        max_hops = int(max_hops)
        if max_hops < 1:
            return []
        if max_hops > 10:
            max_hops = 10

        query = """
        MATCH (start:Job {id: $start_id})
        MATCH p=(start)-[:EVOLVE_TO*1..__MAX_HOPS__]->(target:Job)
        WHERE target.micro_community_id = start.micro_community_id
                    AND all(
                        r IN relationships(p)
                        WHERE coalesce(r.is_cross_micro, false) = false
                    )
                    AND all(
                        r IN relationships(p)
                        WHERE coalesce(r.is_cross_macro, false) = false
                    )
                    AND all(
                        r IN relationships(p)
                        WHERE coalesce(r.salary_gain, 0.0) > 0.0
                    )
        WITH target, p,
                         reduce(
                                cost=0.0,
                                r IN relationships(p) |
                                cost + coalesce(r.final_routing_cost, 0.0)
                         ) AS total_cost
        ORDER BY total_cost ASC
        WITH target, collect({p: p, cost: total_cost})[0] AS best
        WITH best.p AS p, best.cost AS total_cost
        RETURN [n in nodes(p) | {
                id: n.id,
                job_name: n.job_name,
                macro_cid: n.macro_community_id,
                micro_cid: n.micro_community_id
            }] AS path_sequence,
            [r in relationships(p) | {
                from_id: startNode(r).id,
                to_id: endNode(r).id,
                final_routing_cost: r.final_routing_cost,
                transfer_cost: r.transfer_cost,
                salary_gain: r.salary_gain,
                jaccard_high: r.jaccard_high,
                cos_low: r.cos_low,
                pareto_rank: r.pareto_rank,
                pareto_group_size: r.pareto_group_size,
                pareto_front_size: r.pareto_front_size,
                is_cross_macro: r.is_cross_macro,
                is_cross_micro: r.is_cross_micro,
                base_attraction: r.base_attraction,
                rank_penalty: r.rank_penalty,
                cross_penalty: r.cross_penalty,
                build_run_id: r.build_run_id,
                lineage_json: r.lineage_json
            }] AS edge_metrics,
            total_cost AS total_cost
        LIMIT $limit
        """.replace(
            "__MAX_HOPS__", str(max_hops)
        )

        try:
            with self.driver.session() as session:
                result = session.run(
                    Query(query),
                    start_id=start_id,
                    limit=limit,
                )
                rows = []
                for record in result:
                    total_cost = float(record["total_cost"] or 0.0)
                    rows.append(
                        {
                            "path_sequence": record["path_sequence"],
                            "edge_metrics": record["edge_metrics"],
                            "total_cost": round(total_cost, 4),
                        }
                    )
                return rows
        except Exception as e:
            log.error(f"❌ 垂直晋升路径查询失败: {e}")
            return []

    def find_lateral_transfer_paths(
        self,
        start_id: str,
        max_hops: int = 2,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """换岗：同 macro 不同 micro；每跳跨 micro 且不跨 macro。"""

        max_hops = int(max_hops)
        if max_hops < 1:
            return []
        if max_hops > 10:
            max_hops = 10

        query = """
        MATCH (start:Job {id: $start_id})
        MATCH p=(start)-[:EVOLVE_TO*1..__MAX_HOPS__]->(target:Job)
        WHERE target.macro_community_id = start.macro_community_id
          AND target.micro_community_id <> start.micro_community_id
                    AND all(
                        r IN relationships(p)
                        WHERE coalesce(r.is_cross_micro, false) = true
                    )
                    AND all(
                        r IN relationships(p)
                        WHERE coalesce(r.is_cross_macro, false) = false
                    )
        WITH target, p,
                         reduce(
                                cost=0.0,
                                r IN relationships(p) |
                                cost + coalesce(r.final_routing_cost, 0.0)
                         ) AS total_cost
        ORDER BY total_cost ASC
        WITH target, collect({p: p, cost: total_cost})[0] AS best
        WITH best.p AS p, best.cost AS total_cost
        RETURN [n in nodes(p) | {
                id: n.id,
                job_name: n.job_name,
                macro_cid: n.macro_community_id,
                micro_cid: n.micro_community_id
            }] AS path_sequence,
            [r in relationships(p) | {
                from_id: startNode(r).id,
                to_id: endNode(r).id,
                final_routing_cost: r.final_routing_cost,
                transfer_cost: r.transfer_cost,
                salary_gain: r.salary_gain,
                jaccard_high: r.jaccard_high,
                cos_low: r.cos_low,
                pareto_rank: r.pareto_rank,
                pareto_group_size: r.pareto_group_size,
                pareto_front_size: r.pareto_front_size,
                is_cross_macro: r.is_cross_macro,
                is_cross_micro: r.is_cross_micro,
                base_attraction: r.base_attraction,
                rank_penalty: r.rank_penalty,
                cross_penalty: r.cross_penalty,
                build_run_id: r.build_run_id,
                lineage_json: r.lineage_json
            }] AS edge_metrics,
            total_cost AS total_cost
        LIMIT $limit
        """.replace(
            "__MAX_HOPS__", str(max_hops)
        )

        try:
            with self.driver.session() as session:
                result = session.run(
                    Query(query),
                    start_id=start_id,
                    limit=limit,
                )
                rows = []
                for record in result:
                    total_cost = float(record["total_cost"] or 0.0)
                    rows.append(
                        {
                            "path_sequence": record["path_sequence"],
                            "edge_metrics": record["edge_metrics"],
                            "total_cost": round(total_cost, 4),
                        }
                    )
                return rows
        except Exception as e:
            log.error(f"❌ 换岗路径查询失败: {e}")
            return []

    def find_cross_industry_paths(
        self,
        start_id: str,
        max_hops: int = 2,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """跨界跃迁：目标宏观社区不同；路径中至少一跳 is_cross_macro = true。"""

        max_hops = int(max_hops)
        if max_hops < 1:
            return []

    def find_goal_planning_paths(
        self,
        start_id: str,
        target_id: str,
        max_hops: int = 10,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """目标路径规划：给定起点与目标岗位，枚举多条候选路径并按总成本升序返回。

        说明：
        - 关系仅沿 EVOLVE_TO 方向。
        - 路径成本口径：sum(relationships(p).final_routing_cost)。
        - 为避免循环路径，约束为 simple path（nodes(p) 不重复）。
        """

        max_hops = int(max_hops)
        if max_hops < 1:
            return []
        if max_hops > 15:
            max_hops = 15

        limit = int(limit)
        if limit < 1:
            return []
        if limit > 50:
            limit = 50

        query = """
        MATCH (start:Job {id: $start_id}), (target:Job {id: $target_id})
        MATCH p=(start)-[:EVOLVE_TO*1..__MAX_HOPS__]->(target)
        WHERE all(n IN nodes(p) WHERE single(m IN nodes(p) WHERE m = n))
        WITH p,
             reduce(
                cost=0.0,
                r IN relationships(p) |
                cost + coalesce(r.final_routing_cost, 0.0)
             ) AS total_cost
        ORDER BY total_cost ASC
        RETURN [n in nodes(p) | {
                id: n.id,
                job_name: n.job_name,
                macro_cid: n.macro_community_id,
                micro_cid: n.micro_community_id
            }] AS path_sequence,
            [r in relationships(p) | {
                from_id: startNode(r).id,
                to_id: endNode(r).id,
                final_routing_cost: r.final_routing_cost,
                transfer_cost: r.transfer_cost,
                salary_gain: r.salary_gain,
                jaccard_high: r.jaccard_high,
                cos_low: r.cos_low,
                pareto_rank: r.pareto_rank,
                pareto_group_size: r.pareto_group_size,
                pareto_front_size: r.pareto_front_size,
                is_cross_macro: r.is_cross_macro,
                is_cross_micro: r.is_cross_micro,
                base_attraction: r.base_attraction,
                rank_penalty: r.rank_penalty,
                cross_penalty: r.cross_penalty,
                build_run_id: r.build_run_id,
                lineage_json: r.lineage_json
            }] AS edge_metrics,
            total_cost AS total_cost
        LIMIT $limit
        """.replace(
            "__MAX_HOPS__", str(max_hops)
        )

        try:
            with self.driver.session() as session:
                result = session.run(
                    Query(query),
                    start_id=start_id,
                    target_id=target_id,
                    limit=limit,
                )
                rows = []
                for record in result:
                    total_cost = float(record["total_cost"] or 0.0)
                    rows.append(
                        {
                            "path_sequence": record["path_sequence"],
                            "edge_metrics": record["edge_metrics"],
                            "total_cost": round(total_cost, 4),
                        }
                    )
                return rows
        except Exception as e:
            log.error(f"❌ 目标路径规划查询失败: {e}")
            return []
        if max_hops > 10:
            max_hops = 10

        query = """
        MATCH (start:Job {id: $start_id})
        MATCH p=(start)-[:EVOLVE_TO*1..__MAX_HOPS__]->(target:Job)
        WHERE target.macro_community_id <> start.macro_community_id
                    AND any(
                        r IN relationships(p)
                        WHERE coalesce(r.is_cross_macro, false) = true
                    )
        WITH target, p,
                         reduce(
                                cost=0.0,
                                r IN relationships(p) |
                                cost + coalesce(r.final_routing_cost, 0.0)
                         ) AS total_cost
        ORDER BY total_cost ASC
        WITH target, collect({p: p, cost: total_cost})[0] AS best
        WITH best.p AS p, best.cost AS total_cost
        RETURN [n in nodes(p) | {
                id: n.id,
                job_name: n.job_name,
                macro_cid: n.macro_community_id,
                micro_cid: n.micro_community_id
            }] AS path_sequence,
            [r in relationships(p) | {
                from_id: startNode(r).id,
                to_id: endNode(r).id,
                final_routing_cost: r.final_routing_cost,
                transfer_cost: r.transfer_cost,
                salary_gain: r.salary_gain,
                jaccard_high: r.jaccard_high,
                cos_low: r.cos_low,
                pareto_rank: r.pareto_rank,
                pareto_group_size: r.pareto_group_size,
                pareto_front_size: r.pareto_front_size,
                is_cross_macro: r.is_cross_macro,
                is_cross_micro: r.is_cross_micro,
                base_attraction: r.base_attraction,
                rank_penalty: r.rank_penalty,
                cross_penalty: r.cross_penalty,
                build_run_id: r.build_run_id,
                lineage_json: r.lineage_json
            }] AS edge_metrics,
            total_cost AS total_cost
        LIMIT $limit
        """.replace(
            "__MAX_HOPS__", str(max_hops)
        )

        try:
            with self.driver.session() as session:
                result = session.run(
                    Query(query),
                    start_id=start_id,
                    limit=limit,
                )
                rows = []
                for record in result:
                    total_cost = float(record["total_cost"] or 0.0)
                    rows.append(
                        {
                            "path_sequence": record["path_sequence"],
                            "edge_metrics": record["edge_metrics"],
                            "total_cost": round(total_cost, 4),
                        }
                    )
                return rows
        except Exception as e:
            log.error(f"❌ 跨界跃迁路径查询失败: {e}")
            return []

    # ==========================================
    # 1. 逻辑位面查询：硬核路由寻找
    # ==========================================
    def get_shortest_path(
        self, start_id: str, target_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        利用 APOC Dijkstra 算法，在 [:EVOLVE_TO] 演化网上寻找综合阻力最小的路径。
        """
        # 注意: 'EVOLVE_TO>' 带有箭头，强制算法只能顺着演化方向（晋升/平调）走，不能逆行退级！
        query = """
        MATCH (start:Job {id: $start_id}), (target:Job {id: $target_id})
        CALL apoc.algo.dijkstra(
            start,
            target,
            'EVOLVE_TO>',
            'final_routing_cost'
        )
        YIELD path, weight
        RETURN[n in nodes(path) | {
            id: n.id,
            job_name: n.job_name,
                macro_cid: n.macro_community_id,
                micro_cid: n.micro_community_id
            }] AS path_sequence,
            [r in relationships(path) | {
                from_id: startNode(r).id,
                to_id: endNode(r).id,
                final_routing_cost: r.final_routing_cost,
                transfer_cost: r.transfer_cost,
                salary_gain: r.salary_gain,
                jaccard_high: r.jaccard_high,
                cos_low: r.cos_low,
                pareto_rank: r.pareto_rank,
                pareto_group_size: r.pareto_group_size,
                pareto_front_size: r.pareto_front_size,
                is_cross_macro: r.is_cross_macro,
                is_cross_micro: r.is_cross_micro,
                base_attraction: r.base_attraction,
                rank_penalty: r.rank_penalty,
                cross_penalty: r.cross_penalty,
                build_run_id: r.build_run_id,
                lineage_json: r.lineage_json
            }] AS edge_metrics,
            weight AS total_cost
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    start_id=start_id,
                    target_id=target_id,
                )
                record = result.single()

                if record:
                    return {
                        "path_sequence": record["path_sequence"],
                        "edge_metrics": record[
                            "edge_metrics"
                        ],  # 包含了每一步跃迁的详情
                        "total_cost": round(record["total_cost"], 4),
                    }
                else:
                    log.warning(f"⚠️ 未找到从 {start_id} 到 {target_id} 的有效路径。")
                    return None
        except Exception as e:
            log.error(f"❌ 寻路查询失败: {e}")
            return None

    # ==========================================
    # 2. 语义位面查询：增量缺口分析
    # ==========================================
    def get_skill_gaps(
        self, target_job_id: str, student_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """
        查询目标岗位要求的硬技能，并通过直接传入 student_skills 列表进行集合减法。
        （完美契合“不存学生节点”的无状态架构）
        """
        query = """
        MATCH (j:Job {id: $target_job_id})-[r:REQUIRES]->(c:Competency)
        // 图数据库原生的差集运算：找出岗位需要，但我没有的技能
        WHERE NOT c.name IN $student_skills
        RETURN
            c.name AS competency_name,
            c.category AS category,
            r.min_score AS target_score,
            r.weight AS importance_weight,
            r.local_weight AS local_weight,
            r.idf_weight AS idf_weight,
            r.df AS df,
            r.total_jobs AS total_jobs,
            r.prevalence AS prevalence,
            r.idf_run_id AS idf_run_id,
            r.context AS original_context
        ORDER BY r.weight DESC, r.min_score DESC
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    target_job_id=target_job_id,
                    student_skills=student_skills,
                )
                # 将结果转为 Python 字典列表
                return [dict(record) for record in result]
        except Exception as e:
            log.error(f"❌ 获取技能缺口失败: {e}")
            return []

    # ==========================================
    # 3. 辅助查询：获取岗位的软素质与门槛细节
    # ==========================================
    def get_job_details(self, job_id: str) -> Optional[GraphNodeJob]:
        """获取岗位节点的结构化属性快照（GraphNodeJob）。

        来历：读取 Neo4j 节点 (Job {id: job_id}) 的 properties，并映射为 GraphNodeJob。
        说明：GraphNodeJob 以显式字段替代 Dict 输出，避免 schema 漂移；未知字段会被忽略。
        """
        query = """
        MATCH (j:Job {id: $job_id})
        RETURN j
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, job_id=job_id)
                record = result.single()
                if record:
                    props = dict(record["j"]) or {}
                    props.setdefault("id", job_id)
                    props.setdefault("job_name", props.get("job_name") or "")
                    return GraphNodeJob(**props)
                return None
        except Exception as e:
            log.error(f"❌ 获取岗位详情失败: {e}")
            return None
