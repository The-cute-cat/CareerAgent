from ai_service.services.struct_text_extractor import StructTextExtractor
from ai_service.services.pdf_extractor import PDFExtractor
from ai_service.services.word_extractor import WordExtractor
from typing import Optional
from ai_service.utils.logger_handler import log

__all__ = ["DocumentAnalysisService"]


class DocumentAnalysisService:

    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.word_extractor = WordExtractor()
        self.struct_text_extractor = StructTextExtractor()

    async def analyze_pdf(self, file_path: str) -> str:
        pass

    async def analyze_docx(self, file_path: str) -> Optional[str]:
        docx_text = await self.word_extractor.detect_word_to_enhance_text(file_path)
        if not docx_text:
            log.warning(f"No text extracted from docx file: {file_path}")
            return None

        structured_data = await self.struct_text_extractor.extract_from_text_to_json(docx_text)
        if not structured_data:

            log.warning(f"No structured data extracted from docx file: {file_path}")

            return None

        return structured_data

    async def analyze_userform(self, text: str) -> Optional[str]:
        pass

if __name__ == "__main__":

    service = DocumentAnalysisService()

    docx_path = "C:\\Users\\LeJunpeng\\Desktop\\CareerAgent\\CareerAgent\\career-planning-ai\\tests\\2.docx"

    result = asyncio.run(service.analyze_docx(docx_path))

    print(result)