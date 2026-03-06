"""
PDF 文档提取器模块

支持识别和提取文本型、扫描型和混合型 PDF 文档内容。
扫描型 PDF 使用 LLM 进行 OCR 识别。
"""

import base64
import time
from typing import List, Tuple, Optional, Any, Dict

import pymupdf
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from ai_service.models.pdf import PDFType
from ai_service.services.prompt_loader import prompt_loader
from ai_service.utils.logger_handler import log

__all__ = ["pdf_extractor"]

from config import settings


class PDFExtractor:
    """PDF 文档内容提取器

    根据文档类型采用不同的提取策略：
    - 文本型：直接提取文本内容
    - 扫描型：将页面转为图片，使用 LLM 进行 OCR 识别
    - 混合型：结合上述两种方式
    """

    def __init__(self):

        self.llm = ChatOpenAI(
            api_key=settings.llm.api_key.get_secret_value(),
            base_url=settings.llm.base_url,
            timeout=settings.llm.timeout,
            max_retries=settings.llm.max_retries,
            model=settings.pdf.model_name
        )

    def detect_pdf_type(
            self,
            pdf_path: str,
            min_chars_per_page: int = 50,
            password: str = ""
    ) -> Tuple[PDFType, dict]:
        """检测 PDF 文档类型

        Args:
            pdf_path: PDF 文件路径
            min_chars_per_page: 判定为文本页的最小字符数阈值
            password: 加密 PDF 的密码

        Returns:
            元组 (PDF类型, 文档信息字典)
        """
        try:
            with pymupdf.open(pdf_path) as doc:
                info = {
                    "total_pages": len(doc),
                    "text_count": 0,
                    "scanned_count": 0,
                    "encrypted": doc.is_encrypted,
                    "has_images": False,
                    "total_chars": 0,
                    "text_page_list": [],
                    "scanned_page_list": []
                }
                if not self._try_decrypt_pdf(doc, password):
                    log.warning(f"PDF file is encrypted and password is incorrect: {pdf_path}，password: {password}")
                    return PDFType.ENCRYPTED, info

                if doc.page_count == 0:
                    return PDFType.UNKNOWN, info

                # 逐页分析，统计文本页和扫描页
                total_pages = doc.page_count
                for page_num in range(total_pages):
                    page = doc.load_page(page_num)

                    text = page.get_text()
                    char_count = len(text.strip())
                    images = page.get_images()
                    has_images = len(images) > 0

                    # 无图片或字符数达到阈值，判定为文本页
                    if not has_images or char_count >= min_chars_per_page:
                        info["text_count"] += 1
                        info["total_chars"] += char_count
                        info["text_page_list"].append(page_num)
                    else:
                        # 有图片但字符数不足，判定为扫描页
                        info["scanned_count"] += 1
                        info["scanned_page_list"].append(page_num)
                        if has_images:
                            info["has_images"] = True

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
    def _try_decrypt_pdf(doc: pymupdf.Document, password: str) -> bool:
        """尝试解密 PDF 文档

        Args:
            doc: PyMuPDF 文档对象
            password: 解密密码

        Returns:
            未加密或解密成功返回 True；密码错误返回 False
        """
        if doc.is_encrypted:
            if not doc.authenticate(password):  # authenticate如果解密成功，doc就是一个解密后的文档对象，返回一个不等于0的值
                return False
        return True

    def get_text_pdf(
            self,
            pdf_path: str,
            password: Optional[str] = None,
            text_page_list: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """提取文本型 PDF 内容

        Args:
            pdf_path: PDF 文件路径
            password: 加密 PDF 的密码
            text_page_list: 指定提取的页码列表，为空则提取全部

        Returns:
            页面内容列表，每项包含 page 和 content 字段
        """
        try:
            with pymupdf.open(pdf_path) as doc:
                if not self._try_decrypt_pdf(doc, password):
                    log.warning(f"PDF file is encrypted and password is incorrect: {pdf_path}，password: {password}")
                    return []
                text_list = []
                if text_page_list:
                    page_num_list = text_page_list
                else:
                    page_num_list = range(doc.page_count)
                for page_num in page_num_list:
                    try:
                        page = doc.load_page(page_num)
                        text = page.get_text()
                        if text and text.strip():
                            text_list.append({
                                "page": page_num,
                                "content": text
                            })
                    except Exception as e:
                        log.warning(f"Failed to get text from PDF page: {page_num}, error: {e}")
                        text_list.append({
                            "page": page_num,
                            "content": None,
                            "error": str(e)
                        })
                return text_list
        except Exception as e:
            log.error(f"Failed to get text from PDF file: {pdf_path}，error: {e}", exc_info=True)
            return []

    def get_scanned_pdf(
            self,
            pdf_path: str,
            password: Optional[str] = None,
            scanned_page_list: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """提取扫描型 PDF 内容

        将页面渲染为图片后使用 LLM 进行 OCR 识别。

        Args:
            pdf_path: PDF 文件路径
            password: 加密 PDF 的密码
            scanned_page_list: 指定提取的页码列表，为空则提取全部

        Returns:
            页面内容列表，每项包含 page 和 content 字段
        """
        try:
            with pymupdf.open(pdf_path) as doc:
                result = []
                if not self._try_decrypt_pdf(doc, password):
                    log.warning(f"PDF file is encrypted and password is incorrect: {pdf_path}，password: {password}")
                    return []
                if scanned_page_list:
                    page_num_list = scanned_page_list
                else:
                    page_num_list = range(doc.page_count)
                for page_num in page_num_list:
                    try:
                        page = doc.load_page(page_num)
                        # 设置缩放比例提高图片清晰度
                        mat = pymupdf.Matrix(1.5, 1.5)
                        pix = page.get_pixmap(matrix=mat)
                        img_bytes = pix.tobytes("png")
                        content = self._extract_page_content(img_bytes)
                        result.append({
                            "page": page_num,
                            "content": content
                        })
                    except Exception as e:
                        log.warning(f"Failed to get scanned image from PDF file: {pdf_path}，error: {e}", exc_info=True)
                        result.append({
                            "page": page_num,
                            "content": None,
                            "error": str(e)
                        })
                return result
        except Exception as e:
            log.error(f"Failed to get scanned image from PDF file: {pdf_path}，error: {e}", exc_info=True)
            return []

    def get_mixed_pdf(
            self,
            pdf_path: str,
            text_page_list: List[int],
            scanned_page_list: List[int],
            password: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """提取混合型 PDF 内容

        对文本页直接提取文本，对扫描页使用 LLM 识别。

        Args:
            pdf_path: PDF 文件路径
            text_page_list: 文本页码列表
            scanned_page_list: 扫描页码列表
            password: 加密 PDF 的密码

        Returns:
            页面内容列表
        """
        try:
            result = []
            result.extend(self.get_text_pdf(pdf_path, password, text_page_list))
            result.extend(self.get_scanned_pdf(pdf_path, password, scanned_page_list))
            return result
        except Exception as e:
            log.error(f"Failed to get mixed image from PDF file: {pdf_path}，error: {e}", exc_info=True)
            return []

    @staticmethod
    def _image_to_base64(image_bytes: bytes) -> str:
        """图片转 Base64"""
        return base64.b64encode(image_bytes).decode("utf-8")

    def _extract_page_content(self, image_bytes: bytes) -> str | None:
        """识别单页图片的内容"""
        start_time = time.time()
        prompt = prompt_loader.pdf_recognition
        base64_image = self._image_to_base64(image_bytes)
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ]
        )
        try:
            response = self.llm.invoke([message])
            end_time = time.time()
            log.info(f"耗时: {end_time - start_time}秒；response_metadata:{response.response_metadata}")
            return response.content
        except Exception as e:
            log.warning(f"Failed to extract page content: {e}", exc_info=True)
            return None


pdf_extractor = PDFExtractor()

if __name__ == '__main__':
    test_pdf_path = r"D:\code\web\CareerAgent\career-planning-ai\src\ai_service\temp\data\test2.pdf"
    # print(pdf_extractor.detect_pdf_type(test_pdf_path))
    print(pdf_extractor.get_scanned_pdf(test_pdf_path))
    ...