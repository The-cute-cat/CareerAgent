import base64
from typing import List, Tuple, Optional

import pymupdf

from langchain_core.messages import HumanMessage
from openai import OpenAI

from ai_service.models.pdf import PDFType
from ai_service.services.prompt_loader import prompt_loader
from ai_service.utils.logger_handler import log

__all__ = ["pdf_extractor"]

from config import settings


class PDFExtractor:

    def __init__(self):

        self.llm = OpenAI(
            api_key=settings.llm.api_key.get_secret_value(),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            timeout=settings.llm.timeout,
            max_retries=settings.llm.max_retries,
        )

    @staticmethod
    def detect_pdf_type(
            pdf_path: str,
            min_chars_per_page: int = 50,
            password: str = ""
    ) -> Tuple[PDFType, dict]:
        try:
            try:
                doc = pymupdf.open(pdf_path)
            except Exception as e:
                log.error(f"Failed to open PDF file: {pdf_path}，error: {e}", exc_info=True)
                return PDFType.UNKNOWN, {}
            info = {
                "total_pages": len(doc),
                "text_count": 0,
                "scanned_count": 0,
                "encrypted": False,
                "has_images": False,
                "total_chars": 0,
                "text_page_list": [],
                "scanned_page_list": []
            }
            if doc.is_encrypted:
                info["encrypted"] = True
                if not doc.authenticate(password):
                    log.warning(f"PDF file is encrypted and password is incorrect: {pdf_path}，password: {password}")
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

                if has_images == 0 or char_count >= min_chars_per_page:
                    info["text_count"] += 1
                    info["total_chars"] += char_count
                    info["text_page_list"].append(page_num)
                else:
                    info["scanned_count"] += 1
                    info["scanned_page_list"].append(page_num)
                    if has_images:
                        info["has_images"] = True

            doc.close()

            if info["text_count"] == info["total_pages"]:
                return PDFType.TEXT_BASED, info
            elif info["scanned_count"] == info["total_pages"]:
                return PDFType.SCANNED, info
            else:
                return PDFType.MIXED, info
        except Exception as e:
            log.error(f"Failed to detect PDF type: {pdf_path}，error: {e}", exc_info=True)
            return PDFType.UNKNOWN, {}

    @staticmethod
    def get_text_pdf(pdf_path: str, password: Optional[str] = None) -> List[str] | None:
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
    def get_scanned_pdf(pdf_path: str, password: Optional[str] = None) -> List[str] | None:
        try:
            doc = pymupdf.open(pdf_path)
            if doc.is_encrypted:
                if not password or not doc.authenticate(password):  # authenticate如果解密成功，doc就是一个解密后的文档对象，返回一个不等于0的值
                    doc.close()
                    log.warning(f"PDF file is encrypted and password is incorrect: {pdf_path}，password: {password}")
                    return None

        except Exception as e:
            log.error(f"Failed to get scanned image from PDF file: {pdf_path}，error: {e}", exc_info=True)

    @staticmethod
    def _image_to_base64(image_bytes: bytes) -> str:
        """图片转 Base64"""
        return base64.b64encode(image_bytes).decode("utf-8")

    def _extract_page_content(self, image_bytes: bytes) -> str | None:
        raise Exception("正在开发中")
        """识别单页图片的内容"""
        prompt = prompt_loader.pdf_recognition
        base64_image = self._image_to_base64(image_bytes)
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ]
        )
        response = self.llm.invoke([message])
        print(response)
        return response.content


pdf_extractor = PDFExtractor()

if __name__ == '__main__':
    # test_pdf_path = r"C:\Users\The_cute_cat\Desktop\Java程序设计报告.pdf"
    # print(pdf_extractor.detect_pdf_type(test_pdf_path))
    # image_path = r"C:\Users\The_cute_cat\Desktop\1.jpg"
    # with open(image_path, "rb") as f:
    #     image_bytes = f.read()
    # print(pdf_extractor._extract_page_content(image_bytes))
    ...
