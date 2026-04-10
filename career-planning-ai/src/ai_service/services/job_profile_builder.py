# 通过岗位元信息构建岗位画像
from __future__ import annotations

import asyncio
import json
import random
from typing import List, Optional, Dict, Any, Type, TypeVar

from pydantic import BaseModel, SecretStr

from ai_service.engine.ai_engine import AIEngine, InputStep
from ai_service.models.job_info import JobInfo
from ai_service.models.struct_job_txt import (
    JDAnalysisResult,
    Profiles,
    BasicRequirements,
    ProfessionalSkills,
    ProfessionalLiteracy,
    DevelopmentPotential,
    JobAttributes,
)
from ai_service.services import log
from config import _LLMModelBase, settings

__all__ = [
    "JobProfileBuilder",
    "analyze_job_description",
    "analyze_job_profiles",
]

T = TypeVar("T", bound=BaseModel)

# ==========================================
# 1. 定义 Prompt 模板
# ==========================================
SYSTEM_PROMPT = """
你是一位拥有 10 年经验的资深人力资源专家、组织架构分析师，以及职业图谱构建师，擅长岗位价值评估、胜任力模型搭建、组织人效提升和职位数据标准化。

你的任务是：对输入的多个岗位原始数据进行深度分析，基于岗位名称、职责描述、任职要求等信息，识别出其中最应被合并为同一类的一组岗位，完成岗位标准化、岗位画像提炼和岗位合并，最终只输出 1 个严格符合要求的 JSON 对象，用于精简组织架构和构建标准岗位库。

# 任务目标
你需要基于“输入中的全部职位描述文本集合”进行整体分析，而不是只看某一条岗位名称或某一段 JD。
你必须从所有输入职位中，筛选出“最适合合并为同一标准岗位”的那一组岗位，并舍弃其他不适合合并的岗位。
最终只允许输出 1 个标准岗位对象，不能输出多个对象，不能输出数组。

# 分析要求
1. 不要仅依赖岗位名称判断是否为同一岗位。
2. 必须综合分析以下信息后再判断是否合并：
   - 工作职责
   - 任职要求
   - 技能要求
   - 核心产出
   - 服务对象
   - 业务场景
   - 工作边界
3. 只有当多个岗位在以下四个维度综合重合度达到 75% 以上时，才允许合并：
   - 核心产出是否一致
   - 核心职责是否高度重合
   - 所需技能与能力模型是否高度一致
   - 服务对象、业务场景、工作边界是否一致
4. 若某些岗位与目标岗位组差异明显、职责边界不同、业务场景不同，则必须直接舍弃，不纳入最终结果。
5. 若输入中存在多个完全不同的岗位类别，只保留其中相似度最高、最适合合并的一组，其余全部舍弃。

# 标准岗位命名规则
1. 合并后的岗位必须重新命名为行业通用、表达准确、统一规范的标准岗位名称。
2. 命名格式必须统一为：职级-领域-职称
3. 例如：
   - 初级后端开发工程师
   - 中级新媒体运营专员
   - 高级招聘配置经理
4. 若无法明确判断职级，可使用更稳妥的通用表达，但仍需保持“职级-领域-职称”格式。

# 信息提取与推断规则
1. 所有字段信息优先从“输入的全部职位描述内容”中提取。
2. 若多个 JD 对同一字段描述不同，应优先保留在目标岗位组中出现频率更高、共性更强的内容。
3. “职业技能”优先从输入 JD 原文提取；若原文未明确提及，可基于目标岗位组的职责和行业通用知识进行合理推断；若仍无法判断，填“未提及”。
4. “职业素养”“发展潜力”优先从输入 JD 原文提取；若未明确提及，可结合目标岗位组的岗位特征进行合理推断；若仍无法判断，填“未提及”。
5. “岗位属性”中的推断类字段（如岗位序列、职级层次、晋升路径、行业趋势、通用发展方向等），若输入文本未明确说明，可基于目标岗位组的行业通用认知进行合理推断。
6. 如果某字段在所有输入文本中均未提及，且无法合理推断，则统一填“未提及”。
7. 不允许凭空捏造明显脱离输入岗位集合的内容。
8. 所有字段值必须使用简体中文。
9. 输出必须是合法 JSON，不要包含 Markdown 代码块，不要输出解释性文字，不要输出任何 JSON 之外的说明。

# 数组字段强约束
1. 所有数组类型字段必须输出为 JSON 数组格式。
2. 严禁输出空数组 []。
3. 若数组字段无法从输入中提取到有效内容，必须填充至少 1 个占位值：
   - 优先填 ["未提及"]
   - 不允许填 []
4. 数组字段中的内容必须来自“输入的全部职位描述集合”的汇总提炼；若原文没有明确写出，可在目标岗位组语义范围内做合理归纳，但不得脱离输入岗位类别。

# 输出内容要求
你输出的唯一 JSON 对象必须表达“一个标准岗位”，并且要体现：
1. 该岗位由哪些原始岗位合并而来
2. 为什么这些岗位可以被视为同一标准岗位
3. 该标准岗位的核心职责、能力要求、职业素养、发展潜力、岗位属性

# 字段格式强约束（必须遵守）
1. career_orientation 字段：
   - 必须且只能从以下 6 个值中选择一个：
     ['管理型', '技术型', '业务型', '研究型', '综合型', '不限']

2. lateral_transfer_directions 字段：
   - 必须输出为数组格式
   - 不允许输出单个字符串
   - 不允许输出空数组
   - 若无法判断，填 ["未提及"]

3. core_skills 字段：
   - 必须输出为数组格式
   - 不允许输出单个字符串
   - 不允许输出空数组
   - 若无法判断，填 ["未提及"]

4. tool_capabilities 字段：
   - 必须输出为数组格式
   - 不允许输出单个字符串
   - 不允许输出空数组
   - 若无法判断，填 ["未提及"]

5. language_requirements 字段：
   - 必须输出为数组格式
   - 不允许输出单个字符串
   - 不允许输出空数组
   - 若无法判断，填 ["未提及"]

6. certificates 字段：
   - 必须输出为数组格式
   - 不允许输出单个字符串
   - 不允许输出空数组
   - 若无法判断，填 ["未提及"]

7. 所有枚举类字段（如 degree、industry_trend、salary_competitiveness、social_demand 等）：
   - 如果输入中未明确提及且无法合理推断，请填写“不限”或“未提及”
   - 不要编造枚举之外的新值

8. industry_trend 字段：
   - 必须且只能从以下 3 个值中选择一个：
     ['萎缩', '平稳', '朝阳']

9. salary_competitiveness 字段：
   - 必须且只能从以下 3 个值中选择一个：
     ['低', '中', '高']

10. social_demand 字段：
   - 必须且只能从以下 3 个值中选择一个：
     ['低', '中', '高']

11. degree 字段：
   - 必须且只能从以下 5 个值中选择一个：
     ['不限', '专科', '本科', '硕士', '博士']

# 内容质量要求
1. 不允许只根据岗位名称进行简单合并。
2. 必须结合职责、要求、技能和业务场景做实质性判断。
3. 所有描述要专业、简洁、去重、去口语化，适合用于组织架构梳理与标准岗位库建设。

# 输出要求
1. 只能输出一个 JSON 对象。
2. 不能输出 JSON 数组。
3. 不能输出多个岗位对象。
4. 不能输出任何解释性文字。
5. 必须保证 JSON 可被直接解析。
""".strip()

