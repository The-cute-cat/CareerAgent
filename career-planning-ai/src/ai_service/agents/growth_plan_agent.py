from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from typing import Dict, Any

from ai_service.agents import log
from ai_service.agents.middleware import (
    log_before_model, monitor_tool, track_token_usage,
    reset_token_stats, get_token_stats
)
from ai_service.agents.tools import query_books, query_videos, query_project, query_intern, submit_growth_plan, \
    get_resources_by_ids
from ai_service.services.prompt_loader import prompt_loader
from ai_service.utils.json_fixer import JSONFixer
from config import settings


class GrowthPlanAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.growth_plan_agent.api_key.get_secret_value(),
            model=settings.growth_plan_agent.model_name,
            base_url=settings.growth_plan_agent.base_url,
            timeout=settings.growth_plan_agent.timeout,
            max_retries=settings.growth_plan_agent.max_retries,
            temperature=settings.growth_plan_agent.extra["temperature"]
        )
        self.agent = create_agent(
            model=self.llm,
            system_prompt=prompt_loader.growth_plan_generation,
            tools=[query_books, query_videos, query_project, query_intern, submit_growth_plan],
            middleware=[log_before_model, track_token_usage, monitor_tool]
        )

    def generate_growth_plan(self, target_position: str, student_profile: str, ability_gap: str | None = None):
        # 重置 Token 统计
        reset_token_stats()

        input_message = prompt_loader.small_prompts["growth_plan_user"].format(
            target_position=target_position, student_profile=student_profile,
            ability_gap=ability_gap if ability_gap else "暂无"
        )
        config: RunnableConfig = {
            "recursion_limit": settings.growth_plan_agent.extra["recursion_limit"] or 25
        }
        output = self.agent.invoke(
            {"messages": [HumanMessage(content=input_message)]},
            config=config
        )

        # 输出 Token 统计
        stats = get_token_stats()
        log.info(
            f"[Token 统计] 本次计划生成消耗: "
            f"input_tokens={stats.input_tokens}, output_tokens={stats.output_tokens}, "
            f"total_tokens={stats.total_tokens}, 模型调用次数={stats.call_count}"
        )

        return self._parse_output(output)

    def _parse_output(self, output: dict) -> Dict[str, Any] | None:
        """
        从 Agent 输出中提取成长计划，展开资源引用为完整信息
        
        Returns:
            {"plan": dict} 或 None
        """
        messages = output.get("messages", [])
        if not messages:
            log.warning("Agent 返回的消息列表为空")
            return None

        # 优先从 tool_call 提取
        for msg in reversed(messages):
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    if tool_call["name"] == "submit_growth_plan":
                        plan_data = tool_call["args"]["plan"]
                        return self._build_result(plan_data)

        # 备用：从文本消息提取 JSON
        log.warning("未找到 submit_growth_plan 工具调用，尝试从文本消息中提取 JSON")
        for msg in reversed(messages):
            content = getattr(msg, "content", "")
            if not content or not isinstance(content, str):
                continue

            for json_str in JSONFixer.extract_json_objects(content):
                success, data, _ = JSONFixer.try_parse(json_str)
                if success and isinstance(data, dict):
                    plan_data = data.get("plan", data)
                    if "student_summary" in plan_data and "short_term_plan" in plan_data:
                        log.info("成功从文本消息中提取并解析成长计划")
                        return self._build_result(plan_data)

        log.error("无法从 Agent 输出中提取成长计划")
        return None

    def _build_result(self, plan_dict: dict) -> Dict[str, Any]:
        """构建最终结果：去重查询、原地展开资源"""
        resource_refs = self._extract_resource_refs(plan_dict)

        if resource_refs:
            # 去重
            seen = set()
            unique_refs = []
            for ref in resource_refs:
                key = (ref["id"], ref["type"])
                if key not in seen:
                    seen.add(key)
                    unique_refs.append(ref)

            # 查询并展开
            resources = get_resources_by_ids(unique_refs)
            log.info(f"已加载 {len(unique_refs)} 个资源（去重前 {len(resource_refs)} 个）")
            self._expand_resources_in_plan(plan_dict, resources)

        return {"plan": plan_dict}

    @staticmethod
    def _extract_resource_refs(plan_dict: dict) -> list:
        """从字典中提取所有资源引用"""
        refs = []
        for milestone in plan_dict.get("short_term_plan", {}).get("milestones", []):
            for task in milestone.get("tasks", []):
                refs.extend(task.get("resources", []))
        for milestone in plan_dict.get("mid_term_plan", {}).get("milestones", []):
            for task in milestone.get("tasks", []):
                refs.extend(task.get("resources", []))
        refs.extend(plan_dict.get("mid_term_plan", {}).get("recommended_internships", []))
        return refs

    @staticmethod
    def _expand_resources_in_plan(plan_dict: dict, resources_by_type: dict) -> None:
        """
        在计划字典中原地展开资源引用，将完整资源信息嵌入到 resources 字段中
        
        Args:
            plan_dict: 计划字典（会被原地修改）
            resources_by_type: 按类型分组的完整资源 {
                "books": [...], "videos": [...], "projects": [...], "interns": [...]
            }
        """
        # 创建 ID -> 完整资源的映射
        resource_map = {}
        for resources in resources_by_type.values():
            for res in resources:
                resource_map[res["id"]] = res

        def expand_resources(resources_list: list) -> list:
            """展开资源列表，合并完整信息 + reason"""
            if not resources_list:
                return resources_list

            expanded = []
            for ref in resources_list:
                rid = ref.get("id")
                reason = ref.get("reason", "")

                if rid in resource_map:
                    # 合并完整资源信息 + reason（reason 覆盖原 description 字段或作为独立字段）
                    full_resource = {**resource_map[rid], "reason": reason}
                    expanded.append(full_resource)
                else:
                    # 未找到完整信息，保留原引用
                    expanded.append(ref)

            return expanded

        # 遍历短期计划
        for milestone in plan_dict.get("short_term_plan", {}).get("milestones", []):
            for task in milestone.get("tasks", []):
                if "resources" in task:
                    task["resources"] = expand_resources(task["resources"])

        # 遍历中期计划
        mid_term = plan_dict.get("mid_term_plan", {})
        for milestone in mid_term.get("milestones", []):
            for task in milestone.get("tasks", []):
                if "resources" in task:
                    task["resources"] = expand_resources(task["resources"])

        # 展开推荐实习
        if "recommended_internships" in mid_term:
            mid_term["recommended_internships"] = expand_resources(mid_term["recommended_internships"])


