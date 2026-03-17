from ai_service.schemas.struct_txt import StudentProfile
from pydantic import BaseModel
from typing import Optional
from config import settings
from ai_service.engine.ai_engine import AIEngine
from ai_service.utils.logger_handler import log


class StructTextExtractor:
    def __init__(self):
        self.llm = AIEngine().pick_brain(settings.llm)

    async def extract_from_text(self, text: str) -> Optional[StudentProfile]:
        response = await self.llm.set_system_role("你是一个专业的学生信息提取助手").add_text(text) \
                .next_step().set_llm_params(temperature=0.1) \
                .next_step() \
                .into_struct(StudentProfile) \
                .do()
        if response is None:
            log.error(f"在{__name__}中提取学生信息失败: {text}")
            return None

        return response
