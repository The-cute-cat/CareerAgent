import asyncio
import json
import re
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ai_service.models.struct_job_txt import build_jd_result_from_portrait, JDAnalysisResult
from ai_service.repository.job_portrait_repository import JobPortraitRepository
from ai_service.utils.logger_handler import log


class JobKnowledgeGraphService:
    """
    岗位知识图谱生成服务（极简树结构版）

    最终写入 radar_data 的数据格式：
    {
        "name": "岗位知识图谱",
        "children": [
            {
                "name": "核心专业技能",
                "children": [
                    {
                        "name": "Python",
                        "children": [
                            {"name": "基础概念", "children": []},
                            {"name": "典型任务", "children": []}
                        ]
                    }
                ]
            }
        ]
    }

    约定：
    1. 最终结构只保留 name 和 children
    2. 层级和数量都不固定
    3. 支持 LLM 输出任意深度树
    4. 即使没有 LLM，也会先基于规则生成尽可能丰富的骨架
    """

    ROOT_NAME = "岗位知识图谱"

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = JobPortraitRepository(session)

    # =========================
    # 对外主入口
    # =========================

    async def sync_all_job_portrait_radar_data(
            self,
            overwrite: bool = True,
            only_empty: bool = False,
            limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        自动搜索 JobPortrait 表中的全部岗位画像，
        为每个岗位生成知识图谱树，并写入 radar_data。

        Args:
            overwrite: 是否覆盖已有 radar_data
            only_empty: 是否只处理 radar_data 为空的记录
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

        log.info(
            f"[JobKnowledgeGraph] 开始同步全部 JobPortrait 图谱，共 {total} 条 | "
            f"overwrite={overwrite}, only_empty={only_empty}, limit={limit}"
        )

        for portrait in portraits:
            try:
                # 只处理空 radar_data
                if only_empty and portrait.radar_data:
                    skipped += 1
                    log.info(
                        f"[JobKnowledgeGraph] 跳过非空 radar_data 的岗位: portrait_id={portrait.id}"
                    )
                    continue

                # 不覆盖已有 radar_data
                if portrait.radar_data and not overwrite and not only_empty:
                    skipped += 1
                    log.info(
                        f"[JobKnowledgeGraph] 跳过已有 radar_data 的岗位: portrait_id={portrait.id}"
                    )
                    continue

                graph = await self.generate_single_job_knowledge_graph(
                    portrait_id=portrait.id
                )

                if graph:
                    success += 1
                    log.info(
                        f"[JobKnowledgeGraph] 同步成功: portrait_id={portrait.id}, "
                        f"job_title={getattr(portrait, 'job_title', None)}"
                    )
                else:
                    failed += 1
                    errors.append({
                        "portrait_id": portrait.id,
                        "job_title": getattr(portrait, "job_title", None),
                        "error": "生成结果为空"
                    })

            except Exception as e:
                failed += 1
                log.exception(
                    f"[JobKnowledgeGraph] 同步失败 portrait_id={portrait.id}: {e}"
                )
                errors.append({
                    "portrait_id": portrait.id,
                    "job_title": getattr(portrait, "job_title", None),
                    "error": str(e)
                })

        result = {
            "total": total,
            "success": success,
            "skipped": skipped,
            "failed": failed,
            "errors": errors[:50],
        }

        log.info(f"[JobKnowledgeGraph] 全量同步完成: {result}")
        return result

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

        # 1. 规则骨架：先尽量把节点铺开
        skeleton = self._build_rule_skeleton(jd)

        # 2. LLM 补全：要求输出也只能是 name + children
        llm_prompt = self._build_llm_prompt(jd, skeleton)
        llm_result = await self._call_llm_json(llm_prompt)

        # 3. 提取 LLM 树并与骨架合并
        llm_tree = self._extract_tree_from_llm(llm_result)
        merged_tree = self._merge_skeleton_and_llm(skeleton, llm_tree)

        # 4. 最终归一化，只保留 name/children
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
        输出只有 name + children
        层级不固定，尽量展开更多节点
        """
        profiles = jd.profiles

        domains: List[Dict[str, Any]] = []

        basic_nodes = self._build_basic_requirement_nodes(jd)
        if basic_nodes:
            domains.append(self._make_node("岗位基础要求", basic_nodes))

        core_skill_nodes = self._build_core_skill_nodes(jd)
        if core_skill_nodes:
            domains.append(self._make_node("核心专业技能", core_skill_nodes))

        tool_nodes = self._build_tool_nodes(jd)
        if tool_nodes:
            domains.append(self._make_node("工具与平台能力", tool_nodes))

        domain_knowledge_nodes = self._build_domain_knowledge_nodes(jd)
        if domain_knowledge_nodes:
            domains.append(self._make_node("行业与业务知识", domain_knowledge_nodes))

        literacy_nodes = self._build_literacy_nodes(jd)
        if literacy_nodes:
            domains.append(self._make_node("职业素养要求", literacy_nodes))

        path_nodes = self._build_path_nodes(jd)
        if path_nodes:
            domains.append(self._make_node("职业发展路径", path_nodes))

        # 如果完全没有数据，则给一个兜底骨架
        if not domains:
            domains = self._build_default_domains()

        return self._make_node(self.ROOT_NAME, domains)

    def _build_basic_requirement_nodes(self, jd: JDAnalysisResult) -> List[Dict[str, Any]]:
        br = jd.profiles.basic_requirements
        children: List[Dict[str, Any]] = []

        if getattr(br, "degree", None) and br.degree != "不限":
            children.append(
                self._make_node("学历要求", [
                    self._make_node(str(br.degree))
                ])
            )

        majors = self._ensure_list(getattr(br, "major", None))
        majors = [m for m in majors if m != "不限"]
        if majors:
            children.append(
                self._make_node("专业背景", [self._make_node(m) for m in majors])
            )

        certificates = self._ensure_list(getattr(br, "certificates", None))
        if certificates:
            children.append(
                self._make_node("证书与资格", [self._make_node(c) for c in certificates])
            )

        internship_requirement = getattr(br, "internship_requirement", None)
        internship_points = self._split_text_points(internship_requirement)
        if internship_points:
            children.append(
                self._make_node("实习要求", [self._make_node(p) for p in internship_points])
            )

        if getattr(br, "experience_years", None) and br.experience_years != "不限":
            children.append(
                self._make_node("经验要求", [
                    self._make_node(str(br.experience_years))
                ])
            )

        special_requirements = self._split_text_points(getattr(br, "special_requirements", None))
        if special_requirements:
            children.append(
                self._make_node("特殊要求", [self._make_node(p) for p in special_requirements])
            )

        return children

    def _build_core_skill_nodes(self, jd: JDAnalysisResult) -> List[Dict[str, Any]]:
        skills = self._ensure_list(
            jd.profiles.professional_skills.core_skills,
            fallback=["岗位核心技能", "关键能力要求", "专业技能应用"]
        )
        return self._build_expandable_knowledge_nodes(
            items=skills,
            sub_templates=["基础概念", "典型任务", "项目实践", "进阶提升"]
        )

    def _build_tool_nodes(self, jd: JDAnalysisResult) -> List[Dict[str, Any]]:
        tools = self._ensure_list(
            jd.profiles.professional_skills.tool_capabilities,
            fallback=["常用工具掌握", "平台使用能力", "工程协作工具"]
        )
        return self._build_expandable_knowledge_nodes(
            items=tools,
            sub_templates=["基础使用", "高频功能", "协作规范", "排错优化"]
        )

    def _build_domain_knowledge_nodes(self, jd: JDAnalysisResult) -> List[Dict[str, Any]]:
        domain_points = self._split_text_points(
            jd.profiles.professional_skills.domain_knowledge,
            fallback=["行业背景认知", "业务流程理解", "领域规则与方法"]
        )
        return self._build_expandable_knowledge_nodes(
            items=domain_points,
            sub_templates=["基础认知", "业务流程", "规则方法", "案例应用"]
        )

    def _build_literacy_nodes(self, jd: JDAnalysisResult) -> List[Dict[str, Any]]:
        pl = jd.profiles.professional_literacy

        literacy_mapping = [
            ("沟通表达能力", getattr(pl, "communication", None)),
            ("团队协作能力", getattr(pl, "teamwork", None)),
            ("抗压与执行能力", getattr(pl, "stress_management", None)),
            ("逻辑分析能力", getattr(pl, "logic_thinking", None)),
            ("责任心与职业道德", getattr(pl, "ethics", None)),
        ]

        children: List[Dict[str, Any]] = []

        for title, raw_value in literacy_mapping:
            points = self._split_text_points(raw_value)
            if points:
                children.append(
                    self._make_node(
                        title,
                        [self._make_node(p) for p in points]
                    )
                )
            elif raw_value:
                children.append(
                    self._make_node(
                        title,
                        [self._make_node(str(raw_value).strip())]
                    )
                )

        if not children:
            default_titles = [
                "沟通表达能力",
                "团队协作能力",
                "逻辑分析能力",
                "抗压与执行能力",
                "责任心与职业道德"
            ]
            children = [
                self._make_node(
                    title,
                    [
                        self._make_node("关键表现"),
                        self._make_node("实践要求"),
                        self._make_node("提升方式"),
                    ]
                )
                for title in default_titles
            ]

        return children

    def _build_path_nodes(self, jd: JDAnalysisResult) -> List[Dict[str, Any]]:
        ja = jd.profiles.job_attributes
        children: List[Dict[str, Any]] = []

        vertical = getattr(ja, "vertical_promotion_path", None)
        if vertical:
            vertical_node = self._build_chain_path_node("垂直晋升路径", vertical)
            if vertical_node:
                children.append(vertical_node)

        lateral_list = self._ensure_list(getattr(ja, "lateral_transfer_directions", None))
        if lateral_list:
            lateral_children = [
                self._make_node(
                    item,
                    [
                        self._make_node("能力补齐"),
                        self._make_node("迁移场景"),
                        self._make_node("发展方向"),
                    ]
                )
                for item in lateral_list
            ]
            children.append(self._make_node("横向迁移方向", lateral_children))

        industry_trend = self._split_text_points(getattr(ja, "industry_trend", None))
        if industry_trend:
            children.append(
                self._make_node("行业发展趋势", [self._make_node(p) for p in industry_trend])
            )

        social_demand = self._split_text_points(getattr(ja, "social_demand", None))
        if social_demand:
            children.append(
                self._make_node("社会需求与岗位热度", [self._make_node(p) for p in social_demand])
            )

        prerequisite_roles = self._split_text_points(getattr(ja, "prerequisite_roles", None))
        if prerequisite_roles:
            children.append(
                self._make_node("前置岗位基础", [self._make_node(p) for p in prerequisite_roles])
            )

        industry = self._split_text_points(getattr(ja, "industry", None))
        if industry:
            children.append(
                self._make_node("所属行业", [self._make_node(p) for p in industry])
            )

        if not children:
            children = [
                self._make_node("垂直晋升路径", [
                    self._make_node("初级阶段"),
                    self._make_node("中级阶段"),
                    self._make_node("高级阶段"),
                ]),
                self._make_node("横向迁移方向", [
                    self._make_node("相关岗位迁移"),
                    self._make_node("能力补齐方向"),
                ]),
            ]

        return children

    def _build_default_domains(self) -> List[Dict[str, Any]]:
        return [
            self._make_node("岗位基础要求", [
                self._make_node("学历与专业"),
                self._make_node("证书资格"),
                self._make_node("实习经验"),
            ]),
            self._make_node("核心专业技能", [
                self._make_node("基础概念"),
                self._make_node("典型任务"),
                self._make_node("项目实践"),
            ]),
            self._make_node("工具与平台能力", [
                self._make_node("基础使用"),
                self._make_node("高频功能"),
                self._make_node("协作规范"),
            ]),
            self._make_node("行业与业务知识", [
                self._make_node("行业背景"),
                self._make_node("业务流程"),
                self._make_node("规则方法"),
            ]),
            self._make_node("职业素养要求", [
                self._make_node("沟通协作"),
                self._make_node("逻辑分析"),
                self._make_node("责任意识"),
            ]),
            self._make_node("职业发展路径", [
                self._make_node("垂直晋升"),
                self._make_node("横向迁移"),
                self._make_node("趋势发展"),
            ]),
        ]

    # =========================
    # Prompt
    # =========================
    def _build_llm_prompt(self, jd: JDAnalysisResult, skeleton: Dict[str, Any]) -> str:
        """
        构造给大模型的结构化输出提示词
        最终只允许输出 name 和 children
        强调：生成“该岗位需要的知识点和内容”
        """
        job_payload = jd.model_dump(mode="json", by_alias=False)

        prompt = f"""
    你是一名职业教育知识图谱构建专家。
    你的任务是根据岗位画像，生成一棵“该岗位所需知识点与学习内容树”。

    【任务目标】
    请围绕“这个岗位实际需要掌握什么知识、每个知识点下需要学习什么内容”来生成树结构。
    不要泛泛而谈，不要生成空洞分类，而是要突出：
    1. 该岗位需要的知识点
    2. 每个知识点下对应的学习内容、理解内容、实践内容
    3. 节点名称适合前端学习路径图展示

    【输出字段要求】
    1. 输出必须是树结构，且最终字段只能有：
       - name
       - children
    2. 不允许输出以下字段：
       - label
       - description
       - type
       - id
       - root
       - job_id
       - graph_type
       - version
       - domains
       - topics
       - source_field
       - importance
       - difficulty
    3. 根节点 name 固定为："岗位知识图谱"
    4. children 必须始终是数组
    5. 叶子节点也必须保留 children: []
    6. 层级不固定，数量不固定，可以根据岗位内容继续向下展开

    【生成原则】
    1. 生成内容必须紧扣岗位要求，体现“该岗位需要学什么”
    2. 一级节点表示知识领域，不要过多空泛分类
    3. 二级节点优先表示该岗位需要掌握的“具体知识点”
    4. 三级及以下节点优先表示该知识点下需要掌握的“内容”
    5. “内容”可以包括但不限于：
       - 基础概念
       - 核心原理
       - 常用方法
       - 实践应用
       - 业务场景
       - 工具使用
       - 项目实现
       - 常见问题
       - 进阶内容
    6. 不要生成与岗位无关的内容
    7. 不要只写“能力提升”“综合素质”这类空节点，尽量写具体
    8. 节点名称要简洁、专业、适合树图展示
    9. 同类内容不要重复
    10. 如果岗位画像中的某部分信息不足，可以结合岗位常见要求合理补全，但不能偏离岗位本身

    【你生成的树应尽量符合下面的语义】
    - 第一层：知识领域
    - 第二层：该岗位需要的具体知识点
    - 第三层及以下：该知识点下需要掌握的内容

    【错误示例】
    错误：只生成“专业能力 / 综合能力 / 发展路径”这类空泛标题，下面没有具体知识内容
    错误：只做分类，不写该岗位真正要掌握的知识点
    错误：生成与岗位弱相关甚至无关的内容

    【正确示例思路】
    例如某岗位需要“Python开发”：
    - 核心专业技能
      - Python编程
        - 基础语法
        - 面向对象
        - 异常处理
        - 常用标准库
        - 项目实践

    例如某岗位需要“数据分析”：
    - 数据分析能力
      - 数据清洗
        - 缺失值处理
        - 异常值处理
        - 数据格式转换
      - 数据可视化
        - 图表选择
        - 可视化表达
        - 结果解读

    【岗位画像】
    {json.dumps(job_payload, ensure_ascii=False, indent=2)}

    【规则骨架】
    {json.dumps(skeleton, ensure_ascii=False, indent=2)}

    【输出要求再强调一次】
    - 只输出 JSON
    - 不要解释
    - 不要 Markdown
    - 不要前后缀文本
    - 最终只能有 name 和 children 两个字段

    【输出示例】
    {{
      "name": "岗位知识图谱",
      "children": [
        {{
          "name": "核心专业技能",
          "children": [
            {{
              "name": "Python编程",
              "children": [
                {{
                  "name": "基础语法",
                  "children": []
                }},
                {{
                  "name": "面向对象编程",
                  "children": []
                }},
                {{
                  "name": "异常处理",
                  "children": []
                }},
                {{
                  "name": "常用标准库",
                  "children": []
                }},
                {{
                  "name": "项目实践",
                  "children": []
                }}
              ]
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
        这里替换成你项目里的真实大模型调用方式
        需要保证最终返回 dict

        当前先给一个 mock，结构已经改成只保留 name / children
        """
        mock_result = {
            "name": "岗位名称",
            "children": [
                {
                    "name": "岗位基础要求",
                    "children": [
                        {
                            "name": "学历与专业",
                            "children": [
                                {"name": "学历要求", "children": []},
                                {"name": "专业背景", "children": []}
                            ]
                        },
                        {
                            "name": "证书与资格",
                            "children": [
                                {"name": "证书要求", "children": []},
                                {"name": "加分项", "children": []}
                            ]
                        }
                    ]
                },
                {
                    "name": "核心专业技能",
                    "children": [
                        {
                            "name": "核心技能掌握",
                            "children": [
                                {"name": "基础概念", "children": []},
                                {"name": "典型任务", "children": []},
                                {"name": "项目实践", "children": []}
                            ]
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
        skeleton: Dict[str, Any],
        llm_tree: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        将规则骨架与 LLM 树递归合并
        """
        return self._merge_tree_nodes(skeleton, llm_tree)

    def _extract_tree_from_llm(self, llm_result: Any) -> Dict[str, Any]:
        """
        尽可能兼容多种 LLM 返回结构，统一转成 name + children
        """
        if isinstance(llm_result, dict):
            # 已经是标准树
            if "name" in llm_result and "children" in llm_result:
                return llm_result

            # 老格式：{"root": {...}}
            root = llm_result.get("root")
            if isinstance(root, dict):
                return root

            # 老格式：{"domains": [...]}
            domains = llm_result.get("domains")
            if isinstance(domains, list):
                return {
                    "name": self.ROOT_NAME,
                    "children": [
                        self._convert_legacy_node(item)
                        for item in domains
                        if self._convert_legacy_node(item) is not None
                    ]
                }

        return self._make_node(self.ROOT_NAME, [])

    def _convert_legacy_node(self, node: Any) -> Optional[Dict[str, Any]]:
        """
        将老格式 label/topics/domains 兼容转为 name/children
        """
        if isinstance(node, str):
            name = node.strip()
            if not name:
                return None
            return self._make_node(name)

        if not isinstance(node, dict):
            return None

        name = str(node.get("name") or node.get("label") or "").strip()
        if not name:
            return None

        raw_children = (
            node.get("children")
            if isinstance(node.get("children"), list)
            else node.get("topics")
            if isinstance(node.get("topics"), list)
            else node.get("domains")
            if isinstance(node.get("domains"), list)
            else []
        )

        children: List[Dict[str, Any]] = []
        for child in raw_children:
            converted = self._convert_legacy_node(child)
            if converted:
                children.append(converted)

        return self._make_node(name, children)

    def _normalize_tree(self, tree: Dict[str, Any]) -> Dict[str, Any]:
        """
        最终清洗：
        1. 只保留 name / children
        2. 递归去重
        3. 去空节点
        4. 层级不限
        """
        normalized = self._normalize_node(tree)

        if not normalized:
            return self._make_node(self.ROOT_NAME, [])

        if normalized["name"] != self.ROOT_NAME:
            normalized = self._make_node(
                self.ROOT_NAME,
                [normalized]
            )

        return normalized

    def _normalize_node(self, node: Any) -> Optional[Dict[str, Any]]:
        """
        将任意输入递归归一化为：
        {"name": "...", "children": [...]}
        """
        if isinstance(node, str):
            name = node.strip()
            if not name:
                return None
            return self._make_node(name, [])

        if not isinstance(node, dict):
            return None

        name = str(node.get("name") or node.get("label") or "").strip()
        if not name:
            return None

        raw_children = []
        if isinstance(node.get("children"), list):
            raw_children = node["children"]
        elif isinstance(node.get("topics"), list):
            raw_children = node["topics"]
        elif isinstance(node.get("domains"), list):
            raw_children = node["domains"]

        child_map: Dict[str, Dict[str, Any]] = {}

        for child in raw_children:
            normalized_child = self._normalize_node(child)
            if not normalized_child:
                continue

            child_name = normalized_child["name"]
            if child_name in child_map:
                child_map[child_name] = self._merge_tree_nodes(child_map[child_name], normalized_child)
            else:
                child_map[child_name] = normalized_child

        return self._make_node(name, list(child_map.values()))

    def _merge_tree_nodes(self, base: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
        """
        递归合并两棵树，只保留 name / children
        """
        base_node = self._normalize_node(base)
        extra_node = self._normalize_node(extra)

        if not base_node and not extra_node:
            return self._make_node(self.ROOT_NAME, [])

        if not base_node:
            return extra_node  # type: ignore
        if not extra_node:
            return base_node

        # 如果根名不同，把 extra 视为 base 的附加子树
        if base_node["name"] != extra_node["name"]:
            extra_as_child_root = self._make_node(base_node["name"], [extra_node])
            return self._merge_tree_nodes(base_node, extra_as_child_root)

        merged_children_map: Dict[str, Dict[str, Any]] = {}

        for child in base_node.get("children", []):
            merged_children_map[child["name"]] = child

        for child in extra_node.get("children", []):
            child_name = child["name"]
            if child_name in merged_children_map:
                merged_children_map[child_name] = self._merge_tree_nodes(
                    merged_children_map[child_name],
                    child
                )
            else:
                merged_children_map[child_name] = child

        return self._make_node(base_node["name"], list(merged_children_map.values()))

    # =========================
    # 节点构建小工具
    # =========================
    def _make_node(self, name: str, children: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        return {
            "name": str(name).strip(),
            "children": children or []
        }

    def _build_expandable_knowledge_nodes(
        self,
        items: List[str],
        sub_templates: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        给每个知识点自动补一层常见子节点，让树更丰富
        """
        sub_templates = sub_templates or ["基础概念", "典型任务", "实践应用", "进阶提升"]

        nodes: List[Dict[str, Any]] = []
        for item in items:
            item = str(item).strip()
            if not item:
                continue

            child_nodes = [self._make_node(t) for t in sub_templates]
            nodes.append(self._make_node(item, child_nodes))

        return nodes

    def _build_chain_path_node(self, root_name: str, raw_path: Any) -> Optional[Dict[str, Any]]:
        """
        将类似：
        初级 -> 中级 -> 高级 -> 专家
        转成链式嵌套树
        """
        parts = self._split_path_points(raw_path)
        if not parts:
            return None

        if len(parts) == 1:
            return self._make_node(root_name, [self._make_node(parts[0])])

        chain = self._make_node(parts[-1], [])
        for part in reversed(parts[:-1]):
            chain = self._make_node(part, [chain])

        return self._make_node(root_name, [chain])

    # =========================
    # 文本处理小工具
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
            parts = re.split(r"[,，;；、/\n|｜]+", value.strip())
            parts = [p.strip() for p in parts if p.strip()]
            return parts or fallback

        return fallback

    def _split_path_points(self, value: Any) -> List[str]:
        if not value:
            return []

        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]

        if isinstance(value, str):
            parts = re.split(r"\s*(?:->|→|=>|＞|>|/|｜|\||-)\s*", value.strip())
            parts = [p.strip() for p in parts if p.strip()]
            return parts

        return []


async def main():
    from ai_service.repository.connection_session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:

        service = JobKnowledgeGraphService(session=session)
        result = await service.sync_all_job_portrait_radar_data()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())