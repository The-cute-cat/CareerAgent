# 通过岗位元信息构建岗位画像
from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import traceback
from dataclasses import dataclass, field
from typing import Any, AsyncIterable, Dict, Generic, List, Optional, Type, TypeVar

import instructor
import litellm
from pydantic import BaseModel, SecretStr

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

__all__ = [
    "JobProfileAIEngine",
    "BaseStep",
    "InputStep",
    "TuneStep",
    "ShapeStep",
    "StructActionStep",
    "TextActionStep",
    "JobProfileBuilder",
    "analyze_job_description",
    "analyze_job_profiles",
]

T = TypeVar("T", bound=BaseModel)

litellm.drop_params = True
log = logging.getLogger(__name__)


# ==========================================
# 0. 运行时模型配置（不依赖 config 顶层导入）
# ==========================================
@dataclass
class RuntimeLLMModelConfig:
    model_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


def _unwrap_secret(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, SecretStr):
        return value.get_secret_value()
    getter = getattr(value, "get_secret_value", None)
    if callable(getter):
        try:
            return getter()
        except Exception:
            return str(value)
    return str(value)


def _safe_get_settings() -> Any:
    """
    延迟获取 settings。
    若 config.py 在导入时会触发 ValidationError，这里直接吞掉并返回 None，
    避免 import job_profile_builder.py 时就立刻崩溃。
    """
    try:
        import config as config_module
        return getattr(config_module, "settings", None)
    except Exception as e:
        log.warning("延迟加载 config.settings 失败，将改用显式参数 / 环境变量。错误: %s", e)
        return None


def _normalize_model_name(target_model_name: str) -> str:
    if "/" in target_model_name:
        return target_model_name

    provider_map = {
        "qwen": "dashscope",
        "deepseek": "deepseek",
        "gpt-4": "openai",
        "gpt-3.5": "openai",
        "claude": "anthropic",
        "gemini": "gemini",
    }
    lower_name = target_model_name.lower()
    for prefix, provider in provider_map.items():
        if lower_name.startswith(prefix):
            return f"{provider}/{target_model_name}"
    return target_model_name


def _resolve_default_model_name() -> str:
    settings = _safe_get_settings()
    if settings is not None:
        try:
            model_name = getattr(getattr(settings, "vector", None), "llm_long_model_name", None)
            if isinstance(model_name, str) and model_name.strip():
                return _normalize_model_name(model_name)

            llm_long_model = getattr(getattr(settings, "llm", None), "llm_long_model_name", None)
            model_name = getattr(llm_long_model, "model_name", None)
            if isinstance(model_name, str) and model_name.strip():
                return _normalize_model_name(model_name)
        except Exception as e:
            log.warning("从 settings 获取默认 model_name 失败，将继续尝试环境变量。错误: %s", e)

    env_model = (
        os.getenv("LLM_MODEL_NAME")
        or os.getenv("OPENAI_MODEL")
        or os.getenv("DASHSCOPE_MODEL")
        or os.getenv("MODEL_NAME")
    )
    if env_model:
        return _normalize_model_name(env_model)

    return "dashscope/qwen-plus-latest"


def _resolve_default_api_key() -> Optional[str]:
    settings = _safe_get_settings()
    if settings is not None:
        try:
            llm = getattr(settings, "llm", None)
            if llm is not None:
                for attr_name in ("api_key", "llm_api_key"):
                    value = getattr(llm, attr_name, None)
                    unwrapped = _unwrap_secret(value)
                    if unwrapped:
                        return unwrapped
        except Exception as e:
            log.warning("从 settings 获取默认 api_key 失败，将继续尝试环境变量。错误: %s", e)

    for env_name in (
        "OPENAI_API_KEY",
        "DASHSCOPE_API_KEY",
        "DEEPSEEK_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "LLM_API_KEY",
    ):
        value = os.getenv(env_name)
        if value:
            return value

    return None


def _resolve_default_api_base() -> Optional[str]:
    settings = _safe_get_settings()
    if settings is not None:
        try:
            llm = getattr(settings, "llm", None)
            if llm is not None:
                for attr_name in ("base_url", "api_base"):
                    value = getattr(llm, attr_name, None)
                    if value:
                        return str(value)

                llm_long_model = getattr(llm, "llm_long_model_name", None)
                api_base = getattr(llm_long_model, "api_base", None)
                if api_base:
                    return str(api_base)
        except Exception as e:
            log.warning("从 settings 获取默认 api_base 失败，将继续尝试环境变量。错误: %s", e)

    return os.getenv("OPENAI_BASE_URL") or os.getenv("LLM_API_BASE") or os.getenv("API_BASE")