USER_PROMPT = """
以下是多个职位描述（JD）文本，请你把它们视为一个待分析的岗位集合，而不是彼此独立的单条 JD。

请基于全部输入内容进行横向比较，筛选出其中最适合合并为同一标准岗位的一组职位，完成岗位标准化、岗位画像提炼和岗位合并，并严格按要求只输出 1 个 JSON 对象。

职位描述集合如下：
{jd_text}
""".strip()

PROFILE_ONLY_USER_PROMPT = """
以下是多个职位描述（JD）文本，请你把它们视为一个待分析的岗位集合，而不是彼此独立的单条 JD。

请基于全部输入内容进行横向比较和汇总提炼，只输出“岗位详细画像主体（Profiles）”本身。
不要输出 job_id，不要输出 job_name，不要输出解释说明，不要输出 Markdown，只返回符合 Profiles 结构的 JSON 对象。

职位描述集合如下：
{jd_text}
""".strip()


def _build_profile_template() -> Profiles:
    return Profiles(
        basic_requirements=BasicRequirements(
            degree="不限",
            major="不限",
            certificates=["未提及"],
            internship_requirement="未提及",
            experience_years="不限",
            special_requirements="未提及",
        ),
        professional_skills=ProfessionalSkills(
            core_skills=["未提及"],
            tool_capabilities=["未提及"],
            language_requirements=["未提及"],
            domain_knowledge="未提及",
            project_requirements="未提及",
        ),
        professional_literacy=ProfessionalLiteracy(
            communication="未提及",
            teamwork="未提及",
            stress_management="未提及",
            logic_thinking="未提及",
            ethics="未提及",
        ),
        development_potential=DevelopmentPotential(
            learning_ability="未提及",
            innovation="未提及",
            leadership="未提及",
            adaptability="未提及",
            career_orientation="不限",
        ),
        job_attributes=JobAttributes(
            salary_competitiveness="中",
            social_demand="中",
            industry_trend="平稳",
            industry="不限",
            vertical_promotion_path="未提及",
            prerequisite_roles="未提及",
            lateral_transfer_directions=["未提及"],
        ),
    )


