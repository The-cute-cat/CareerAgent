import os
import zipfile
from typing import Dict

import puremagic
from binaryornot.check import is_binary

from ai_service.utils.logger_handler import log
from ai_service.utils.magic_numbers import (
    FILE_SIGNATURES,
    DANGEROUS_EXTENSIONS,
    SAFE_EXTENSIONS,
    OLE2_SIGNATURES,
    ZIP_SIGNATURES,
)
from ai_service.utils.path_tool import abs_path

__all__ = ["file_detector"]


class FileDetector:
    """
    文件类型检测器

    通过分析文件头部的魔数（Magic Number）识别文件的真实类型，
    而非依赖文件扩展名，可有效防止文件伪装攻击。

    检测策略：
        1. 自定义魔数检测（快速匹配预定义的文件签名）
        2. 文本文件检测（使用 binaryornot 库）
        3. puremagic 检测（第三方库后备方案）

    安全原则：
        - 统一检测流程，所有文件使用相同方法识别真实类型
        - 危险性判断基于检测到的真实扩展名，而非文件名扩展名
        - 检测失败时采用保守策略（视为危险/不安全）

    Attributes:
        magic_detector: puremagic 模块引用，用于后备检测
    """

    def __init__(self):
        """初始化检测器"""
        self.magic_detector = puremagic

    @staticmethod
    def _format_size(size: int) -> str:
        """
        将字节大小格式化为人类可读格式

        Args:
            size: 文件大小（字节）

        Returns:
            格式化后的文件大小字符串，如 "1.50 MB"
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    @staticmethod
    def _check_magic_numbers(file_bytes: bytes, result: Dict[str, str]) -> Dict[str, str] | None:
        try:
            for ext, signature in FILE_SIGNATURES.items():
                for magic_byte in signature.magic_bytes:
                    if file_bytes.startswith(magic_byte):
                        if magic_byte == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
                            result["method"] = "ole2_pending"
                            return result
                        if magic_byte == b"PK\x03\x04":
                            result["method"] = "zip_pending"
                            return result
                        result["description"] = signature.description
                        result["mime_type"] = signature.mime_type
                        result["extension"] = ext
                        result["method"] = "magic_numbers"
                        return result
        except Exception as e:
            log.warning(f"magic_string error: {e}")
            return None

    @staticmethod
    def _check_text_file(file_path: str, result: Dict[str, str]) -> Dict[str, str] | None:
        try:
            if not is_binary(file_path):
                result["mime_type"] = "text/plain"
                result["extension"] = "txt"
                result["description"] = "text file"
                result["method"] = "binaryornot"
                return result
        except Exception as e:
            log.warning(f"is_binary error: {e}")
            return None

    @staticmethod
    def _deep_check_ole2(file_path: str, result: Dict[str, str]) -> Dict[str, str] | None:
        """
        深度检测 OLE2 文件类型（doc/xls/ppt 共享相同魔数）

        通过检查文件内部的结构特征区分具体类型：
        - Excel: 包含 Workbook 或 Book 流
        - Word: 包含 WordDocument 流
        - PowerPoint: 包含 PowerPoint Document 流
        """
        try:
            file_size = os.path.getsize(file_path)
            read_size = min(file_size, 65536)
            with open(file_path, 'rb') as f:
                content = f.read(read_size)

            for sig in OLE2_SIGNATURES.values():
                for marker in sig.markers:
                    if marker in content:
                        result["extension"] = sig.extension
                        result["mime_type"] = sig.mime_type
                        result["description"] = sig.description
                        result["method"] = "ole2_deep"
                        return result
        except Exception as e:
            log.warning(f"OLE2 deep check error: {e}")
        return None

    @staticmethod
    def _deep_check_zip(file_path: str, result: Dict[str, str]) -> Dict[str, str] | None:
        """
        深度检测 ZIP 格式 Office 文件（docx/xlsx/pptx 共享相同魔数）

        通过检查 ZIP 内部文件路径区分具体类型：
        - xlsx: 包含 xl/workbook.xml
        - docx: 包含 word/document.xml
        - pptx: 包含 ppt/presentation.xml
        """
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                names = zf.namelist()

                for sig in ZIP_SIGNATURES.values():
                    for marker in sig.markers:
                        if marker.decode('utf-8') in names:
                            result["extension"] = sig.extension
                            result["mime_type"] = sig.mime_type
                            result["description"] = sig.description
                            result["method"] = "zip_deep"
                            return result
        except Exception as e:
            log.warning(f"ZIP deep check error: {e}")
        return None

    def _check_by_puremagic(self, file_path: str, result: Dict[str, str]) -> Dict[str, str] | None:
        try:
            matches = self.magic_detector.magic_file(file_path)
            result["mime_type"] = matches[0].mime_type
            result["extension"] = matches[0].extension.replace(".", "")
            result["description"] = matches[0].name
            result["method"] = "puremagic"
            return result
        except Exception as e:
            log.warning(f"magic_file error: {e}")
            return None

    def get_file_info(self, filepath: str) -> Dict[str, str]:
        """
        获取文件的类型信息

        使用三级检测策略识别文件类型：
        1. 自定义签名检测：快速匹配预定义的文件魔数
        2. 文本文件检测：识别纯文本文件
        3. puremagic 检测：使用第三方库识别更多格式

        Args:
            filepath: 文件路径

        Returns:
            包含文件类型信息的字典:
            - method: 检测方法，如 "magic_numbers"
            - mime_type: MIME 类型，如 "application/pdf"
            - extension: 文件扩展名，如 "pdf"
            - description: 文件类型描述，如 "Portable Document Format"
            - file_name: 文件名称，如 "example.pdf"
            - size: 文件大小，如 "1.50 MB"

        Raises:
            Exception: 当无法识别文件类型时抛出异常
        """
        result = {
            "method": "",
            "mime_type": "unknown",
            "extension": "unknown",
            "description": "unknown file",
            "file_name": os.path.basename(filepath),
            "size": self._format_size(os.path.getsize(filepath))
        }

        with open(filepath, 'rb') as f:
            file_bytes = f.read(1024)
        temp = self._check_magic_numbers(file_bytes, result)
        if temp:
            if temp.get("method") == "ole2_pending":
                deep_result = self._deep_check_ole2(filepath, result)
                if deep_result:
                    return deep_result
            elif temp.get("method") == "zip_pending":
                deep_result = self._deep_check_zip(filepath, result)
                if deep_result:
                    return deep_result
            else:
                return temp
        temp = self._check_text_file(filepath, result)
        if temp:
            return temp
        temp = self._check_by_puremagic(filepath, result)
        if temp:
            return temp
        raise FileDetectorError(f"未知文件类型: {filepath}")

    def is_dangerous_file(self, filepath: str) -> tuple[bool, Dict[str, str]]:
        """
        检查文件是否属于危险类型

        危险文件包括可执行文件、脚本文件等可能存在安全风险的文件类型。

        Args:
            filepath: 文件路径

        Returns:
            Tuple[bool, Dict[str, str]]

            True 表示危险文件，False 表示非危险文件
            当检测失败时默认返回 True（危险优先原则）

            包含文件类型信息的字典:
                - method: 检测方法，如 "magic_numbers"
                - mime_type: MIME 类型，如 "application/pdf"
                - extension: 文件扩展名，如 "pdf"
                - description: 文件类型描述，如 "Portable Document Format"
                - file_name: 文件名称，如 "example.pdf"
                - size: 文件大小，如 "1.50 MB"
        """
        try:
            file_info = self.get_file_info(filepath)
            log.info(f"文件信息: {file_info}")
            return file_info["extension"] in DANGEROUS_EXTENSIONS, file_info
        except Exception as e:
            log.warning(f"is_dangerous_file error: {e}")
            return True, {}  # 检测失败时保守处理，视为危险文件

    def is_safe_file(self, filepath: str) -> tuple[bool, Dict[str, str]]:
        """
        检查文件是否属于安全类型

        安全文件包括文档、图片、压缩包等允许上传的文件类型。

        Args:
            filepath: 文件路径

        Returns:
            Tuple[bool, Dict[str, str]]

            True 表示安全文件，False 表示非安全文件
            当检测失败时默认返回 False（安全优先原则）

            包含文件类型信息的字典:
                - method: 检测方法，如 "magic_numbers"
                - mime_type: MIME 类型，如 "application/pdf"
                - extension: 文件扩展名，如 "pdf"
                - description: 文件类型描述，如 "Portable Document Format"
                - file_name: 文件名称，如 "example.pdf"
                - size: 文件大小，如 "1.50 MB"
        """
        try:
            file_info = self.get_file_info(filepath)
            log.info(f"文件信息: {file_info}")
            return file_info["extension"] in SAFE_EXTENSIONS, file_info
        except Exception as e:
            log.warning(f"is_safe_file error: {e}")
            return False, {}  # 检测失败时保守处理，视为不安全文件


class FileDetectorError(Exception):
    """
    文件检测器异常

    当文件类型无法识别时抛出，调用方可据此判断文件是否允许处理。
    """
    msg: str = ""
    pass


file_detector = FileDetector()

if __name__ == '__main__':
    test_file_path = r"C:\Users\The_cute_cat\Desktop\CareerAgent\第十七届中国大学生服务外包创新创业大赛A13赛题.pdf"
    print(file_detector.get_file_info(test_file_path))