def _coerce_model_config(
    model: Any,
    fallback_api_key: Optional[str] = None,
    fallback_api_base: Optional[str] = None,
) -> RuntimeLLMModelConfig:
    """
    把外部传入的 model（可能是 dict / Pydantic 模型 / 自定义配置对象）
    统一转成 RuntimeLLMModelConfig。
    """
    if isinstance(model, RuntimeLLMModelConfig):
        return model

    if model is None:
        raise ValueError("model 不能为空")

    if isinstance(model, str):
        return RuntimeLLMModelConfig(
            model_name=_normalize_model_name(model),
            api_key=fallback_api_key or _resolve_default_api_key(),
            api_base=fallback_api_base or _resolve_default_api_base(),
        )

    if isinstance(model, dict):
        model_name = model.get("model_name") or model.get("model")
        if not model_name:
            raise ValueError("model 配置中缺少 model_name/model 字段")

        api_key = _unwrap_secret(model.get("api_key")) or fallback_api_key or _resolve_default_api_key()
        api_base = model.get("api_base") or model.get("base_url") or fallback_api_base or _resolve_default_api_base()

        extra = {
            k: v for k, v in model.items()
            if k not in {"model_name", "model", "api_key", "api_base", "base_url"}
        }
        return RuntimeLLMModelConfig(
            model_name=_normalize_model_name(str(model_name)),
            api_key=api_key,
            api_base=api_base,
            extra=extra,
        )

    model_name = getattr(model, "model_name", None) or getattr(model, "model", None)
    if not model_name:
        raise ValueError(f"无法从 model 对象中提取 model_name，收到类型: {type(model).__name__}")

    api_key = (
        _unwrap_secret(getattr(model, "api_key", None))
        or fallback_api_key
        or _resolve_default_api_key()
    )
    api_base = (
        getattr(model, "api_base", None)
        or getattr(model, "base_url", None)
        or fallback_api_base
        or _resolve_default_api_base()
    )

    extra: Dict[str, Any] = {}
    for key in ("timeout", "max_tokens", "top_p", "frequency_penalty", "presence_penalty"):
        value = getattr(model, key, None)
        if value is not None:
            extra[key] = value

    return RuntimeLLMModelConfig(
        model_name=_normalize_model_name(str(model_name)),
        api_key=api_key,
        api_base=str(api_base) if api_base else None,
        extra=extra,
    )


def _create_model_config_from_name(
    target_model_name: str,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
) -> RuntimeLLMModelConfig:
    """
    根据模型名称字符串动态创建运行时模型配置对象。
    不在模块顶层导入 config，彻底避免 import 即触发 Settings 校验。
    """
    return RuntimeLLMModelConfig(
        model_name=_normalize_model_name(target_model_name),
        api_key=api_key or _resolve_default_api_key(),
        api_base=api_base or _resolve_default_api_base(),
    )


# ==========================================
# 1. Prompt 模板
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
2. 命名格式必须严格统一为：职级-领域-职称
3. 例如：
   - 初级后端开发工程师
   - 中级新媒体运营专员
   - 高级招聘配置经理
4. 若无法明确判断职级，可使用更稳妥的通用表达，但仍需保持“职级-领域-职称”格式。
5. 不能含有五险一金、股权激励，全国有岗位、周末双休这类无实际意义的描述性词汇。
6. 不能含有符号，如“/”、“&”、“-”、“、”等。

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
不要输出解释说明，不要输出 Markdown，只返回符合 JDAnalysisResult 结构的 JSON 对象。

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
# 2. 结果修正与输入构建辅助函数
# ==========================================
def fix_llm_json_keys(data: dict) -> dict:
    """
    修复 LLM 返回的 JSON 中的键名不匹配问题 + 空数组兜底
    """
    if not isinstance(data, dict):
        return data

    if "profiles" in data and isinstance(data["profiles"], dict):
        profiles = data["profiles"]

        if "职业技能" in profiles and isinstance(profiles["职业技能"], dict):
            skills = profiles["职业技能"]
            if "行业 Domain 知识" in skills and "行业_Domain_知识" not in skills:
                skills["行业_Domain_知识"] = skills.pop("行业 Domain 知识")

        array_field_mapping = {
            "基础要求": ["证书要求"],
            "职业技能": ["核心专业技能", "工具与平台能力", "语言能力"],
            "岗位属性": ["横向转岗方向"],
        }

        for parent, fields in array_field_mapping.items():
            if parent in profiles and isinstance(profiles[parent], dict):
                for field_name in fields:
                    if field_name in profiles[parent] and profiles[parent][field_name] == []:
                        profiles[parent][field_name] = ["未提及"]

    return data


