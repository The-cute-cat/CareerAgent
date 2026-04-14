from __future__ import annotations

from typing import List, Optional

from ai_service.engine.ai_engine import AIEngine, InputStep
from ai_service.models.job_info import JobInfo
from ai_service.models.struct_job_txt import Profiles, JDAnalysisResult

# 这里只导入类型，不导入 settings，避免模块加载即触发配置校验
from config import _LLMModelBase


def build_jd_text(jobs: List[JobInfo]) -> str:
    """
    将 JobInfo 列表拼成适合送入 LLM 的 JD 文本
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


class JobProfileAIEngine:
    """
    岗位画像专用 AIEngine 包装器
    作用：
    1. 保留原 AIEngine 的五阶段链式调用
    2. 增加 from_text / from_jobs 的岗位画像快捷入口
    """

    def __init__(
        self,
        system_prompt: str,
        instruction_prompt: str,
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
        return self._engine.pick_brain(model, model_fallbacks)

    def from_text(
        self,
        text: str,
        model: _LLMModelBase,
        model_fallbacks: Optional[List[_LLMModelBase]] = None,
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
        jobs: List[JobInfo],
        model: _LLMModelBase,
        model_fallbacks: Optional[List[_LLMModelBase]] = None,
        system_prompt: Optional[str] = None,
        instruction_prompt: Optional[str] = None,
    ) -> InputStep:
        jd_text = build_jd_text(jobs)
        return self.from_text(
            text=jd_text,
            model=model,
            model_fallbacks=model_fallbacks,
            system_prompt=system_prompt,
            instruction_prompt=instruction_prompt,
        )