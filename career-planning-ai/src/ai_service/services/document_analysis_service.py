from ai_service.schemas.struct_txt import StudentProfile
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

    async def analyze_pdf(self, file_path: str) -> Optional[StudentProfile]:
        pdf_text = await self.pdf_extractor.extract_text(file_path)
        if not pdf_text:
            log.warning(f"No text extracted from PDF file: {file_path}")
            return None
        structured_data = await self.struct_text_extractor.extract_from_text(pdf_text)
        return structured_data

    async def analyze_docx(self, file_path: str) -> Optional[StudentProfile]:
        docx_text = await self.word_extractor.detect_word_to_enhance_text(file_path)
        if not docx_text:
            log.warning(f"No text extracted from docx file: {file_path}")
            return None

        structured_data = await self.struct_text_extractor.extract_from_text(docx_text)
        return structured_data