def _build_jd_text(jobs: List[Any]) -> str:
    """
    构建发送给 LLM 的 JD 文本
    直接将传入的所有对象/数据转为字符串拼接，不手动提取特定字段
    """
    if not jobs:
        raise ValueError("jobs 不能为空")

    separator = ""
    return separator.join(str(job.to_json()) for job in jobs)


# ==========================================
# 3. 轻量级本地 AIEngine（不依赖外部 ai_engine.py）
# ==========================================
@dataclass
class _PipelineState:
    model: RuntimeLLMModelConfig
    model_fallbacks: List[RuntimeLLMModelConfig] = field(default_factory=list)
    system_role: Optional[str] = None
    instructions: List[str] = field(default_factory=list)
    user_texts: List[str] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)
    llm_params: Dict[str, Any] = field(default_factory=dict)

    def clone(self) -> "_PipelineState":
        return _PipelineState(
            model=self.model,
            model_fallbacks=list(self.model_fallbacks),
            system_role=self.system_role,
            instructions=list(self.instructions),
            user_texts=list(self.user_texts),
            history=[dict(item) for item in self.history],
            llm_params=dict(self.llm_params),
        )

    def compile_messages(self) -> List[Dict[str, Any]]:
        messages: List[Dict[str, Any]] = []

        if self.system_role:
            messages.append({"role": "system", "content": self.system_role})

        for item in self.history:
            role = item.get("role", "user")
            content = item.get("content", "")
            if content:
                messages.append({"role": role, "content": content})

        user_blocks: List[str] = []
        if self.instructions:
            user_blocks.append("任务要求：\n" + "\n".join(self.instructions))
        if self.user_texts:
            user_blocks.append("\n\n".join(self.user_texts))

        if user_blocks:
            messages.append({"role": "user", "content": "\n\n".join(user_blocks)})

        return messages

    def to_litellm_params(self, model_cfg: RuntimeLLMModelConfig) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "model": model_cfg.model_name,
            **self.llm_params,
        }

        if model_cfg.api_key:
            params["api_key"] = model_cfg.api_key
        if model_cfg.api_base:
            params["api_base"] = model_cfg.api_base

        if model_cfg.extra:
            for key, value in model_cfg.extra.items():
                if value is not None and key not in params:
                    params[key] = value

        return params


class BaseStep:
    def __init__(self, state: _PipelineState, engine: "JobProfileAIEngine") -> None:
        self._state = state
        self._engine = engine

    def _clone_state(self) -> _PipelineState:
        return self._state.clone()

    def _ensure_has_input(self) -> None:
        has_input = bool(self._state.instructions or self._state.user_texts or self._state.history)
        if not has_input:
            raise ValueError("必须至少注入 指令、文本 或 历史记录 中的一项")


class StructActionStep(Generic[T], BaseStep):
    def __init__(self, state: _PipelineState, engine: "JobProfileAIEngine", schema: Type[T]) -> None:
        super().__init__(state, engine)
        self.schema = schema

    async def do(self) -> T:
        messages = self._state.compile_messages()
        if not messages:
            raise ValueError("没有可发送给 LLM 的消息内容")

        candidates = [self._state.model, *self._state.model_fallbacks]
        last_error: Optional[Exception] = None

        for idx, model_cfg in enumerate(candidates, start=1):
            try:
                kwargs = self._state.to_litellm_params(model_cfg)
                kwargs["messages"] = messages
                kwargs["response_model"] = self.schema

                log.info(
                    "[结构化提取] 开始执行 | 第 %s 个模型 | model=%s | schema=%s",
                    idx,
                    model_cfg.model_name,
                    self.schema.__name__,
                )

                result = await self._engine.struct_client.chat.completions.create(**kwargs)
                log.info("[结构化提取] 执行成功 | model=%s | schema=%s", model_cfg.model_name, self.schema.__name__)
                return result
            except Exception as e:
                last_error = e
                log.warning(
                    "[结构化提取] 模型调用失败，尝试下一个候选 | model=%s | schema=%s | error=%s",
                    model_cfg.model_name,
                    self.schema.__name__,
                    e,
                )

        raise RuntimeError(f"结构化提取失败，所有模型均调用失败。最后错误: {last_error}")


