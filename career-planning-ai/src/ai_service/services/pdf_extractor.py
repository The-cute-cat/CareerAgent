from typing import List

import pymupdf

from ai_service.models.pdf import PDFType
from ai_service.utils.logger_handler import log


class PDFExtractor:

    @staticmethod
    def detect_pdf_type(pdf_path: str, password: str = None) -> PDFType:
        try:
            try:
                doc = pymupdf.open(pdf_path)
            except Exception as e:
                log.error(f"Failed to open PDF file: {pdf_path}，error: {e}", exc_info=True)
                return PDFType.UNKNOWN

            if doc.is_encrypted:
                if not password or not doc.authenticate(password):
                    doc.close()
                    return PDFType.ENCRYPTED

            if doc.page_count == 0:
                doc.close()
                return PDFType.UNKNOWN

            has_text_pages = 0
            total_pages = doc.page_count
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text and text.strip():
                    has_text_pages += 1

            doc.close()

            if has_text_pages == 0:
                return PDFType.SCANNED
            elif has_text_pages == total_pages:
                return PDFType.TEXT_BASED
            else:
                return PDFType.MIXED
        except Exception as e:
            log.error(f"Failed to detect PDF type: {pdf_path}，error: {e}", exc_info=True)
            return PDFType.UNKNOWN

    def get_text_pdf(self, pdf_path: str, password: str = None) -> List[str]:

        ...
