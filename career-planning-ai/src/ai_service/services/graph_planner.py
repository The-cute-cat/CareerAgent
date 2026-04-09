import uuid
from typing import List, Dict, Any, Optional

from ai_service.models.career_graph import (
    CareerPath,
    CareerPathBundle,
    TransitionStep,
    UniversalGapInfo,
    GapType,
    PathType,
    JobSnapshot,
    EvolveEdgeEvidence,
    BuildRunEvidence,
)
from ai_service.models.graph import GraphNodeJob
from ai_service.repository.career_repository import CareerRepository
from ai_service.services import log


class GraphPlanner:
    def __init__(self, repository: CareerRepository):
        self.repository = repository

        log.info("✅ GraphPlanner 初始化完成（纯证据模式）")

    def _generate_path_id(self) -> str:
        return f"path_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def _classify_path_type(edge_metrics: List[Dict[str, Any]]) -> PathType:
        if any(bool(e.get("is_cross_macro")) for e in edge_metrics):
            return PathType.CROSS_INDUSTRY
        if any(bool(e.get("is_cross_micro")) for e in edge_metrics):
            return PathType.LATERAL
        return PathType.VERTICAL

    @staticmethod
    def _build_job_snapshot(
        job: GraphNodeJob,
    ) -> JobSnapshot:
        return JobSnapshot(
            job_id=job.id,
            job_name=job.job_name,
            attributes=job,
        )

    def _build_career_path_from_query_result(
        self,
        *,
        start_job_id: str,
        path_result: Dict[str, Any],
        path_type: PathType,
        start_skill_baseline: List[str],
    ) -> Optional[CareerPath]:
        path_sequence = path_result.get("path_sequence", [])
        edge_metrics = path_result.get("edge_metrics", [])
        total_cost = path_result.get("total_cost", 0.0)

        if not path_sequence or len(path_sequence) < 2:
            return None

        build_run_evidence = None
        run_id = edge_metrics[0].get("build_run_id") if edge_metrics else None
        if run_id:
            run = self.repository.get_build_run(run_id)
            if run:
                build_run_evidence = BuildRunEvidence(
                    run_id=str(run_id),
                    status=run.get("status"),
                    meta_json=run.get("meta_json"),
                )

        job_props_map: Dict[str, GraphNodeJob] = {}
        for node in path_sequence:
            jid = node.get("id")
            if not jid:
                continue
            job = self.repository.get_job_details(jid)
            if not job:
                job = GraphNodeJob(id=jid, job_name=node.get("job_name") or "")
            job_props_map[jid] = job

        # 仅用 job_id 的情况下：用“起点岗位 requires 技能”作为基线，并沿路径逐站累积。
        known_skills = set(start_skill_baseline)

        steps: List[TransitionStep] = []
        for idx in range(len(path_sequence) - 1):
            from_node = path_sequence[idx]
            to_node = path_sequence[idx + 1]

            from_id = from_node["id"]
            to_id = to_node["id"]
            from_name = from_node.get("job_name", "")
            to_name = to_node.get("job_name", "")

            edge = edge_metrics[idx] if idx < len(edge_metrics) else {}

            edge_evidence = EvolveEdgeEvidence(
                from_job_id=edge.get("from_id") or from_id,
                to_job_id=edge.get("to_id") or to_id,
                final_routing_cost=edge.get("final_routing_cost"),
                transfer_cost=edge.get("transfer_cost"),
                salary_gain=edge.get("salary_gain"),
                jaccard_high=edge.get("jaccard_high"),
                cos_low=edge.get("cos_low"),
                pareto_rank=edge.get("pareto_rank"),
                pareto_group_size=edge.get("pareto_group_size"),
                pareto_front_size=edge.get("pareto_front_size"),
                is_cross_macro=edge.get("is_cross_macro"),
                is_cross_micro=edge.get("is_cross_micro"),
                base_attraction=edge.get("base_attraction"),
                rank_penalty=edge.get("rank_penalty"),
                cross_penalty=edge.get("cross_penalty"),
                build_run_id=edge.get("build_run_id"),
                lineage_json=edge.get("lineage_json"),
            )

            gaps_raw = self.repository.get_skill_gaps(
                to_id,
                list(known_skills),
            )
            gaps: List[UniversalGapInfo] = []
            for g in gaps_raw:
                name = g.get("competency_name", "")
                gaps.append(
                    UniversalGapInfo(
                        gap_key=f"hard:{name}",
                        gap_type=GapType.HARD_SKILL,
                        gap_name=name,
                        category=g.get("category", ""),
                        target_score=int(g.get("target_score") or 0),
                        original_context=g.get("original_context", ""),
                        importance_weight=g.get("importance_weight"),
                        local_weight=g.get("local_weight"),
                        idf_weight=g.get("idf_weight"),
                        df=g.get("df"),
                        total_jobs=g.get("total_jobs"),
                        prevalence=g.get("prevalence"),
                        idf_run_id=g.get("idf_run_id"),
                    )
                )

            step = TransitionStep(
                step_index=idx + 1,
                from_job_id=from_id,
                from_job_name=from_name,
                to_job_id=to_id,
                to_job_name=to_name,
                jaccard_high=float(edge.get("jaccard_high") or 0.0),
                cos_low=float(edge.get("cos_low") or 0.0),
                salary_gain=float(edge.get("salary_gain") or 0.0),
                from_job_snapshot=self._build_job_snapshot(
                    job_props_map.get(
                        from_id,
                        GraphNodeJob(id=from_id, job_name=from_name or ""),
                    )
                ),
                to_job_snapshot=self._build_job_snapshot(
                    job_props_map.get(
                        to_id,
                        GraphNodeJob(id=to_id, job_name=to_name or ""),
                    )
                ),
                skill_gaps=gaps,
                edge_evidence=edge_evidence,
            )
            steps.append(step)

            # 累积：把 to 岗位的 requires 技能也加入已掌握集合
            for s in self.repository.get_required_skill_names(to_id):
                known_skills.add(s)

        return CareerPath(
            path_id=self._generate_path_id(),
            path_type=path_type,
            total_steps=len(steps),
            total_routing_cost=float(total_cost or 0.0),
            steps=steps,
            build_run_evidence=build_run_evidence,
        )

    def build_vertical_promotion_bundle(self, job_id: str) -> CareerPathBundle:
        brief = self.repository.get_job_brief(job_id)
        start_name = brief.get("job_name") if brief else None
        baseline = self.repository.get_required_skill_names(job_id)
        results = self.repository.find_vertical_promotion_paths(
            start_id=job_id,
            max_hops=5,
            limit=10,
        )
        paths = []
        for r in results:
            p = self._build_career_path_from_query_result(
                start_job_id=job_id,
                path_result=r,
                path_type=PathType.VERTICAL,
                start_skill_baseline=baseline,
            )
            if p:
                paths.append(p)
        return CareerPathBundle(
            start_job_id=job_id,
            start_job_name=start_name,
            paths=paths,
        )

    def build_lateral_transfer_bundle(self, job_id: str) -> CareerPathBundle:
        brief = self.repository.get_job_brief(job_id)
        start_name = brief.get("job_name") if brief else None
        baseline = self.repository.get_required_skill_names(job_id)
        results = self.repository.find_lateral_transfer_paths(
            start_id=job_id,
            max_hops=2,
            limit=10,
        )
        paths = []
        for r in results:
            p = self._build_career_path_from_query_result(
                start_job_id=job_id,
                path_result=r,
                path_type=PathType.LATERAL,
                start_skill_baseline=baseline,
            )
            if p:
                paths.append(p)
        return CareerPathBundle(
            start_job_id=job_id,
            start_job_name=start_name,
            paths=paths,
        )

    def build_cross_industry_bundle(self, job_id: str) -> CareerPathBundle:
        brief = self.repository.get_job_brief(job_id)
        start_name = brief.get("job_name") if brief else None
        baseline = self.repository.get_required_skill_names(job_id)
        results = self.repository.find_cross_industry_paths(
            start_id=job_id,
            max_hops=2,
            limit=10,
        )
        paths = []
        for r in results:
            p = self._build_career_path_from_query_result(
                start_job_id=job_id,
                path_result=r,
                path_type=PathType.CROSS_INDUSTRY,
                start_skill_baseline=baseline,
            )
            if p:
                paths.append(p)
        return CareerPathBundle(
            start_job_id=job_id,
            start_job_name=start_name,
            paths=paths,
        )

    def build_goal_planning_bundle(
        self,
        *,
        start_job_id: str,
        target_job_id: str,
        limit_paths: int,
    ) -> CareerPathBundle:
        """目标设定与职业路径规划：给定起点与目标岗位，返回多条候选路径。

        口径：
        - 候选路径按 total_cost（sum(final_routing_cost)）升序优先。
        - 每条路径仍返回每步的边级证据与技能缺口证据。
        """

        brief = self.repository.get_job_brief(start_job_id)
        start_name = brief.get("job_name") if brief else None
        baseline = self.repository.get_required_skill_names(start_job_id)

        results = self.repository.find_goal_planning_paths(
            start_id=start_job_id,
            target_id=target_job_id,
            max_hops=10,
            limit=limit_paths,
        )

        paths: List[CareerPath] = []
        for r in results:
            edge_metrics = r.get("edge_metrics", [])
            inferred_type = self._classify_path_type(edge_metrics)
            p = self._build_career_path_from_query_result(
                start_job_id=start_job_id,
                path_result=r,
                path_type=inferred_type,
                start_skill_baseline=baseline,
            )
            if p:
                paths.append(p)

        return CareerPathBundle(
            start_job_id=start_job_id,
            start_job_name=start_name,
            paths=paths,
        )

    def close(self):
        """关闭资源"""
        if self.repository:
            self.repository.close()