class TextActionStep(BaseStep):
    async def do(self) -> str:
        messages = self._state.compile_messages()
        if not messages:
            raise ValueError("没有可发送给 LLM 的消息内容")

        candidates = [self._state.model, *self._state.model_fallbacks]
        last_error: Optional[Exception] = None

        for idx, model_cfg in enumerate(candidates, start=1):
            try:
                kwargs = self._state.to_litellm_params(model_cfg)
                kwargs["messages"] = messages

                log.info("[文本生成] 开始执行 | 第 %s 个模型 | model=%s", idx, model_cfg.model_name)
                response = await self._engine.text_client(**kwargs)
                content = response.choices[0].message.content
                result = content if content else "没有返回任何内容。"
                log.info("[文本生成] 执行成功 | model=%s", model_cfg.model_name)
                return result
            except Exception as e:
                last_error = e
                log.warning("[文本生成] 模型调用失败，尝试下一个候选 | model=%s | error=%s", model_cfg.model_name, e)

        raise RuntimeError(f"文本生成失败，所有模型均调用失败。最后错误: {last_error}")

    async def stream(self) -> AsyncIterable[str]:
        messages = self._state.compile_messages()
        if not messages:
            raise ValueError("没有可发送给 LLM 的消息内容")

        candidates = [self._state.model, *self._state.model_fallbacks]
        last_error: Optional[Exception] = None

        for idx, model_cfg in enumerate(candidates, start=1):
            try:
                kwargs = self._state.to_litellm_params(model_cfg)
                kwargs["messages"] = messages
                kwargs["stream"] = True

                log.info("[流式生成] 开始执行 | 第 %s 个模型 | model=%s", idx, model_cfg.model_name)
                response = await self._engine.text_client(**kwargs)

                async for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content

                log.info("[流式生成] 执行成功 | model=%s", model_cfg.model_name)
                return
            except Exception as e:
                last_error = e
                log.warning("[流式生成] 模型调用失败，尝试下一个候选 | model=%s | error=%s", model_cfg.model_name, e)

        raise RuntimeError(f"流式生成失败，所有模型均调用失败。最后错误: {last_error}")


class InputStep(BaseStep):
    """
    统一链式入口：
    支持直接写成：
    llm.set_system_role(...).add_text(...).set_llm_params(...).into_struct(...).do()
    """

    def set_system_role(self, role: str) -> "InputStep":
        state = self._clone_state()
        state.system_role = role
        return InputStep(state, self._engine)

    def add_instruction(self, task: str) -> "InputStep":
        state = self._clone_state()
        state.instructions.append(task)
        return InputStep(state, self._engine)

    def add_text(self, text: str) -> "InputStep":
        state = self._clone_state()
        state.user_texts.append(text)
        return InputStep(state, self._engine)

    def set_history(self, history: List[Dict[str, Any]]) -> "InputStep":
        state = self._clone_state()
        state.history = list(history)
        return InputStep(state, self._engine)

    def add_history_message(self, role: str, content: str) -> "InputStep":
        state = self._clone_state()
        state.history.append({"role": role, "content": content})
        return InputStep(state, self._engine)

    def set_llm_params(self, **params: Any) -> "InputStep":
        state = self._clone_state()
        state.llm_params.update(params)
        return InputStep(state, self._engine)

    def into_struct(self, schema: Type[T]) -> StructActionStep[T]:
        self._ensure_has_input()
        state = self._clone_state()
        state.llm_params.setdefault("temperature", 0.1)
        return StructActionStep(state, self._engine, schema)

    def into_text(self) -> TextActionStep:
        self._ensure_has_input()
        return TextActionStep(self._state, self._engine)

    def next_step(self) -> "InputStep":
        """
        为兼容旧代码保留，但现在不是必须的。
        """
        self._ensure_has_input()
        return self


class TuneStep(InputStep):
    """
    兼容旧导出名保留。
    """
    pass


class ShapeStep(InputStep):
    """
    兼容旧导出名保留。
    """
    pass


class JobProfileAIEngine:
    """
    岗位画像专用轻量 AI 引擎。
    保留链式调用能力，但外部调用已简化为：
    llm.set_system_role(...).add_text(...).set_llm_params(...).into_struct(...).do()
    """
    _converter = instructor.from_litellm(litellm.acompletion, mode=instructor.Mode.MD_JSON)

    def __init__(self) -> None:
        self.struct_client = self._converter
        self.text_client = litellm.acompletion

    def pick_brain(
        self,
        model: Any,
        model_fallbacks: Optional[List[Any]] = None,
    ) -> InputStep:
        main_model = _coerce_model_config(model)
        fallback_models = [_coerce_model_config(item) for item in (model_fallbacks or [])]

        state = _PipelineState(
            model=main_model,
            model_fallbacks=fallback_models,
        )
        return InputStep(state, self)


