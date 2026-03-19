import json
from typing import Optional, Any

from ai_service.engine.ai_engine import AIEngine
from ai_service.models.struct_txt import StudentProfile
from ai_service.services.major_aliger import major_aligner
from ai_service.models.userform_txt import StudentFormProfile
from ai_service.utils.logger_handler import log
from config import settings

__all__ = [
    "struct_text_extractor",
]


class StructTextExtractor:
    def __init__(self):
        self.llm = AIEngine().pick_brain(settings.lite_llm)

    async def extract_from_text_to_json(self, text: str) -> Any:
        response = await self.llm.set_system_role("你是一个专业的学生信息提取助手").add_text(text) \
            .next_step().set_llm_params(temperature=0.1) \
            .next_step() \
            .into_struct(StudentProfile) \
            .do()
        if response is None:
            log.error(f"在{__name__}中提取学生信息失败: {text}")
            return None
        return json.loads(response.model_dump_json())

    async def extract_from_text_to_userform(self, text: str) -> Any:
        response = await self.llm.set_system_role("你是一个专业的学生信息提取助手").add_text(text) \
            .next_step().set_llm_params(temperature=0.1) \
            .next_step() \
            .into_struct(StudentFormProfile) \
            .do()
        if response is None:
            log.error(f"在{__name__}中提取学生信息失败: {text}")
            return None
        
        # 对 major 进行标准化处理
        response.major = major_aligner.align(response.major)
        return json.loads(response.model_dump_json())



struct_text_extractor = StructTextExtractor()
