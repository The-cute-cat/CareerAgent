import json
from typing import Any, TypeVar
from pydantic import BaseModel
from ai_service.engine.ai_engine import AIEngine
from ai_service.models.struct_txt import StudentProfile
from ai_service.models.user_form import UserForm
from ai_service.models.user_form_profile import StudentFormProfile
from ai_service.services import log
from ai_service.scripts.py.major_aliger import major_aligner
from ai_service.services.prompt_loader import prompt_loader
from config import settings

__all__ = [
    "struct_text_extractor",
]

T = TypeVar("T", bound=BaseModel)


class StructTextExtractor:
    def __init__(self):
        self.llm = AIEngine().pick_brain(settings.lite_llm)

    async def extract_from_user_form_to_userprofile(self, user_form: UserForm) -> Any:
        text = user_form.to_llm_context()  # 将用户表单转换为文本
        # noinspection DuplicatedCode
        response = await self.llm.set_system_role(prompt_loader.small_prompts["system_role"]) \
            .add_instruction(prompt_loader.small_prompts["struct_prompt"]) \
            .add_text(text) \
            .next_step().set_llm_params(temperature=0.1) \
            .next_step() \
            .into_struct(StudentProfile) \
            .do()
        if response is None:
            log.error(f"在{__name__}中提取学生信息失败: {text}")
            return None

        return json.loads(response.model_dump_json(by_alias=True))

    async def extract_from_text_to_user_form(self, text: str) -> Any:
        # noinspection DuplicatedCode
        response = await self.llm.set_system_role(prompt_loader.small_prompts["system_role"]) \
            .add_instruction(prompt_loader.small_prompts["struct_prompt"]) \
            .add_text(text) \
            .next_step().set_llm_params(temperature=0.1) \
            .next_step() \
            .into_struct(StudentFormProfile) \
            .do()
        if response is None:
            log.error(f"在{__name__}中提取学生信息失败: {text}")
            return None
        # 对 major 进行标准化处理
        if response.major:
            response.major = major_aligner.align_list(response.major)
        return json.loads(response.model_dump_json(by_alias=True))

    async def extract_from_text_to_struct(self, text: str, struct_type: type[T]) -> Any:
        # noinspection DuplicatedCode
        response = await self.llm.set_system_role(prompt_loader.small_prompts["system_role"]) \
            .add_instruction(prompt_loader.small_prompts["struct_prompt"]) \
            .add_text(text) \
            .next_step().set_llm_params(temperature=0.1) \
            .next_step() \
            .into_struct(struct_type) \
            .do()
        if response is None:
            log.error(f"在{__name__}中提取信息失败: {text}")
            return None
        return json.loads(response.model_dump_json(by_alias=True))


struct_text_extractor = StructTextExtractor()