# ==========================================
# 4. JobProfileBuilder
# ==========================================
class JobProfileBuilder:
    """
    岗位画像构建器

    设计目标：
    1. 对外语义聚焦“岗位画像构建”
    2. 对内提供链式分段调用能力
    3. 支持两种用法：
       - 手动链式调用：
         builder.pick_brain(...).set_system_role(...).add_text(...).into_struct(...).do()
       - 直接业务调用：
         await builder.build_jd_result(...), await builder.build_profiles(...)
    """

    def __init__(
        self,
        system_prompt: str = FULL_SYSTEM_PROMPT,
        instruction_prompt: str = USER_PROMPT,
        engine: Optional[JobProfileAIEngine] = None,
    ) -> None:
        self.system_prompt = system_prompt
        self.instruction_prompt = instruction_prompt
        self._engine = engine or JobProfileAIEngine()

    def pick_brain(
        self,
        model: Any,
        model_fallbacks: Optional[List[Any]] = None,
    ) -> InputStep:
        return self._engine.pick_brain(model, model_fallbacks)

    def from_text(
        self,
        text: str,
        model: Any,
        model_fallbacks: Optional[List[Any]] = None,
        system_prompt: Optional[str] = None,
        instruction_prompt: Optional[str] = None,
    ) -> InputStep:
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
        jobs: List[Any],
        model: Any,
        model_fallbacks: Optional[List[Any]] = None,
        system_prompt: Optional[str] = None,
        instruction_prompt: Optional[str] = None,
    ) -> InputStep:
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
        jobs: Optional[List[Any]] = None,
        text: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        api_base: Optional[str] = None,
        temperature: float = 0.1,
        max_retries: int = 3,
        model_fallbacks: Optional[List[Any]] = None,
        system_prompt: Optional[str] = None,
        instruction_prompt: Optional[str] = None,
    ) -> T:
        if not text and not jobs:
            raise ValueError("text 和 jobs 至少传一个")

        payload_text = text if text else _build_jd_text(jobs or [])

        resolved_model_name = model_name or _resolve_default_model_name()
        resolved_api_key = api_key or _resolve_default_api_key()
        resolved_api_base = api_base or _resolve_default_api_base()

        if not resolved_api_key:
            raise ValueError(
                "未能获取可用的 api_key。"
                "请显式传入 api_key，或修复 config/settings 配置，或设置环境变量（如 DASHSCOPE_API_KEY / OPENAI_API_KEY）。"
            )

        model_config = _create_model_config_from_name(
            target_model_name=resolved_model_name,
            api_key=resolved_api_key,
            api_base=resolved_api_base,
        )

        normalized_fallbacks = None
        if model_fallbacks:
            normalized_fallbacks = [
                _coerce_model_config(item, fallback_api_key=resolved_api_key, fallback_api_base=resolved_api_base)
                for item in model_fallbacks
            ]

        for attempt in range(max_retries):
            try:
                pipeline = self.from_text(
                    text=payload_text,
                    model=model_config,
                    model_fallbacks=normalized_fallbacks,
                    system_prompt=system_prompt,
                    instruction_prompt=instruction_prompt,
                )

                result = await (
                    pipeline
                    .set_llm_params(temperature=temperature)
                    .into_struct(schema)
                    .do()
                )

                if result is None:
                    raise ValueError("LLM 返回为空")

                log.info("岗位画像构建成功 | schema=%s", schema.__name__)
                return result

            except Exception as e:
                if attempt >= max_retries - 1:
                    log.error(
                        "岗位画像构建失败（重试耗尽）| schema=%s | error=%s",
                        schema.__name__,
                        e,
                        exc_info=True,
                    )
                    raise

                wait_time = (attempt + 1) * 2 + random.uniform(0, 1)
                log.warning(
                    "岗位画像构建失败，%.2f 秒后重试 (%s/%s) | schema=%s | error=%s",
                    wait_time,
                    attempt + 1,
                    max_retries,
                    schema.__name__,
                    e,
                )
                await asyncio.sleep(wait_time)

        raise RuntimeError("岗位画像构建失败：超过最大重试次数")

    async def build_jd_result(
        self,
        *,
        jobs: Optional[List[Any]] = None,
        text: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        api_base: Optional[str] = None,
        temperature: float = 0.1,
        max_retries: int = 3,
        model_fallbacks: Optional[List[Any]] = None,
    ) -> JDAnalysisResult:
        result = await self.build_struct(
            schema=JDAnalysisResult,
            jobs=jobs,
            text=text,
            api_key=api_key,
            model_name=model_name,
            api_base=api_base,
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
        jobs: Optional[List[Any]] = None,
        text: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        api_base: Optional[str] = None,
        temperature: float = 0.1,
        max_retries: int = 3,
        model_fallbacks: Optional[List[Any]] = None,
    ) -> Profiles:
        result = await self.build_struct(
            schema=Profiles,
            jobs=jobs,
            text=text,
            api_key=api_key,
            model_name=model_name,
            api_base=api_base,
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
    model_name: Optional[str] = None,
    api_base: Optional[str] = None,
) -> dict:
    """
    兼容旧调用方式：返回完整 JDAnalysisResult 的 dict
    """
    builder = JobProfileBuilder()
    result = await builder.build_jd_result(
        jobs=jobs,
        api_key=api_key,
        model_name=model_name,
        api_base=api_base,
    )
    return json.loads(result.model_dump_json(by_alias=True))