growth_plan_agent = GrowthPlanAgent()


def main():
    import json

    # 测试参数
    target_position = "Java后端开发工程师"

    student_profile = """
    {
        "基础信息": {
            "学历": "本科",
            "专业背景": "计算机科学与技术",
            "证书": ["CET-6", "计算机二级"],
            "实习时长": 0,
            "求职状态": "在校生"
        },
        "专业技能": {
            "核心专业技能": ["Java", "MySQL", "HTML", "CSS", "JavaScript"],
            "工具与平台能力": ["Git", "Maven", "IDEA"],
            "行业领域知识评分": 2,
            "语言能力": ["CET-6 520分"],
            "项目经验丰富度": 2
        },
        "职业素养": {
            "沟通能力": 3,
            "团队协作": 3,
            "抗压能力": 3,
            "逻辑思维": 4,
            "责任心与职业道德": 4
        },
        "发展潜力": {
            "学习能力": 4,
            "创新能力": 3,
            "领导力潜质": 2,
            "职业倾向性": "技术型",
            "环境适应性": 4
        },
        "个人限制": {
            "生理限制": "无",
            "价值观限制": "拒绝博彩行业",
            "环境限制": "无",
            "时间习惯限制": "拒绝夜班",
            "其他特殊要求": "希望在一线城市工作"
        },
        "实践详情": {
            "项目经历详情": "在{学生信息管理系统}项目中担任{核心开发者}，负责{数据库设计与后端开发}，产出{完整的增删改查功能模块}",
            "实习经历详情": "暂无实习经历",
            "校园_实践活动": "在{校园网站开发项目}中担任{前端开发}，负责{页面设计与交互实现}，产出{学校社团活动展示网站}",
            "竞赛获奖详情": "在{蓝桥杯程序设计竞赛}中担任{参赛选手}，负责{算法题解答}，产出{省级三等奖}"
        }
    }
    """

    ability_gap = """
        主要差距：
        1. 缺乏企业级项目开发经验，对Spring Boot、MyBatis等主流框架掌握不足
        2. 对分布式系统、微服务架构缺乏了解
        3. 数据库设计和优化能力薄弱
        4. 缺乏实际的项目部署和运维经验
        5. 缺少有竞争力的开源项目或技术博客
        """

    print("=" * 80)
    print("开始生成成长计划...")
    print("=" * 80)

    result = growth_plan_agent.generate_growth_plan(
        target_position=target_position,
        student_profile=student_profile,
        ability_gap=ability_gap
    )

    if result:
        print("\n✅ 成长计划生成成功！")
        print("=" * 80)

        # 输出计划概要
        plan = result["plan"]
        print(f"目标岗位: {plan['target_position']}")
        print(f"短期目标: {plan['short_term_plan']['goal']}")
        print(f"中期目标: {plan['mid_term_plan']['goal']}")

        # 统计资源数量（从展开后的计划中统计）
        def count_resources(plan_dict):
            """统计计划中的资源数量"""
            count = 0
            for milestone in plan_dict.get("short_term_plan", {}).get("milestones", []):
                for task in milestone.get("tasks", []):
                    count += len(task.get("resources", []))
            for milestone in plan_dict.get("mid_term_plan", {}).get("milestones", []):
                for task in milestone.get("tasks", []):
                    count += len(task.get("resources", []))
            count += len(plan_dict.get("mid_term_plan", {}).get("recommended_internships", []))
            return count

        print(f"\n📚 资源引用总数: {count_resources(plan)}")

        print("\n📋 完整计划:")
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print("\n❌ 成长计划生成失败，请检查日志")

    return result


if __name__ == '__main__':
    main()
