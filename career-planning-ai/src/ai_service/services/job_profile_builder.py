#通过岗位元信息构建岗位画像
import os
import json
import re
import asyncio
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_community.chat_models import ChatTongyi
from ai_service.models.struct_job_txt import JDAnalysisResult, JobAttributes
from ai_service.models.job_info import JobInfo
from ai_service.services import log
from config import settings
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()


# 2. 定义 Prompt 模板，可以修改条件

SYSTEM_PROMPT = """
你是一位拥有 10 年经验的资深人力资源专家、组织架构分析师，以及职业图谱构建师，擅长岗位价值评估、胜任力模型搭建、组织人效提升和职位数据标准化。

你的任务是：对输入的多个岗位原始数据进行深度分析，基于岗位名称、职责描述、任职要求等信息，识别出其中**最应被合并为同一类**的一组岗位，完成岗位标准化、岗位画像提炼和岗位合并，最终只输出 **1 个** 严格符合要求的 JSON 结果，用于精简组织架构和构建标准岗位库。

# 核心任务
你需要完成以下工作：


2. 对岗位进行标准化处理：
   - 不要仅依赖岗位名称判断是否为同一岗位。
   - 必须综合分析“工作职责”“任职要求”“技能库”“核心产出”“业务场景”。
   - 从所有输入岗位中，筛选出**最适合合并成同一标准岗位**的一组岗位。
   - 若某些岗位与目标岗位组差异明显、职责边界不同、业务场景不同，则直接舍弃，不纳入最终结果。
   - 最终结果中只保留 1 个标准岗位对象。

3. 为合并后的岗位重新命名：
   - 生成行业通用、表达准确、统一规范的标准岗位名称。
   - 命名格式必须统一为：【职称】-【领域】
   - 例如：运营专员-新媒体、工程师-后端开发、经理-招聘配置

4. 为最终保留的标准岗位生成岗位画像：

   - 剔除重复、冗余、口语化表达
   - 输出内容要简洁、专业、适合用于组织架构梳理与岗位标准库建设

# 提取与推断规则
1. 基础信息优先从 JD 原文提取。
2. “职业技能”优先从 JD 原文提取；若 JD 未明确提及，则基于行业通用知识进行合理推断；若仍无法判断，填充“未提及”。
3. “职业素养”“发展潜力”中的软性要求，若 JD 未明确提及，则基于行业通用知识进行合理推断；若仍无法判断，填充“未提及”。
4. “岗位属性”中的推断类字段（如岗位序列、职级层次、晋升路径、行业趋势、通用发展方向等），若 JD 未明确说明，可基于行业通用知识进行合理推断。
5. 如果某字段在原文中完全未提及且无法合理推断，统一填充“未提及”。
6. 所有字段值必须使用简体中文。
7. 输出必须是合法 JSON，不要包含 Markdown 代码块标记，不要输出解释性文字，不要输出多余说明。
8. 不允许只根据岗位名称进行简单合并，必须结合职责、要求、技能和业务场景做实质性判断。
9. 只有当岗位间核心职责、能力要求、业务场景高度一致时才允许合并；若只是名称相近但职责边界不同，则必须舍弃，不纳入最终输出。
10. 若多个原始岗位被合并，必须保留“合并来源岗位名称”字段，记录原始岗位名称列表。
11. “核心职责”请总结为 3-8 条；“职业技能”请提炼为 3-10 项；“职业素养”请提炼为 3-6 项。
12. 合并依据必须清晰说明：为什么这些岗位被判断为同一标准岗位。
13. 最终只能输出一个标准岗位对象，不能输出多个岗位，不能输出数组中的多个元素。
14. 若输入中存在多个完全不同的岗位类别，只保留其中**相似度最高、最适合合并的一组**，其余全部舍弃。

# 合并判断标准
判断是否合并时，请重点比较以下四个维度：
1. 核心产出是否一致
2. 核心职责是否高度重合
3. 所需技能与能力模型是否高度一致
4. 服务对象、业务场景、工作边界是否一致

只有当以上维度综合重合度达到 80% 以上时，才合并为同一标准岗位。

# 输出要求
1. 必须只输出 **一个 JSON 对象**，不要输出 JSON 数组。
2. 最终结果只能代表 **一个标准岗位**。
3. 与该标准岗位不相同、不能合并的岗位，直接舍弃，不要输出。
4. 不要输出任何 JSON 之外的说明文字。

"""