PROFILE_TEMPLATE = _build_profile_template()
PROFILE_TEMPLATE_JSON = PROFILE_TEMPLATE.model_dump_json(by_alias=True, indent=2)

JD_TEMPLATE = JDAnalysisResult(
    job_id="job_001",
    job_name="示例岗位",
    profiles=PROFILE_TEMPLATE,
)
JD_TEMPLATE_JSON = JD_TEMPLATE.model_dump_json(by_alias=True, indent=2)

FULL_SYSTEM_PROMPT = (
    SYSTEM_PROMPT
    + "\n\n# 输出格式说明\n"
    + "请严格按照以下 JSON 格式输出结果，不要包含任何其他文字或 Markdown 标记：\n"
    + JD_TEMPLATE_JSON
)

PROFILE_SYSTEM_PROMPT = (
    SYSTEM_PROMPT
    + "\n\n# 输出格式说明\n"
    + "请严格按照以下 JSON 格式输出结果，不要包含任何其他文字或 Markdown 标记：\n"
    + PROFILE_TEMPLATE_JSON
)

# ==========================================
# 2. 模型配置辅助函数
# ==========================================
def _create_model_config_from_name(
    target_model_name: str,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
) -> _LLMModelBase:
    """
    根据模型名称字符串动态创建 _LLMModelBase 配置对象
    使用 Pydantic model_copy 避免类作用域冲突
    """
    if "/" not in target_model_name:
        provider_map = {
            "qwen": "dashscope",
            "deepseek": "deepseek",
            "gpt-4": "openai",
            "gpt-3.5": "openai",
            "claude": "anthropic",
            "gemini": "gemini",
        }
        for prefix, provider in provider_map.items():
            if target_model_name.lower().startswith(prefix):
                target_model_name = f"{provider}/{target_model_name}"
                break

    default_config = settings.lite_llm.qwen

    update_fields: Dict[str, Any] = {"model_name": target_model_name}

    if api_key:
        update_fields["api_key"] = SecretStr(api_key)
    else:
        update_fields["api_key"] = default_config.api_key

    if api_base:
        update_fields["api_base"] = api_base
    elif getattr(default_config, "api_base", None):
        update_fields["api_base"] = default_config.api_base

    return default_config.model_copy(update=update_fields)


