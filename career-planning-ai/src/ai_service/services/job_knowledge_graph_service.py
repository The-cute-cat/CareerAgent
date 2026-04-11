import json
import re
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ai_service.models.struct_job_txt import build_jd_result_from_portrait, JDAnalysisResult
from ai_service.repository.job_portrait_repository import JobPortraitRepository
from ai_service.utils.logger_handler import log

class JobKnowledgeGraphService:
    """
    岗位知识图谱生成服务

    功能：
    1. 从 job_profile 表读取所有岗位画像
    2. 将 skills_req 转换为 JDAnalysisResult
    3. 规则骨架 + LLM 结构化补全
    4. 将结果保存回 radar_data

    当前约定：
    1. 最终结果只保留 job_id
    2. 不保留 job_name
    3. 不保留节点 id / source_field / importance / difficulty
    4. 所有层级数量都不固定
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = JobPortraitRepository(session)

    # =========================
    # 对外主入口
    # =========================
    async def generate_all_job_knowledge_graphs(
        self,
        overwrite: bool = False,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        批量生成岗位知识图谱，并保存到 radar_data

        Args:
            overwrite: 是否覆盖已有 radar_data
            limit: 最多处理多少条，便于测试

        Returns:
            统计结果
        """
        portraits = await self.repo.get_list_all(filters={"is_deleted": 0})
        if limit is not None:
            portraits = portraits[:limit]

        total = len(portraits)
        success = 0
        skipped = 0
        failed = 0
        errors: List[Dict[str, Any]] = []

        log.info(f"[JobKnowledgeGraph] 开始批量生成，共 {total} 条岗位画像")

        for portrait in portraits:
            try:
                if portrait.radar_data and not overwrite:
                    skipped += 1
                    log.info(f"[JobKnowledgeGraph] 跳过已有 radar_data 的岗位: id={portrait.id}")
                    continue

                graph = await self.generate_single_job_knowledge_graph(portrait_id=portrait.id)

                if graph:
                    success += 1
                else:
                    failed += 1
                    errors.append({
                        "portrait_id": portrait.id,
                        "error": "图谱生成为空"
                    })

            except Exception as e:
                failed += 1
                log.exception(f"[JobKnowledgeGraph] 生成失败 portrait_id={portrait.id}: {e}")
                errors.append({
                    "portrait_id": portrait.id,
                    "error": str(e)
                })

        return {
            "total": total,
            "success": success,
            "skipped": skipped,
            "failed": failed,
            "errors": errors[:20],
        }

    async def generate_single_job_knowledge_graph(
        self,
        portrait_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        为单个岗位生成知识图谱并写入 radar_data
        """
        portrait = await self.repo.get_by_id(portrait_id)
        if not portrait:
            raise ValueError(f"未找到岗位画像: portrait_id={portrait_id}")

        jd = build_jd_result_from_portrait(portrait)

        skeleton = self._build_rule_skeleton(jd)
        llm_prompt = self._build_llm_prompt(jd, skeleton)
        llm_result = await self._call_llm_json(llm_prompt)

        merged_tree = self._merge_skeleton_and_llm(jd, skeleton, llm_result)
        cleaned_tree = self._normalize_tree(merged_tree)

        await self.repo.update(
            portrait_id=portrait.id,
            update_data={
                "radar_data": cleaned_tree
            }
        )

        log.info(f"[JobKnowledgeGraph] 生成并保存成功: portrait_id={portrait.id}, job_id={jd.job_id}")
        return cleaned_tree

    # =========================
    # 规则骨架
    # =========================
    def _build_rule_skeleton(self, jd: JDAnalysisResult) -> Dict[str, Any]:
        """
        构建规则骨架
        注意：这里只提供候选一级节点和种子知识点，不限制数量
        """
        profiles = jd.profiles

        domains = [
            {
                "label": "岗位基础要求",
                "description": "岗位准入门槛与基本背景要求",
                "seed_points": [
                    "学历与专业要求",
                    "证书与资格要求",
                    "实习与年限要求",
                    "特殊要求"
                ]
            },
            {
                "label": "核心专业技能",
                "description": "岗位要求的核心能力与关键技能",
                "seed_points": self._ensure_list(
                    profiles.professional_skills.core_skills,
                    fallback=[
                        "岗位核心技能",
                        "关键能力要求",
                        "专业技能应用"
                    ]
                )
            },
            {
                "label": "工具与平台能力",
                "description": "岗位常用工具、平台与软件能力要求",
                "seed_points": self._ensure_list(
                    profiles.professional_skills.tool_capabilities,
                    fallback=[
                        "常用工具掌握",
                        "平台使用能力",
                        "工程协作工具"
                    ]
                )
            },
            {
                "label": "行业与业务知识",
                "description": "岗位所在行业、业务流程及领域知识要求",
                "seed_points": self._split_text_points(
                    profiles.professional_skills.domain_knowledge,
                    fallback=[
                        "行业背景认知",
                        "业务流程理解",
                        "领域规则与方法"
                    ]
                )
            },
            {
                "label": "职业素养要求",
                "description": "岗位要求的沟通、协作、逻辑、抗压等职业素养",
                "seed_points": [
                    "沟通表达能力",
                    "团队协作能力",
                    "逻辑分析能力",
                    "抗压与执行能力",
                    "责任心与职业道德"
                ]
            },
            {
                "label": "职业发展路径",
                "description": "岗位的晋升方向、横向迁移与行业趋势",
                "seed_points": self._merge_seed_points(
                    self._split_text_points(profiles.job_attributes.vertical_promotion_path),
                    self._ensure_list(profiles.job_attributes.lateral_transfer_directions),
                    fallback=[
                        "垂直晋升路径",
                        "横向转岗方向",
                        "行业发展趋势"
                    ]
                )
            },
        ]

        selected = [item for item in domains if self._domain_has_meaningful_data(item, jd)]

        # 如果一个都没有，就全部给出兜底骨架
        if not selected:
            selected = domains

        return {
            "job_id": jd.job_id,
            "domains": selected
        }

    def _domain_has_meaningful_data(self, domain: Dict[str, Any], jd: JDAnalysisResult) -> bool:
        """
        判断一级域是否有足够信息
        """
        label = domain["label"]
        profiles = jd.profiles

        if label == "岗位基础要求":
            br = profiles.basic_requirements
            return any([
                br.degree and br.degree != "不限",
                br.major and br.major != "不限",
                br.certificates,
                br.internship_requirement,
                br.experience_years and br.experience_years != "不限",
                br.special_requirements,
            ])

        if label == "核心专业技能":
            return bool(profiles.professional_skills.core_skills)

        if label == "工具与平台能力":
            return bool(profiles.professional_skills.tool_capabilities)

        if label == "行业与业务知识":
            return bool(profiles.professional_skills.domain_knowledge)

        if label == "职业素养要求":
            pl = profiles.professional_literacy
            return any([
                pl.communication,
                pl.teamwork,
                pl.stress_management,
                pl.logic_thinking,
                pl.ethics,
            ])

        if label == "职业发展路径":
            ja = profiles.job_attributes
            return any([
                ja.vertical_promotion_path,
                ja.lateral_transfer_directions,
                ja.industry_trend,
                ja.social_demand,
                ja.prerequisite_roles,
                ja.industry,
            ])

        return True

    # =========================
    # Prompt
    # =========================
    def _build_llm_prompt(self, jd: JDAnalysisResult, skeleton: Dict[str, Any]) -> str:
        """
        构造给大模型的结构化输出提示词
        """
        job_payload = jd.model_dump(mode="json", by_alias=False)

        prompt = f"""
你是一名职业教育知识图谱构建专家。
你的任务是根据岗位画像，生成“岗位知识树”。

【任务要求】
1. 必须围绕给定一级知识域生成内容
2. 可以删减不适合的一级知识域
3. 不允许新增未给出的一级知识域
4. 每个一级知识域下的二级知识点数量不固定
5. 如果某个一级知识域没有合适内容，可以输出空 topics
6. 节点名称要简洁、专业、适合前端树图展示
7. description 要简洁清晰
8. 输出必须是纯 JSON，不要 Markdown，不要解释
9. 最终结果只需要岗位的 job_id
10. 不需要输出 job_name
11. 不需要输出节点 id
12. 不需要输出 importance、difficulty、source_field
13. 所有层级数量都不固定

【岗位画像】
{json.dumps(job_payload, ensure_ascii=False, indent=2)}

【规则骨架】
{json.dumps(skeleton, ensure_ascii=False, indent=2)}

【输出 JSON 格式】
{{
  "domains": [
    {{
      "label": "岗位基础要求",
      "description": "岗位准入门槛与基本背景要求",
      "topics": [
        {{
          "label": "学历与专业要求",
          "description": "理解岗位对学历层次与专业背景的要求"
        }},
        {{
          "label": "证书与资格要求",
          "description": "了解岗位所需证书、资格或加分项要求"
        }}
      ]
    }}
  ]
}}
"""
        return prompt.strip()

    # =========================
    # LLM 调用占位
    # =========================
    async def _call_llm_json(self, prompt: str) -> Dict[str, Any]:
        """
        这里替换成你项目里的大模型调用方式
        需要保证最终返回 dict
        """
        mock_result = {
            "domains": [
                {
                    "label": "岗位基础要求",
                    "description": "岗位准入门槛与基本背景要求",
                    "topics": [
                        {
                            "label": "学历与专业要求",
                            "description": "理解岗位对学历层次与专业背景的要求"
                        },
                        {
                            "label": "证书与资格要求",
                            "description": "了解岗位所需证书、资格或加分项要求"
                        }
                    ]
                },
                {
                    "label": "核心专业技能",
                    "description": "岗位要求的核心能力与关键技能",
                    "topics": [
                        {
                            "label": "核心技能掌握",
                            "description": "掌握岗位所需核心专业技能及其应用"
                        }
                    ]
                }
            ]
        }
        return mock_result

    # =========================
    # 合并 / 清洗
    # =========================
    def _merge_skeleton_and_llm(
        self,
        jd: JDAnalysisResult,
        skeleton: Dict[str, Any],
        llm_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        将规则骨架与 LLM 输出合并，缺省时回退到 seed_points
        """
        llm_domains = {
            item.get("label", "").strip(): item
            for item in llm_result.get("domains", [])
            if isinstance(item, dict) and item.get("label")
        }

        root = {
            "label": "岗位知识图谱",
            "type": "root",
            "description": "基于岗位画像生成的知识树",
            "children": []
        }

        for domain in skeleton["domains"]:
            domain_label = domain["label"]
            domain_desc = domain.get("description", "")
            domain_llm = llm_domains.get(domain_label, {})
            domain_topics = domain_llm.get("topics", [])
            domain_description = domain_llm.get("description") or domain_desc

            valid_topics = self._normalize_topics(domain_topics)

            if not valid_topics:
                valid_topics = [
                    {
                        "label": point,
                        "description": f"围绕“{point}”建立岗位知识与学习要求理解"
                    }
                    for point in domain.get("seed_points", [])
                ]

            domain_node = {
                "label": domain_label,
                "type": "domain",
                "description": domain_description,
                "children": []
            }

            for topic in valid_topics:
                domain_node["children"].append({
                    "label": topic["label"],
                    "type": "topic",
                    "description": topic.get("description"),
                    "children": []
                })

            # 不固定数量，只要这个一级节点下有内容就保留
            if domain_node["children"]:
                root["children"].append(domain_node)

        return {
            "graph_type": "job_knowledge_tree",
            "version": "v1",
            "job_id": jd.job_id,
            "root": root
        }

    def _normalize_tree(self, tree: Dict[str, Any]) -> Dict[str, Any]:
        """
        最终清洗：
        1. 去重
        2. 去空
        3. 不限制层级数量
        """
        root = tree.get("root", {})
        domains = root.get("children", [])

        cleaned_domains = []
        seen_domain_labels = set()

        for domain in domains:
            label = (domain.get("label") or "").strip()
            if not label or label in seen_domain_labels:
                continue
            seen_domain_labels.add(label)

            topics = domain.get("children", [])
            cleaned_topics = []
            seen_topic_labels = set()

            for topic in topics:
                t_label = (topic.get("label") or "").strip()
                if not t_label or t_label in seen_topic_labels:
                    continue
                seen_topic_labels.add(t_label)

                cleaned_topics.append({
                    "label": t_label,
                    "type": "topic",
                    "description": (topic.get("description") or "").strip() or None,
                    "children": []
                })

            if cleaned_topics:
                cleaned_domains.append({
                    "label": label,
                    "type": "domain",
                    "description": (domain.get("description") or "").strip() or None,
                    "children": cleaned_topics
                })

        root["children"] = cleaned_domains
        tree["root"] = root

        return tree

    def _normalize_topics(self, topics: Any) -> List[Dict[str, Any]]:
        """
        清洗 LLM 输出的 topics
        """
        if not isinstance(topics, list):
            return []

        results = []
        for item in topics:
            if not isinstance(item, dict):
                continue

            label = str(item.get("label", "")).strip()
            if not label:
                continue

            results.append({
                "label": label,
                "description": str(item.get("description", "")).strip() or f"围绕“{label}”形成岗位知识点要求"
            })

        return results

    # =========================
    # 小工具
    # =========================
    def _ensure_list(self, value: Any, fallback: Optional[List[str]] = None) -> List[str]:
        fallback = fallback or []

        if isinstance(value, list):
            items = [str(v).strip() for v in value if str(v).strip()]
            return items or fallback

        if isinstance(value, str):
            value = value.strip()
            return [value] if value else fallback

        return fallback

    def _split_text_points(self, value: Any, fallback: Optional[List[str]] = None) -> List[str]:
        fallback = fallback or []

        if not value:
            return fallback

        if isinstance(value, list):
            values = [str(v).strip() for v in value if str(v).strip()]
            return values or fallback

        if isinstance(value, str):
            parts = re.split(r"[,，;；、/\n→]+", value.strip())
            parts = [p.strip() for p in parts if p.strip()]
            return parts or fallback

        return fallback

    def _merge_seed_points(self, *groups: List[str], fallback: Optional[List[str]] = None) -> List[str]:
        fallback = fallback or []
        merged = []
        seen = set()

        for group in groups:
            for item in group or []:
                if item and item not in seen:
                    seen.add(item)
                    merged.append(item)

        return merged or fallback