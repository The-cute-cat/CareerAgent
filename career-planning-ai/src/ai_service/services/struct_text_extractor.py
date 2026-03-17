from ai_service.models.struct_txt import StudentProfile
from pydantic import BaseModel
from typing import Optional
import asyncio
from config import settings
from ai_service.engine.ai_engine import AIEngine
from ai_service.utils.logger_handler import log


class StructTextExtractor:
    def __init__(self):
        self.llm = AIEngine().pick_brain(settings.llm)

    async def extract_from_text_to_json(self, text: str) -> Optional[str]:
        response = await self.llm.set_system_role("你是一个专业的学生信息提取助手").add_text(text) \
                .next_step().set_llm_params(temperature=0.1) \
                .next_step() \
                .into_struct(StudentProfile) \
                .do()
        if response is None:
            log.error(f"在{__name__}中提取学生信息失败: {text}")
            return None
        return response.model_dump_json()


if __name__ == "__main__":
    extractor = StructTextExtractor()
    sample_text = "姓名：张三，年龄：22岁，专业：计算机科学，兴趣爱好：编程、篮球。"
    result_json = asyncio.run(extractor.extract_from_text_to_json(sample_text))
    print(result_json)