USER_PROMPT = """
请分析以下职位描述（JD）文本:

{jd_text}
"""


# ==========================================
# 3. 封装调用函数
# ==========================================


def fix_llm_json_keys(data: dict) -> dict:
    """
    修复 LLM 返回的 JSON 中的键名不匹配问题

    Args:
        data: LLM 返回的字典

    Returns:
        dict: 修正后的字典
    """
    if not isinstance(data, dict):
        return data

    # 修复 "行业 Domain 知识" -> "行业_Domain_知识"
    if "profiles" in data and isinstance(data["profiles"], dict):
        profiles = data["profiles"]
        if "职业技能" in profiles and isinstance(profiles["职业技能"], dict):
            skills = profiles["职业技能"]
            if "行业 Domain 知识" in skills:
                skills["行业_Domain_知识"] = skills.pop("行业 Domain 知识")

    return data


def _build_jd_text(jobs: List[JobInfo]) -> str:
    """构建发送给 LLM 的 JD 文本。"""
    jd_text_parts = []
    for job in jobs:
        job_info = f"""ID: {job.id}
        岗位名称: {job.job_title or '未知'}
        薪资范围: {job.salary_range or '未知'}
        所属行业: {job.industry or '未知'}
        岗位描述: {job.job_desc or '未知'}
        """
        jd_text_parts.append(job_info)

    return "\n" + "=" * 80 + "\n".join(jd_text_parts)


def _create_llm(api_key: str, model_name: str) -> ChatTongyi:
    """创建 LLM 实例。"""
    return ChatTongyi(
        api_key=api_key,
        model=model_name,
        temperature=0.1,
        streaming=True,
    )


async def analyze_job_description(
    jobs: List[JobInfo],
    api_key: Optional[str] = None,
    model_name: str = settings.vector.llm_model_name,
) -> dict:
    """
    异步分析多个岗位信息并返回结构化 JSON 数据。

    优先使用 LangChain 的 ainvoke；如果底层模型不支持真正异步，
    则自动回退到 asyncio.to_thread 包装同步 invoke，避免阻塞事件循环。
    """
    jd_text = _build_jd_text(jobs)

    if not api_key:
        api_key = settings.llm.api_key.get_secret_value()

    if not api_key:
        raise ValueError("请提供 API Key 或设置环境变量 LLM__API_KEY")

    llm = _create_llm(api_key=api_key, model_name=model_name)
    parser = PydanticOutputParser(pydantic_object=JDAnalysisResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT + "\n\n# 输出格式说明\n{format_instructions}"),
        ("user", USER_PROMPT),
    ])
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    chain = prompt | llm | parser

    try:
        try:
            result = await chain.ainvoke({"jd_text": jd_text})
        except Exception as async_error:
            log.warning(f"ainvoke 调用失败，回退到线程池 invoke: {async_error}")
            result = await asyncio.to_thread(chain.invoke, {"jd_text": jd_text})

        return result.model_dump(by_alias=True)

    except Exception as e:
        log.error(f"解析错误:{e}", exc_info=True)

        error_msg = str(e)
        if "行业_Domain_知识" in error_msg or "行业 Domain 知识" in error_msg:
            log.warning("检测到键名不匹配问题，尝试修复...")

            try:
                simple_prompt = ChatPromptTemplate.from_messages([
                    ("system", SYSTEM_PROMPT),
                    ("user", USER_PROMPT),
                ])
                simple_chain = simple_prompt | llm

                try:
                    raw_output = await simple_chain.ainvoke({"jd_text": jd_text})
                except Exception as async_error:
                    log.warning(f"ainvoke 修复流程失败，回退到线程池 invoke: {async_error}")
                    raw_output = await asyncio.to_thread(simple_chain.invoke, {"jd_text": jd_text})

                json_match = re.search(r'\{.*\}', raw_output.content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    parsed_data = json.loads(json_str)
                    fixed_data = fix_llm_json_keys(parsed_data)
                    result = JDAnalysisResult.model_validate(fixed_data)
                    return result.model_dump(by_alias=True)

            except Exception as fix_error:
                log.error(f"修复失败: {fix_error}", exc_info=True)

        return {"error": str(e), "raw_text": jd_text}
