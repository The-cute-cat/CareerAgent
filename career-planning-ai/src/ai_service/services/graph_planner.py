import uuid
import json
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

from ai_service.models.career_graph import (
    CareerPath,
    CareerPathBundle,
    PathType,
    SkillGapInfo,
)
from ai_service.models.struct_job_txt import JDAnalysisResult
from ai_service.engine.ai_engine import AIEngine
from ai_service.repository.career_repository import CareerRepository
from ai_service.services import log
from config import settings


class CareerPathResponse(BaseModel):
    paths: List[CareerPath] = Field(
        description="为用户规划的包含演化步骤与缺口的职业发展路径列表"
    )


class GraphPlanner:
    def __init__(self, repository: CareerRepository):
        self.repository = repository

        # 统一走 AIEngine：保证全项目单次调用协议一致（LiteLLM + Instructor(MD_JSON)）
        self.engine = AIEngine()
        log.info(
            "✅ GraphPlanner 初始化完成，基于 AIEngine 调用，模型："
            f"{settings.llm.model_name}"
        )

    def _generate_path_id(self) -> str:
        return f"path_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def _safe_float(v: Any, default: float = 0.0) -> float:
        try:
            return float(v)
        except Exception:
            return default

    @staticmethod
    def _safe_int(v: Any, default: int = 0) -> int:
        try:
            return int(v)
        except Exception:
            return default

    def _repair_lateral_paths(
        self,
        paths: List[CareerPath],
        discovered_paths: List[Dict[str, Any]],
    ) -> List[CareerPath]:
        """对换岗(LATERAL)路径做确定性修正，保证输出与图数据一致。

        目标：
        - step_index 连续从 1 开始
        - total_steps == len(steps)
        - total_routing_cost 尽量与图上的 total_cost 一致
        - from/to_job_name 与图节点一致
        - jaccard_high/cos_low/salary_gain 与 EVOLVE_TO 边指标一致
        - 若某一步 skill_gaps 为空，则用 REQUIRES 差集补齐
        """

        candidates = []
        for d in discovered_paths:
            seq = d.get("path_sequence") or []
            edges = d.get("edge_metrics") or []
            if not seq:
                continue
            seq_ids = [str(n.get("id")) for n in seq if n and n.get("id")]
            if not seq_ids:
                continue
            job_name_map = {str(n.get("id")): n.get("job_name") for n in seq}
            candidates.append(
                {
                    "seq_ids": seq_ids,
                    "job_name_map": job_name_map,
                    "edges": edges,
                    "total_cost": d.get("total_cost"),
                }
            )

        for path in paths:
            # 固定为换岗路径
            path.path_type = PathType.LATERAL

            if not path.steps:
                continue

            # 1) 统一 step_index
            for i, step in enumerate(path.steps, start=1):
                step.step_index = i

            # 2) total_steps
            path.total_steps = len(path.steps)

            # 3) 尝试把 LLM 输出路径与图上的真实序列匹配，然后回填关键字段
            derived_seq_ids = [str(path.steps[0].from_job_id)]
            derived_seq_ids.extend([str(s.to_job_id) for s in path.steps])

            matched = None
            for cand in candidates:
                if cand["seq_ids"] == derived_seq_ids:
                    matched = cand
                    break

            if not matched:
                continue

            # 3.1 回填 total_routing_cost
            if matched.get("total_cost") is not None:
                path.total_routing_cost = self._safe_float(
                    matched["total_cost"],
                    0.0,
                )

            # 3.2 回填 from/to_job_name 与 3 个物理指标
            edges = matched.get("edges") or []
            job_name_map = matched.get("job_name_map") or {}

            for idx, step in enumerate(path.steps):
                from_id = str(step.from_job_id)
                to_id = str(step.to_job_id)

                if not step.from_job_name and job_name_map.get(from_id):
                    step.from_job_name = job_name_map[from_id]
                if not step.to_job_name and job_name_map.get(to_id):
                    step.to_job_name = job_name_map[to_id]

                if idx < len(edges):
                    em = edges[idx] or {}
                    step.jaccard_high = self._safe_float(
                        em.get("jaccard_high"),
                        default=step.jaccard_high,
                    )
                    step.cos_low = self._safe_float(
                        em.get("cos_low"),
                        default=step.cos_low,
                    )
                    step.salary_gain = self._safe_float(
                        em.get("salary_gain"),
                        default=step.salary_gain,
                    )

                # 3.3 缺口兜底：如果 LLM 没给缺口，改用岗位→岗位差集补齐
                if step.skill_gaps:
                    continue

                gaps = self.repository.get_transition_skill_gaps(
                    from_id,
                    to_id,
                )
                repaired_gaps: List[SkillGapInfo] = []
                for g in gaps:
                    competency_name = str(g.get("competency_name") or "")
                    category = str(g.get("category") or "")
                    target_score = self._safe_int(
                        g.get("target_score"),
                        default=1,
                    )
                    original_context = str(g.get("original_context") or "")
                    repaired_gaps.append(
                        SkillGapInfo(
                            competency_name=competency_name,
                            category=category,
                            target_score=target_score,
                            original_context=original_context,
                            actionable_advice=(
                                f"围绕 {competency_name} 补齐：做一个小项目并复盘到简历中"
                                if competency_name
                                else "补齐该能力：通过项目练习并沉淀到简历"
                            ),
                        )
                    )
                step.skill_gaps = repaired_gaps

        return paths

    def _repair_vertical_paths(
        self,
        paths: List[CareerPath],
        discovered_paths: List[Dict[str, Any]],
    ) -> List[CareerPath]:
        """对晋升(VERTICAL)路径做确定性修正，保证输出与图数据一致。

        目标：
        - step_index 连续从 1 开始
        - total_steps == len(steps)
        - total_routing_cost 尽量与图上的 total_cost 一致
        - from/to_job_name 与图节点一致
        - jaccard_high/cos_low/salary_gain 与 EVOLVE_TO 边指标一致
        - 若某一步 skill_gaps 为空，则用 REQUIRES 差集补齐
        """

        candidates = []
        for d in discovered_paths:
            seq = d.get("path_sequence") or []
            edges = d.get("edge_metrics") or []
            if not seq:
                continue
            seq_ids = [str(n.get("id")) for n in seq if n and n.get("id")]
            if not seq_ids:
                continue
            job_name_map = {str(n.get("id")): n.get("job_name") for n in seq}
            candidates.append(
                {
                    "seq_ids": seq_ids,
                    "job_name_map": job_name_map,
                    "edges": edges,
                    "total_cost": d.get("total_cost"),
                }
            )

        for path in paths:
            path.path_type = PathType.VERTICAL

            if not path.steps:
                continue

            for i, step in enumerate(path.steps, start=1):
                step.step_index = i

            path.total_steps = len(path.steps)

            derived_seq_ids = [str(path.steps[0].from_job_id)]
            derived_seq_ids.extend([str(s.to_job_id) for s in path.steps])

            matched = None
            for cand in candidates:
                if cand["seq_ids"] == derived_seq_ids:
                    matched = cand
                    break

            if not matched:
                continue

            if matched.get("total_cost") is not None:
                path.total_routing_cost = self._safe_float(
                    matched["total_cost"],
                    0.0,
                )

            edges = matched.get("edges") or []
            job_name_map = matched.get("job_name_map") or {}

            for idx, step in enumerate(path.steps):
                from_id = str(step.from_job_id)
                to_id = str(step.to_job_id)

                if not step.from_job_name and job_name_map.get(from_id):
                    step.from_job_name = job_name_map[from_id]
                if not step.to_job_name and job_name_map.get(to_id):
                    step.to_job_name = job_name_map[to_id]

                if idx < len(edges):
                    em = edges[idx] or {}
                    step.jaccard_high = self._safe_float(
                        em.get("jaccard_high"),
                        default=step.jaccard_high,
                    )
                    step.cos_low = self._safe_float(
                        em.get("cos_low"),
                        default=step.cos_low,
                    )
                    step.salary_gain = self._safe_float(
                        em.get("salary_gain"),
                        default=step.salary_gain,
                    )

                if step.skill_gaps:
                    continue

                gaps = self.repository.get_transition_skill_gaps(
                    from_id,
                    to_id,
                )
                repaired_gaps: List[SkillGapInfo] = []
                for g in gaps:
                    competency_name = str(g.get("competency_name") or "")
                    category = str(g.get("category") or "")
                    target_score = self._safe_int(
                        g.get("target_score"),
                        default=1,
                    )
                    original_context = str(g.get("original_context") or "")
                    repaired_gaps.append(
                        SkillGapInfo(
                            competency_name=competency_name,
                            category=category,
                            target_score=target_score,
                            original_context=original_context,
                            actionable_advice=(
                                f"围绕 {competency_name} 做一次高阶实践并沉淀方法论"
                                if competency_name
                                else "针对该能力做一次高阶实践并沉淀方法论"
                            ),
                        )
                    )
                step.skill_gaps = repaired_gaps

        return paths

    async def build_lateral_paths_with_llm(
        self,
        starting_job: Union[Dict[str, Any], BaseModel],
        max_paths: int = 5,
        limit_per_title: int = 1,
    ) -> CareerPathBundle:
        """从“起始岗位（含横向转岗意向）”出发，规划纯岗位间的横向转岗路径。

        输入严格只包含岗位信息（及预析结果 deep_analysis 作为语义上下文），不涉及学生节点或学生技能。
        """
        # 兼容两种输入：
        # 1) Pydantic StartingJob（推荐：raw_data=JDAnalysisResult，
        #    deep_analysis=DeepAnalysisResult）
        # 2) dict（兼容旧调用）
        current_job_id: Optional[str]
        raw_data_obj: Any
        deep_analysis_obj: Any

        if isinstance(starting_job, dict):
            current_job_id = starting_job.get("job_id")
            raw_data_obj = starting_job.get("raw_data")
            deep_analysis_obj = starting_job.get("deep_analysis")
        else:
            current_job_id = getattr(starting_job, "job_id", None)
            raw_data_obj = getattr(starting_job, "raw_data", None)
            deep_analysis_obj = getattr(starting_job, "deep_analysis", None)

        # 注意：lateral_transfer_directions 仅作为“文本证据”给 LLM 做交叉验证，
        # 禁止用于目标发现（目标必须由图拓扑探测产生）。
        if isinstance(raw_data_obj, JDAnalysisResult):
            job_attributes = raw_data_obj.profiles.job_attributes
            lateral_transfer_directions_text = (
                job_attributes.lateral_transfer_directions or ""
            )
            raw_data_job_id = raw_data_obj.job_id
        else:
            raw_data_dict = raw_data_obj if isinstance(raw_data_obj, dict) else {}
            lateral_transfer_directions_text = (
                raw_data_dict.get("profiles", {})
                .get("job_attributes", {})
                .get("lateral_transfer_directions", "")
                or ""
            )
            raw_data_job_id = raw_data_dict.get("job_id")

        if not current_job_id:
            return CareerPathBundle(
                start_job_id="",
                start_job_name=None,
                paths=[],
            )

        # 一致性检查：避免“用 A 的 job_id 寻路，却用 B 的 JD 文本做交叉验证”
        if raw_data_job_id and str(raw_data_job_id) != str(current_job_id):
            log.warning(
                "⚠️ StartingJob.job_id 与 raw_data.job_id 不一致："
                f"{current_job_id} vs {raw_data_job_id}，"
                "将以 StartingJob.job_id 为物理起点"
            )

        # Step 1: 拓扑探测（Target Discovery）
        # 以 EVOLVE_TO 的图结构自动发现换岗目标：
        # - 1..2 跳
        # - 全路径边 is_cross_micro = true
        # - 目标 micro 不同
        # - 目标 salary_rank >= 起点 salary_rank
        # - 排序偏好：pareto_rank=0 边更多 + total_cost 更低
        discovered_paths = self.repository.discover_lateral_paths(
            start_job_id=current_job_id,
            max_targets=3,
        )
        if not discovered_paths:
            log.warning(f"⚠️ 拓扑探测未发现可用换岗目标：start={current_job_id}")
            return CareerPathBundle(
                start_job_id=str(current_job_id),
                start_job_name=(
                    getattr(raw_data_obj, "job_name", None)
                    if isinstance(raw_data_obj, JDAnalysisResult)
                    else (
                        (raw_data_obj or {}).get("job_name")
                        if isinstance(raw_data_obj, dict)
                        else None
                    )
                ),
                paths=[],
            )

        log.info(
            "🚀 开始横向转岗路径流水线："
            f"start={current_job_id} 探测到 {len(discovered_paths)} 条候选路径"
        )

        all_context_blocks = []
        for discovered in discovered_paths[: max_paths or 3]:
            target_job_id = discovered.get("target_job_id")
            path_sequence = discovered.get("path_sequence", [])
            edge_metrics = discovered.get("edge_metrics", [])
            total_cost = discovered.get("total_cost")

            if not target_job_id or not path_sequence:
                continue

            # 2. 语义图位面：对沿途每一次跳跃做“岗位→岗位”的集合减法缺口
            transition_gaps = []
            for i in range(len(path_sequence) - 1):
                from_station = path_sequence[i]
                to_station = path_sequence[i + 1]

                gaps = self.repository.get_transition_skill_gaps(
                    from_station["id"],
                    to_station["id"],
                )
                transition_gaps.append(
                    {
                        "from_job_id": from_station["id"],
                        "from_job_name": from_station.get("job_name"),
                        "to_job_id": to_station["id"],
                        "to_job_name": to_station.get("job_name"),
                        "missing_skills": gaps,
                    }
                )

            # 3. 将前面取得的信息连同前端传进来的预析结果一块封装给大模型上下文
            block = {
                "starting_job": {
                    "job_id": current_job_id,
                    "raw_data": (
                        raw_data_obj.model_dump()
                        if isinstance(raw_data_obj, BaseModel)
                        else (raw_data_obj or {})
                    ),
                    "deep_analysis": (
                        deep_analysis_obj.model_dump()
                        if isinstance(deep_analysis_obj, BaseModel)
                        else (deep_analysis_obj or {})
                    ),
                    "lateral_transfer_directions": (lateral_transfer_directions_text),
                },
                "target_job_id": target_job_id,
                "physical_path": {
                    "sequence": path_sequence,
                    "edges": edge_metrics,
                },
                "semantic_gaps": transition_gaps,
                "total_cost": total_cost,
            }
            all_context_blocks.append(json.dumps(block, ensure_ascii=False))

        if not all_context_blocks:
            log.warning("没有成功获取到任何可用的物理及语义路径，中断规划")
            return CareerPathBundle(
                start_job_id=str(current_job_id),
                start_job_name=(
                    getattr(raw_data_obj, "job_name", None)
                    if isinstance(raw_data_obj, JDAnalysisResult)
                    else (
                        (raw_data_obj or {}).get("job_name")
                        if isinstance(raw_data_obj, dict)
                        else None
                    )
                ),
                paths=[],
            )

        # 4. Agent 因果推理：强制要求 LLM 根据传入的大模型上下文提取完整的 CareerPath 对象
        system_prompt = """
    你是一个基于无状态图谱架构的 AI 职业路径规划 Agent。
    我将为你提供如下信息：
    1. 从起始岗位到目标岗位的物理跃迁路径（仅岗位节点 + EVOLVE_TO 带权边指标）；这些目标由拓扑探测产生；
    2. 从语义位面基于 REQUIRES 边做的“岗位→岗位”集合减法缺口，
       即每一次跳跃 from->to 的缺口及 JD 原文 context；
    3. 前端传来的起始岗位预析结果 deep_analysis（仅作为语义润色与风险提示的上下文）。
    4. 起始岗位 JD 文本中的 lateral_transfer_directions（仅作为“行业共识文本证据”，不可用来生成目标）。

    你的任务：
    请基于以上数据进行全局因果推理。结合路径成本、薪资增益与技能缺口，
    提炼每一步的 transition_reason 以及 skill_gaps，
    并对每个缺口补入可行的行动建议 actionable_advice，
    最终生成每条线路的 overall_summary 并构建一条完整的 CareerPath。

    约束：
    - 全程只讨论“岗位→岗位”的路径，不要引入学生、求职者、用户画像等主体。
    - 每个 TransitionStep 的缺口 skill_gaps 必须来源于对应的
        from->to 缺口（semantic_gaps.missing_skills）。
    - 物理边指标字段含义：
      jaccard_high(硬技能重合度)、cos_low(软素质契合度)、salary_gain(薪资增益)、final_routing_cost(该跳跃阻力)。
        - 你必须把每条路径的 path_type 固定为 lateral。

        交叉验证任务：
                - 如果图算法推荐的目标岗位在 lateral_transfer_directions 文本中出现：
                    强调“这不仅是行业共识，更是基于全网图谱数据验证的最优路径”。
                - 如果图算法发现了文本没提到的目标岗位：
                    强调“基于图谱深度关联，我们发现了一条隐藏的高价值转岗通道”。
    """.strip()

        user_content = "请分析以下路径图与技能缺口上下文数据，并强制返回结构化的 Pydantic 路径对象：\n" + "\n\n---\n\n".join(
            all_context_blocks
        )

        try:
            log.info("⏳ 正在通过 AIEngine 发送结构化路径提取请求...")
            response: Optional[CareerPathResponse] = (
                await self.engine.pick_brain(model=settings.llm)
                .set_system_role(system_prompt)
                .add_text(user_content)
                .next_step()
                .set_llm_params(max_retries=2)
                .next_step()
                .into_struct(CareerPathResponse)
                .do()
            )

            if not response:
                return CareerPathBundle(
                    start_job_id=str(current_job_id),
                    start_job_name=(
                        getattr(raw_data_obj, "job_name", None)
                        if isinstance(raw_data_obj, JDAnalysisResult)
                        else (
                            (raw_data_obj or {}).get("job_name")
                            if isinstance(raw_data_obj, dict)
                            else None
                        )
                    ),
                    paths=[],
                )

            # 为返回数据补齐业务必需的随机 ID
            final_paths = response.paths
            for p in final_paths:
                if not p.path_id or "path_" not in p.path_id:
                    p.path_id = self._generate_path_id()
                p.path_type = PathType.LATERAL

            # 确定性校验/回填（仅换岗路径）：用图上的真实数据修正关键字段
            final_paths = self._repair_lateral_paths(
                paths=final_paths,
                discovered_paths=discovered_paths,
            )

            log.info(f"🎉 成功由 Instructor 获取并校验 {len(final_paths)} 条演化路径")
            return CareerPathBundle(
                start_job_id=str(current_job_id),
                start_job_name=(
                    getattr(raw_data_obj, "job_name", None)
                    if isinstance(raw_data_obj, JDAnalysisResult)
                    else (
                        (raw_data_obj or {}).get("job_name")
                        if isinstance(raw_data_obj, dict)
                        else None
                    )
                ),
                paths=final_paths,
            )

        except Exception as e:
            log.error(f"❌ Instructor LLM 请求提取路径时异常：{e}", exc_info=True)
            return CareerPathBundle(
                start_job_id=str(current_job_id or ""),
                start_job_name=(
                    getattr(raw_data_obj, "job_name", None)
                    if isinstance(raw_data_obj, JDAnalysisResult)
                    else (
                        (raw_data_obj or {}).get("job_name")
                        if isinstance(raw_data_obj, dict)
                        else None
                    )
                ),
                paths=[],
            )

    async def build_vertical_paths_with_llm(
        self,
        starting_job: Union[Dict[str, Any], BaseModel],
        max_paths: int = 3,
    ) -> CareerPathBundle:
        """从起始岗位出发，规划纯岗位间的垂直晋升路径。

        约束：
        - 目标发现必须由图拓扑探测产生（不得由文本生成目标）。
        - 垂直晋升定义：沿 EVOLVE_TO 边，is_cross_micro=false 且 salary_gain>0。
        - 输出严格为 List[CareerPath]，path_type 固定为 vertical。
        """

        current_job_id: Optional[str]
        raw_data_obj: Any
        deep_analysis_obj: Any

        if isinstance(starting_job, dict):
            current_job_id = starting_job.get("job_id")
            raw_data_obj = starting_job.get("raw_data")
            deep_analysis_obj = starting_job.get("deep_analysis")
        else:
            current_job_id = getattr(starting_job, "job_id", None)
            raw_data_obj = getattr(starting_job, "raw_data", None)
            deep_analysis_obj = getattr(starting_job, "deep_analysis", None)

        if isinstance(raw_data_obj, JDAnalysisResult):
            job_attributes = raw_data_obj.profiles.job_attributes
            vertical_promotion_path_text = job_attributes.vertical_promotion_path or ""
            raw_data_job_id = raw_data_obj.job_id
        else:
            raw_data_dict = raw_data_obj if isinstance(raw_data_obj, dict) else {}
            vertical_promotion_path_text = (
                raw_data_dict.get("profiles", {})
                .get("job_attributes", {})
                .get("vertical_promotion_path", "")
                or ""
            )
            raw_data_job_id = raw_data_dict.get("job_id")

        if not current_job_id:
            return CareerPathBundle(
                start_job_id="",
                start_job_name=None,
                paths=[],
            )

        if raw_data_job_id and str(raw_data_job_id) != str(current_job_id):
            log.warning(
                "⚠️ StartingJob.job_id 与 raw_data.job_id 不一致："
                f"{current_job_id} vs {raw_data_job_id}，"
                "将以 StartingJob.job_id 为物理起点"
            )

        discovered_paths = self.repository.discover_vertical_paths(
            start_job_id=current_job_id,
            max_targets=3,
        )
        if not discovered_paths:
            log.warning(f"⚠️ 拓扑探测未发现可用晋升路径：start={current_job_id}")
            return CareerPathBundle(
                start_job_id=str(current_job_id),
                start_job_name=(
                    getattr(raw_data_obj, "job_name", None)
                    if isinstance(raw_data_obj, JDAnalysisResult)
                    else (
                        (raw_data_obj or {}).get("job_name")
                        if isinstance(raw_data_obj, dict)
                        else None
                    )
                ),
                paths=[],
            )

        log.info(
            "🚀 开始垂直晋升路径流水线："
            f"start={current_job_id} 探测到 {len(discovered_paths)} 条候选路径"
        )

        all_context_blocks = []
        for discovered in discovered_paths[: max_paths or 3]:
            target_job_id = discovered.get("target_job_id")
            path_sequence = discovered.get("path_sequence", [])
            edge_metrics = discovered.get("edge_metrics", [])
            total_cost = discovered.get("total_cost")

            if not target_job_id or not path_sequence:
                continue

            transition_gaps = []
            for i in range(len(path_sequence) - 1):
                from_station = path_sequence[i]
                to_station = path_sequence[i + 1]

                gaps = self.repository.get_transition_skill_gaps(
                    from_station["id"],
                    to_station["id"],
                )
                transition_gaps.append(
                    {
                        "from_job_id": from_station["id"],
                        "from_job_name": from_station.get("job_name"),
                        "to_job_id": to_station["id"],
                        "to_job_name": to_station.get("job_name"),
                        "missing_skills": gaps,
                    }
                )

            block = {
                "starting_job": {
                    "job_id": current_job_id,
                    "raw_data": (
                        raw_data_obj.model_dump()
                        if isinstance(raw_data_obj, BaseModel)
                        else (raw_data_obj or {})
                    ),
                    "deep_analysis": (
                        deep_analysis_obj.model_dump()
                        if isinstance(deep_analysis_obj, BaseModel)
                        else (deep_analysis_obj or {})
                    ),
                    "vertical_promotion_path": (vertical_promotion_path_text),
                },
                "target_job_id": target_job_id,
                "physical_path": {
                    "sequence": path_sequence,
                    "edges": edge_metrics,
                },
                "semantic_gaps": transition_gaps,
                "total_cost": total_cost,
            }
            all_context_blocks.append(json.dumps(block, ensure_ascii=False))

        if not all_context_blocks:
            log.warning("没有成功获取到任何可用的物理及语义晋升路径，中断规划")
            return CareerPathBundle(
                start_job_id=str(current_job_id),
                start_job_name=(
                    getattr(raw_data_obj, "job_name", None)
                    if isinstance(raw_data_obj, JDAnalysisResult)
                    else (
                        (raw_data_obj or {}).get("job_name")
                        if isinstance(raw_data_obj, dict)
                        else None
                    )
                ),
                paths=[],
            )

        system_prompt = """
你是一个基于无状态图谱架构的 AI 职业路径规划 Agent。

我将为你提供：
1) 起始岗位到目标岗位的物理晋升路径（仅岗位节点 + EVOLVE_TO 带权边指标）；
   这些目标由图拓扑探测产生；
2) 每一步 from->to 的岗位→岗位缺口（基于 REQUIRES 边做集合减法，含 JD 原文 context）；
3) 前端传来的起始岗位预析结果 deep_analysis（仅用于语义润色与风险提示）；
4) 起始岗位 JD 文本中的 vertical_promotion_path（仅作为“文本证据”，不可用于生成目标）。

你的任务：
- 验证图路径与 vertical_promotion_path 文本建议的吻合度；
- 解释每一级跳跃的核心价值提升（技能深度、复杂度、影响力、带团队/带项目等）；
- 重点针对 missing_skills 给出高阶发展的行动建议（要可执行、可落地）。

约束：
- 全程只讨论“岗位→岗位”的路径，不要引入学生、求职者、用户画像等主体。
- 每个 TransitionStep 的 skill_gaps 必须来源于对应 from->to 的 missing_skills。
- 物理边指标字段含义：
  jaccard_high(硬技能重合度)、cos_low(软素质契合度)、salary_gain(薪资增益)、final_routing_cost(该跳跃阻力)。
- 你必须把每条路径的 path_type 固定为 vertical。

交叉验证：
- 若图算法推荐的目标岗位在 vertical_promotion_path 文本中出现：
  强调“这不仅是文本建议，也是图谱数据验证的最优晋升链条”。
- 若图算法发现了文本没提到的目标岗位：
  强调“基于图谱拓扑，我们发现了一条隐藏的高价值晋升通道”。
""".strip()

        user_content = "请分析以下晋升路径图与技能缺口上下文数据，并强制返回结构化的 Pydantic 路径对象：\n" + "\n\n---\n\n".join(
            all_context_blocks
        )

        try:
            log.info("⏳ 正在通过 AIEngine 发送结构化晋升路径提取请求...")
            response: Optional[CareerPathResponse] = (
                await self.engine.pick_brain(model=settings.llm)
                .set_system_role(system_prompt)
                .add_text(user_content)
                .next_step()
                .set_llm_params(max_retries=2)
                .next_step()
                .into_struct(CareerPathResponse)
                .do()
            )

            if not response:
                return CareerPathBundle(
                    start_job_id=str(current_job_id),
                    start_job_name=(
                        getattr(raw_data_obj, "job_name", None)
                        if isinstance(raw_data_obj, JDAnalysisResult)
                        else (
                            (raw_data_obj or {}).get("job_name")
                            if isinstance(raw_data_obj, dict)
                            else None
                        )
                    ),
                    paths=[],
                )

            final_paths = response.paths
            for p in final_paths:
                if not p.path_id or "path_" not in p.path_id:
                    p.path_id = self._generate_path_id()
                p.path_type = PathType.VERTICAL

            final_paths = self._repair_vertical_paths(
                paths=final_paths,
                discovered_paths=discovered_paths,
            )

            log.info(f"🎉 成功由 Instructor 获取并校验 {len(final_paths)} 条晋升路径")
            return CareerPathBundle(
                start_job_id=str(current_job_id),
                start_job_name=(
                    getattr(raw_data_obj, "job_name", None)
                    if isinstance(raw_data_obj, JDAnalysisResult)
                    else (
                        (raw_data_obj or {}).get("job_name")
                        if isinstance(raw_data_obj, dict)
                        else None
                    )
                ),
                paths=final_paths,
            )

        except Exception as e:
            log.error(f"❌ Instructor LLM 请求提取晋升路径时异常：{e}", exc_info=True)
            return CareerPathBundle(
                start_job_id=str(current_job_id or ""),
                start_job_name=(
                    getattr(raw_data_obj, "job_name", None)
                    if isinstance(raw_data_obj, JDAnalysisResult)
                    else (
                        (raw_data_obj or {}).get("job_name")
                        if isinstance(raw_data_obj, dict)
                        else None
                    )
                ),
                paths=[],
            )

    def close(self):
        """关闭资源"""
        if self.repository:
            self.repository.close()