# ==========================================
# 3. 结果修正与输入构建辅助函数
# ==========================================
def fix_llm_json_keys(data: dict) -> dict:
    """
    修复 LLM 返回的 JSON 中的键名不匹配问题 + 空数组兜底
    """
    if not isinstance(data, dict):
        return data

    if "profiles" in data and isinstance(data["profiles"], dict):
        profiles = data["profiles"]

        # 修复 "行业 Domain 知识" -> "行业_Domain_知识"
        if "职业技能" in profiles and isinstance(profiles["职业技能"], dict):
            skills = profiles["职业技能"]
            if "行业 Domain 知识" in skills and "行业_Domain_知识" not in skills:
                skills["行业_Domain_知识"] = skills.pop("行业 Domain 知识")

        # 将空数组兜底为 ["未提及"]
        array_field_mapping = {
            "基础要求": ["证书要求"],
            "职业技能": ["核心专业技能", "工具与平台能力", "语言能力"],
            "岗位属性": ["横向转岗方向"],
        }

        for parent, fields in array_field_mapping.items():
            if parent in profiles and isinstance(profiles[parent], dict):
                for field in fields:
                    if field in profiles[parent] and profiles[parent][field] == []:
                        profiles[parent][field] = ["未提及"]

    return data


def _build_jd_text(jobs: List[JobInfo]) -> str:
    """
    构建发送给 LLM 的 JD 文本
    """
    if not jobs:
        raise ValueError("jobs 不能为空")

    jd_text_parts: List[str] = []
    for job in jobs:
        job_info = (
            f"ID: {getattr(job, 'id', '未知')}\n"
            f"岗位名称: {getattr(job, 'job_title', None) or '未知'}\n"
            f"薪资范围: {getattr(job, 'salary_range', None) or '未知'}\n"
            f"所属行业: {getattr(job, 'industry', None) or '未知'}\n"
            f"岗位描述: {getattr(job, 'job_desc', None) or '未知'}\n"
        )
        jd_text_parts.append(job_info)

    separator = "\n" + "=" * 80 + "\n"
    return separator.join(jd_text_parts)


