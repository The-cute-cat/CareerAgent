import json
from typing import Any
from ai_service.prompts.struct_prompt import struct_prompt, system_role
from ai_service.models.userform import UserForm
from ai_service.engine.ai_engine import AIEngine
from ai_service.models.struct_txt import StudentProfile
from ai_service.models.userform_profile import StudentFormProfile
from ai_service.services import log
from ai_service.services.major_aliger import major_aligner
from config import settings

__all__ = [
    "struct_text_extractor",
]


class StructTextExtractor:
    def __init__(self):
        self.llm = AIEngine().pick_brain(settings.lite_llm)

    async def extract_from_userform_to_userprofile(self, user_form: UserForm) -> Any:
        text = user_form.to_llm_context()  # 将用户表单转换为文本
        response = await self.llm.set_system_role(system_role) \
            .add_instruction(struct_prompt) \
            .add_text(text) \
            .next_step().set_llm_params(temperature=0.1) \
            .next_step() \
            .into_struct(StudentProfile) \
            .do()
        if response is None:
            log.error(f"在{__name__}中提取学生信息失败: {text}")
            return None
        return json.loads(response.model_dump_json(by_alias=True))

    async def extract_from_text_to_userform(self, text: str) -> Any:
        response = await self.llm.set_system_role(system_role) \
            .add_instruction(struct_prompt) \
            .add_text(text) \
            .next_step().set_llm_params(temperature=0.1) \
            .next_step() \
            .into_struct(StudentFormProfile) \
            .do()
        if response is None:
            log.error(f"在{__name__}中提取学生信息失败: {text}")
            return None

        # 对 major 进行标准化处理
        return json.loads(response.model_dump_json(by_alias=True))


struct_text_extractor = StructTextExtractor()