async def analyze_job_profiles(
    jobs: List[JobInfo],
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    api_base: Optional[str] = None,
) -> dict:
    """
    返回纯 Profiles 的 dict
    直接采用链式模式：
    await (
        builder
        .pick_brain(model_config)
        .set_system_role(PROFILE_SYSTEM_PROMPT)
        .add_instruction("请提取岗位画像主体，只返回 Profiles 对象")
        .add_text(jd_text)
        .set_llm_params(temperature=0.1)
        .into_struct(Profiles)
        .do()
    )
    """
    if not jobs:
        raise ValueError("jobs 不能为空")

    builder = JobProfileBuilder()
    jd_text = _build_jd_text(jobs)
    # print(jd_text)

    resolved_model_name = model_name or _resolve_default_model_name()
    resolved_api_key = api_key or _resolve_default_api_key()
    resolved_api_base = api_base or _resolve_default_api_base()

    if not resolved_api_key:
        raise ValueError(
            "未能获取可用的 api_key。"
            "请显式传入 api_key，或修复 config/settings 配置，或设置环境变量（如 DASHSCOPE_API_KEY / OPENAI_API_KEY）。"
        )

    model_config = _create_model_config_from_name(
        target_model_name=resolved_model_name,
        api_key=_resolve_default_api_key(),
        api_base=resolved_api_base,
    )

    result = await (
                builder
                .pick_brain(model_config)
                .set_system_role(PROFILE_SYSTEM_PROMPT)
                .add_instruction("请提取岗位画像主体，只返回 JDAnalysisResult 对象")
                .add_text(jd_text)
                .set_llm_params(temperature=0.1)
                .into_struct(JDAnalysisResult)
                .do()
            )

    return result.model_dump()

# async def analyze_job_profiles(
#     jobs: List[Any],
#     api_key: Optional[str] = None,
#     model_name: Optional[str] = None,
#     api_base: Optional[str] = None,
# ) -> dict:
#     """
#     返回纯 Profiles 的 dict
#     """
#     builder = JobProfileBuilder()
#     result = await builder.build_profiles(
#         jobs=jobs,
#         api_key=api_key,
#         model_name=model_name,
#         api_base=api_base,
#     )
#     return json.loads(result.model_dump_json(by_alias=True))


# ==========================================
# 6. 测试入口
# ==========================================
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s"
    )

    async def main() -> None:
        from config import settings
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
        from ai_service.repository.job_info_repository import JobRepository

        DB_URL = (
            f"mysql+aiomysql://{settings.database.user}:{settings.database.password}"
            f"@{settings.database.host}:{settings.database.port}/{settings.database.database}"
            f"?charset=utf8mb4"
        )
        engine = create_async_engine(DB_URL, echo=False)
        AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with AsyncSessionLocal() as session:
            job_repo = JobRepository(session)
            job_list = await job_repo.get_by_id(1)

        try:
            result1 = await analyze_job_profiles(
                [job_list]
            )
        except Exception as e:
            print("异常类型:", type(e).__name__)
            print("异常内容:", repr(e))
            traceback.print_exc()
            raise

        print("=== result1: Profiles ===")
        print(result1)

    asyncio.run(main())