# ==========================================
# 4. JobProfileBuilder
#    让 job_profile_builder 也拥有和 AIEngine 一样的链式入口
# ==========================================
class JobProfileBuilder:
    """
    岗位画像构建器

    设计目标：
    1. 对外语义聚焦“岗位画像构建”
    2. 对内完全复用 AIEngine 的链式分段调用能力
    3. 支持两种用法：
       - 手动链式调用：builder.pick_brain(...).set_system_role(...).add_text(...).next_step()...
       - 直接业务调用：await builder.build_jd_result(...), await builder.build_profiles(...)
    """

    def __init__(
        self,
        system_prompt: str = FULL_SYSTEM_PROMPT,
        instruction_prompt: str = USER_PROMPT,
        engine: Optional[AIEngine] = None,
    ) -> None:
        self.system_prompt = system_prompt
        self.instruction_prompt = instruction_prompt
        self._engine = engine or AIEngine()

    def pick_brain(
        self,
        model: _LLMModelBase,
        model_fallbacks: Optional[List[_LLMModelBase]] = None,
    ) -> InputStep:
        """
        与 AIEngine 保持一致的入口
        """
        return self._engine.pick_brain(model, model_fallbacks)

    def from_text(
        self,
        text: str,
        model: _LLMModelBase,
        model_fallbacks: Optional[List[_LLMModelBase]] = None,
        system_prompt: Optional[str] = None,
        instruction_prompt: Optional[str] = None,
    ) -> InputStep:
        """
        预填充岗位画像场景的链式起点
        返回的仍然是 InputStep，后续链式调用和 AIEngine 完全一致
        """
        if not text or not text.strip():
            raise ValueError("text 不能为空")

        final_system_prompt = system_prompt or self.system_prompt
        final_instruction_prompt = instruction_prompt or self.instruction_prompt

        pipeline = self.pick_brain(model, model_fallbacks).set_system_role(final_system_prompt)

        if "{jd_text}" in final_instruction_prompt:
            return pipeline.add_text(final_instruction_prompt.format(jd_text=text))

        return pipeline.add_instruction(final_instruction_prompt).add_text(text)

    def from_jobs(
        self,
        jobs: List[JobInfo],
        model: _LLMModelBase,
        model_fallbacks: Optional[List[_LLMModelBase]] = None,
        system_prompt: Optional[str] = None,
        instruction_prompt: Optional[str] = None,
    ) -> InputStep:
        """
        直接从 JobInfo 列表构建链式起点
        """
        jd_text = _build_jd_text(jobs)
        return self.from_text(
            text=jd_text,
            model=model,
            model_fallbacks=model_fallbacks,
            system_prompt=system_prompt,
            instruction_prompt=instruction_prompt,
        )

    async def build_struct(
        self,
        *,
        schema: Type[T],
        jobs: Optional[List[JobInfo]] = None,
        text: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: str = settings.vector.llm_long_model_name,
        temperature: float = 0.1,
        max_retries: int = 3,
        model_fallbacks: Optional[List[_LLMModelBase]] = None,
        system_prompt: Optional[str] = None,
        instruction_prompt: Optional[str] = None,
    ) -> T:
        """
        通用结构化构建入口
        可输出 Profiles / JDAnalysisResult / 其他 BaseModel
        """
        if not text and not jobs:
            raise ValueError("text 和 jobs 至少传一个")

        payload_text = text if text else _build_jd_text(jobs or [])

        if api_key is None:
            api_key = settings.lite_llm.qwen.api_key.get_secret_value()

        model_config = _create_model_config_from_name(model_name, api_key)

        for attempt in range(max_retries):
            try:
                pipeline = self.from_text(
                    text=payload_text,
                    model=model_config,
                    model_fallbacks=model_fallbacks,
                    system_prompt=system_prompt,
                    instruction_prompt=instruction_prompt,
                )

                result = await (
                    pipeline
                    .next_step()
                    .set_llm_params(temperature=temperature)
                    .next_step()
                    .into_struct(schema)
                    .do()
                )

                if result is None:
                    raise ValueError("LLM 返回为空")

                log.info(f"岗位画像构建成功 | schema={schema.__name__}")
                return result

            except Exception as e:
                if attempt >= max_retries - 1:
                    log.error(
                        f"岗位画像构建失败（重试耗尽）| schema={schema.__name__} | error={e}",
                        exc_info=True,
                    )
                    raise

                wait_time = (attempt + 1) * 2 + random.uniform(0, 1)
                log.warning(
                    f"岗位画像构建失败，{wait_time:.2f} 秒后重试 "
                    f"({attempt + 1}/{max_retries}) | schema={schema.__name__} | error={e}"
                )
                await asyncio.sleep(wait_time)

        raise RuntimeError("岗位画像构建失败：超过最大重试次数")

    async def build_jd_result(
        self,
        *,
        jobs: Optional[List[JobInfo]] = None,
        text: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: str = settings.vector.llm_long_model_name,
        temperature: float = 0.1,
        max_retries: int = 3,
        model_fallbacks: Optional[List[_LLMModelBase]] = None,
    ) -> JDAnalysisResult:
        """
        输出完整的 JDAnalysisResult
        """
        result = await self.build_struct(
            schema=JDAnalysisResult,
            jobs=jobs,
            text=text,
            api_key=api_key,
            model_name=model_name,
            temperature=temperature,
            max_retries=max_retries,
            model_fallbacks=model_fallbacks,
            system_prompt=FULL_SYSTEM_PROMPT,
            instruction_prompt=USER_PROMPT,
        )

        result_dict = json.loads(result.model_dump_json(by_alias=True))
        result_dict = fix_llm_json_keys(result_dict)
        normalized = JDAnalysisResult.model_validate(result_dict)

        log.info("JDAnalysisResult 结果标准化完成")
        return normalized

    async def build_profiles(
        self,
        *,
        jobs: Optional[List[JobInfo]] = None,
        text: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: str = settings.vector.llm_long_model_name,
        temperature: float = 0.1,
        max_retries: int = 3,
        model_fallbacks: Optional[List[_LLMModelBase]] = None,
    ) -> Profiles:
        """
        只输出 Profiles
        """
        result = await self.build_struct(
            schema=Profiles,
            jobs=jobs,
            text=text,
            api_key=api_key,
            model_name=model_name,
            temperature=temperature,
            max_retries=max_retries,
            model_fallbacks=model_fallbacks,
            system_prompt=PROFILE_SYSTEM_PROMPT,
            instruction_prompt=PROFILE_ONLY_USER_PROMPT,
        )

        log.info("Profiles 结果构建完成")
        return result


