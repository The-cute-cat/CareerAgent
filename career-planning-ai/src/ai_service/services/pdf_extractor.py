from typing import List, Tuple

import pymupdf

from ai_service.models.pdf import PDFType
from ai_service.utils.logger_handler import log

__all__ = ["pdf_extractor"]


class PDFExtractor:

    @staticmethod
    def detect_pdf_type(
            pdf_path: str,
            min_chars_per_page: int = 50
    ) -> Tuple[PDFType, dict]:
        try:
            try:
                doc = pymupdf.open(pdf_path)
            except Exception as e:
                log.error(f"Failed to open PDF file: {pdf_path}，error: {e}", exc_info=True)
                return PDFType.UNKNOWN, {}
            info = {
                "total_pages": len(doc),
                "text_pages": 0,
                "scanned_pages": 0,
                "encrypted": False,
                "has_images": False,
                "total_chars": 0
            }
            if doc.is_encrypted:
                info["encrypted"] = True
                if not doc.authenticate(""):
                    doc.close()
                    return PDFType.ENCRYPTED, info

            if doc.page_count == 0:
                doc.close()
                return PDFType.UNKNOWN, info

            total_pages = doc.page_count
            for page_num in range(total_pages):
                page = doc.load_page(page_num)

                text = page.get_text()
                char_count = len(text.strip())
                images = page.get_images()
                has_images = len(images) > 0

                if char_count >= min_chars_per_page:
                    info["text_pages"] += 1
                    info["total_chars"] += char_count
                else:
                    info["scanned_pages"] += 1
                    if has_images:
                        info["has_images"] = True

            doc.close()

            if info["text_pages"] == info["total_pages"]:
                return PDFType.TEXT_BASED, info
            elif info["scanned_pages"] == info["total_pages"]:
                return PDFType.SCANNED, info
            else:
                return PDFType.MIXED, info
        except Exception as e:
            log.error(f"Failed to detect PDF type: {pdf_path}，error: {e}", exc_info=True)
            return PDFType.UNKNOWN, {}

    @staticmethod
    def get_text_pdf(pdf_path: str, password: str = None) -> List[str] | None:
        try:
            doc = pymupdf.open(pdf_path)
            if doc.is_encrypted:
                if not password or not doc.authenticate(password):  # authenticate如果解密成功，doc就是一个解密后的文档对象，返回一个不等于0的值
                    doc.close()
                    log.warning(f"PDF file is encrypted and password is incorrect: {pdf_path}，password: {password}")
                    return None
            text_list = []
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text and text.strip():
                    text_list.append(text)
            doc.close()
            return text_list
        except Exception as e:
            log.error(f"Failed to get text from PDF file: {pdf_path}，error: {e}", exc_info=True)

    @staticmethod
    def get_scanned_pdf(pdf_path: str, password: str = None) -> List[str] | None:
        try:
            doc = pymupdf.open(pdf_path)
            if doc.is_encrypted:
                if not password or not doc.authenticate(password):  # authenticate如果解密成功，doc就是一个解密后的文档对象，返回一个不等于0的值
                    doc.close()
                    log.warning(f"PDF file is encrypted and password is incorrect: {pdf_path}，password: {password}")
                    return None

        except Exception as e:
            log.error(f"Failed to get scanned image from PDF file: {pdf_path}，error: {e}", exc_info=True)

pdf_extractor = PDFExtractor()

if __name__ == '__main__':
    test_pdf_path = r"C:\Users\The_cute_cat\Desktop\Java程序设计报告.pdf"
    print(pdf_extractor.detect_pdf_type(test_pdf_path))
