import logging
from typing import List, Dict, Optional, Any, Iterable
from neo4j import GraphDatabase

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

    # ==========================================
    # 1. 逻辑位面查询：硬核路由寻找
    # ==========================================
    def discover_lateral_paths(
        self,
        start_job_id: str,
        max_targets: int = 3,
    ) -> List[Dict[str, Any]]:
        """拓扑探测：从起点出发在 1..2 跳内发现换岗(Lateral Transfer)目标与路径。

        业务定义：换岗路径为沿着 is_cross_micro = true 的 EVOLVE_TO 边到达的岗位。

        约束（来自业务规则）：
        - 只探测 1~2 跳（EVOLVE_TO*1..2）。
        - 目标岗位 micro_community_id 与起点不同。
        - 目标岗位 salary_rank 不低于起点。
        - 优先选择路径上 pareto_rank = 0 的边（作为排序偏好，不做硬过滤）。
        - 按 final_routing_cost（路径累计）升序取前 max_targets 个不同目标岗位。
        """

        query = """
        MATCH (s:Job {id: $start_job_id})
        WITH
            s,
            coalesce(s.salary_rank, 0) AS start_salary_rank,
            coalesce(s.micro_community_id, 0) AS start_micro

        MATCH p = (s)-[r:EVOLVE_TO*1..2]->(t:Job)
        WHERE
            coalesce(t.salary_rank, 0) >= start_salary_rank
            AND coalesce(t.micro_community_id, 0) <> start_micro
            AND all(
                rel IN relationships(p)
                WHERE coalesce(rel.is_cross_micro, false) = true
            )

        WITH
            t,
            p,
            reduce(
                cost = 0.0,
                rel IN relationships(p)
                | cost + coalesce(rel.final_routing_cost, 0.0)
            ) AS total_cost,
            reduce(
                non_pareto = 0,
                rel IN relationships(p)
                | non_pareto
                + CASE WHEN coalesce(rel.pareto_rank, 0) = 0 THEN 0 ELSE 1 END
            ) AS non_pareto_edges

        ORDER BY total_cost ASC, non_pareto_edges ASC
        WITH
            t,
            head(
                collect(
                    {
                        p: p,
                        total_cost: total_cost,
                        non_pareto_edges: non_pareto_edges
                    }
                )
            ) AS best

        RETURN
            t.id AS target_job_id,
            [n IN nodes(best.p) | {
                id: n.id,
                job_name: n.job_name,
                macro_community_id: coalesce(n.macro_community_id, 0),
                micro_community_id: coalesce(n.micro_community_id, 0),
                salary_rank: coalesce(n.salary_rank, 0)
            }] AS path_sequence,
            [rel IN relationships(best.p) | {
                final_routing_cost: coalesce(rel.final_routing_cost, 0.0),
                transfer_cost: coalesce(rel.transfer_cost, 0.0),
                salary_gain: coalesce(rel.salary_gain, 0.0),
                jaccard_high: coalesce(rel.jaccard_high, 0.0),
                cos_low: coalesce(rel.cos_low, 0.0),
                pareto_rank: coalesce(rel.pareto_rank, 0),
                is_cross_macro: coalesce(rel.is_cross_macro, false),
                is_cross_micro: coalesce(rel.is_cross_micro, false)
            }] AS edge_metrics,
            round(best.total_cost, 4) AS total_cost,
            best.non_pareto_edges AS non_pareto_edges
        ORDER BY total_cost ASC, non_pareto_edges ASC
        LIMIT $max_targets
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    start_job_id=start_job_id,
                    max_targets=max_targets,
                )
                return [dict(record) for record in result]
        except Exception as e:
            log.error(f"❌ 拓扑探测换岗目标失败: {e}", exc_info=True)
            return []

    def discover_vertical_paths(
        self,
        start_job_id: str,
        max_targets: int = 3,
    ) -> List[Dict[str, Any]]:
        """拓扑探测：从起点出发在 1..3 跳内发现垂直晋升(Vertical)目标与路径。

        业务定义：
        - 始终留在本赛道：每一跳 EVOLVE_TO 边满足 is_cross_micro = false。
        - 每一跳必须为“上升”：salary_gain > 0。

        约束（来自业务规则）：
        - 探测 1~3 跳（EVOLVE_TO*1..3），模拟 初级->中级->高级 的成长链条。
        - 目标岗位 micro_community_id 与起点相同。
        - 目标岗位 salary_rank 必须高于起点。
        - 优先选择路径上 pareto_rank = 0 的边（作为排序偏好，不做硬过滤）。
        - 按 final_routing_cost（路径累计）升序取前 max_targets 个不同目标岗位。
        """

        query = """
        MATCH (s:Job {id: $start_job_id})
        WITH
            s,
            coalesce(s.salary_rank, 0) AS start_salary_rank,
            coalesce(s.micro_community_id, 0) AS start_micro

        MATCH p = (s)-[r:EVOLVE_TO*1..3]->(t:Job)
        WHERE
            coalesce(t.salary_rank, 0) > start_salary_rank
            AND coalesce(t.micro_community_id, 0) = start_micro
            AND all(
                rel IN relationships(p)
                WHERE
                    coalesce(rel.is_cross_micro, false) = false
                    AND coalesce(rel.salary_gain, 0.0) > 0.0
            )

        WITH
            t,
            p,
            reduce(
                cost = 0.0,
                rel IN relationships(p)
                | cost + coalesce(rel.final_routing_cost, 0.0)
            ) AS total_cost,
            reduce(
                non_pareto = 0,
                rel IN relationships(p)
                | non_pareto
                + CASE WHEN coalesce(rel.pareto_rank, 0) = 0 THEN 0 ELSE 1 END
            ) AS non_pareto_edges

        ORDER BY total_cost ASC, non_pareto_edges ASC
        WITH
            t,
            head(
                collect(
                    {
                        p: p,
                        total_cost: total_cost,
                        non_pareto_edges: non_pareto_edges
                    }
                )
            ) AS best

        RETURN
            t.id AS target_job_id,
            [n IN nodes(best.p) | {
                id: n.id,
                job_name: n.job_name,
                macro_community_id: coalesce(n.macro_community_id, 0),
                micro_community_id: coalesce(n.micro_community_id, 0),
                salary_rank: coalesce(n.salary_rank, 0)
            }] AS path_sequence,
            [rel IN relationships(best.p) | {
                final_routing_cost: coalesce(rel.final_routing_cost, 0.0),
                transfer_cost: coalesce(rel.transfer_cost, 0.0),
                salary_gain: coalesce(rel.salary_gain, 0.0),
                jaccard_high: coalesce(rel.jaccard_high, 0.0),
                cos_low: coalesce(rel.cos_low, 0.0),
                pareto_rank: coalesce(rel.pareto_rank, 0),
                is_cross_macro: coalesce(rel.is_cross_macro, false),
                is_cross_micro: coalesce(rel.is_cross_micro, false)
            }] AS edge_metrics,
            round(best.total_cost, 4) AS total_cost,
            best.non_pareto_edges AS non_pareto_edges
        ORDER BY total_cost ASC, non_pareto_edges ASC
        LIMIT $max_targets
        """

        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    start_job_id=start_job_id,
                    max_targets=max_targets,
                )
                return [dict(record) for record in result]
        except Exception as e:
            log.error(f"❌ 拓扑探测晋升目标失败: {e}", exc_info=True)
            return []

    def get_shortest_path(
        self, start_id: str, target_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        利用 APOC Dijkstra 算法，在 [:EVOLVE_TO] 演化网上寻找综合阻力最小的路径。
        """
        # 注意: 'EVOLVE_TO>' 带有箭头，强制算法只能顺着演化方向（晋升/平调）走，不能逆行退级！
        query = """
        MATCH (start:Job {id: $start_id}), (target:Job {id: $target_id})
        CALL apoc.algo.dijkstra(start, target, 'EVOLVE_TO>',
            'final_routing_cost')
        YIELD path, weight
        RETURN[n in nodes(path) | {
            id: n.id,
            job_name: n.job_name,
            macro_community_id: coalesce(n.macro_community_id, 0),
            micro_community_id: coalesce(n.micro_community_id, 0)
            }] AS path_sequence,[r in relationships(path) | {
                final_routing_cost: r.final_routing_cost,
                transfer_cost: r.transfer_cost,
                salary_gain: r.salary_gain,
                jaccard_high: r.jaccard_high,
                cos_low: r.cos_low,
                pareto_rank: coalesce(r.pareto_rank, 0),
                is_cross_macro: coalesce(r.is_cross_macro, false),
                is_cross_micro: coalesce(r.is_cross_micro, false)
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
    # 2. 语义位面查询：岗位 → 岗位缺口分析（不涉及学生）
    # ==========================================
    def get_transition_skill_gaps(
        self, from_job_id: str, to_job_id: str
    ) -> List[Dict[str, Any]]:
        """计算一次跳跃（from -> to）的技能缺口：to 岗位需要但 from 岗位不要求的技能。

        说明：这是严格的“岗位画像差集”，不涉及任何学生信息。
        """
        query = """
        MATCH (from:Job {id: $from_job_id})-[:REQUIRES]->(c:Competency)
        WITH collect(DISTINCT c.name) AS from_skills
        MATCH (to:Job {id: $to_job_id})-[r:REQUIRES]->(c2:Competency)
        WHERE NOT c2.name IN from_skills
        RETURN
            c2.name AS competency_name,
            c2.category AS category,
            r.min_score AS target_score,
            r.weight AS importance_weight,
            r.context AS original_context
        ORDER BY r.weight DESC, r.min_score DESC
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    from_job_id=from_job_id,
                    to_job_id=to_job_id,
                )
                return [dict(record) for record in result]
        except Exception as e:
            log.error(f"❌ 获取岗位跳跃技能缺口失败: {e}")
            return []

    # ==========================================
    # 3. 目标节点锁定：岗位名称 → job_id 映射
    # ==========================================
    def get_job_id_by_exact_name(self, job_name: str) -> Optional[str]:
        """按岗位名称精确匹配获取 job_id（大小写不敏感）。"""
        query = """
        MATCH (j:Job)
        WHERE toLower(j.job_name) = toLower($job_name)
        RETURN j.id AS job_id
        LIMIT 1
        """
        try:
            with self.driver.session() as session:
                record = session.run(query, job_name=job_name).single()
                if record and record.get("job_id"):
                    return str(record["job_id"])
        except Exception as e:
            log.error(f"❌ 通过名称精确匹配岗位失败: {e}")
        return None

    def search_job_ids_by_name_fragment(
        self, name_fragment: str, limit: int = 3
    ) -> List[str]:
        """按名称片段模糊匹配获取 job_id（大小写不敏感）。"""
        query = """
        MATCH (j:Job)
        WHERE toLower(j.job_name) CONTAINS toLower($name_fragment)
        RETURN DISTINCT j.id AS job_id
        LIMIT $limit
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    name_fragment=name_fragment,
                    limit=limit,
                )
                return [str(r["job_id"]) for r in result if r and r.get("job_id")]
        except Exception as e:
            log.error(
                f"❌ 通过名称片段模糊匹配岗位失败: {e}",
                exc_info=True,
            )
            return []

    def resolve_job_ids_from_titles(
        self,
        titles: Iterable[str],
        limit_per_title: int = 1,
    ) -> List[str]:
        """将一组岗位名称解析为 job_id 列表（先精确，后模糊），并去重保序。"""
        resolved: List[str] = []
        seen = set()

        for title in titles:
            title = (title or "").strip()
            if not title:
                continue

            job_id = self.get_job_id_by_exact_name(title)
            candidates = (
                [job_id]
                if job_id
                else self.search_job_ids_by_name_fragment(
                    title,
                    limit=limit_per_title,
                )
            )

            for cid in candidates:
                if cid and cid not in seen:
                    seen.add(cid)
                    resolved.append(cid)

        return resolved

    # ==========================================
    # 4. 辅助查询：获取岗位的软素质与门槛细节
    # ==========================================
    def get_job_details(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        提取岗位的全量文本属性，专供 Agent 阅读和撰写报告时提供“有血有肉”的上下文。
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
                    # 返回节点内部的所有属性字典
                    return dict(record["j"])
                return None
        except Exception as e:
            log.error(f"❌ 获取岗位详情失败: {e}")
            return None