# ==========================================
# 5. 对外兼容函数
# ==========================================
async def analyze_job_description(
    jobs: List[JobInfo],
    api_key: Optional[str] = None,
    model_name: str = settings.vector.llm_long_model_name,
) -> dict:
    """
    兼容旧调用方式：返回完整 JDAnalysisResult 的 dict
    """
    builder = JobProfileBuilder()
    result = await builder.build_jd_result(
        jobs=jobs,
        api_key=api_key,
        model_name=model_name,
    )
    return json.loads(result.model_dump_json(by_alias=True))


async def analyze_job_profiles(
    jobs: List[JobInfo],
    api_key: Optional[str] = None,
    model_name: str = settings.vector.llm_long_model_name,
) -> dict:
    """
    返回纯 Profiles 的 dict
    """
    builder = JobProfileBuilder()
    result = await builder.build_profiles(
        jobs=jobs,
        api_key=api_key,
        model_name=model_name,
    )
    return json.loads(result.model_dump_json(by_alias=True))


# ==========================================
# 6. 测试入口
# ==========================================
if __name__ == "__main__":
    async def main() -> None:
        sample_text = """
ID: 1
岗位名称: C++开发工程师
薪资范围: 10000-20000元/月
所属行业: 计算机软件
岗位描述: 负责 C++/Qt 桌面端功能开发，要求熟悉数据结构、算法、多线程、网络编程。
        """.strip()

        builder = JobProfileBuilder()

        model_config = _create_model_config_from_name(
            settings.vector.llm_long_model_name,
            settings.lite_llm.qwen.api_key.get_secret_value(),
        )

        # 方式1：完全按 AIEngine 风格手动链式调用
        llm = builder.pick_brain(model_config)
        try:
            result1 = await (
                llm
                .set_system_role(PROFILE_SYSTEM_PROMPT)
                .add_instruction("请提取岗位画像主体，只返回 Profiles 对象")
                .add_text(sample_text)
                .next_step()
                .set_llm_params(temperature=0.1)
                .next_step()
                .into_struct(Profiles)
                .do()
            )
        except Exception as e:
            print("异常类型:", type(e).__name__)
            print("异常内容:", repr(e))
            traceback.print_exc()
            raise
        print("=== result1: Profiles ===")
        print(result1.model_dump_json(by_alias=True, indent=2))

        # 方式2：直接使用封装好的业务入口
        result2 = await builder.build_jd_result(text=sample_text)
        print("=== result2: JDAnalysisResult ===")
        print(result2.model_dump_json(by_alias=True, indent=2))

    asyncio.run(main())