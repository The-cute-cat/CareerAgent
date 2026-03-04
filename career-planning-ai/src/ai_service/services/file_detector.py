import os
from typing import Dict

import puremagic
from binaryornot.check import is_binary

from ai_service.utils.logger_handler import log
from ai_service.utils.magic_numbers import (
    FILE_SIGNATURES,
    DANGEROUS_EXTENSIONS,
    SAFE_EXTENSIONS,
)
from ai_service.utils.path_tool import abs_path, get_abs_path

__all__ = ["file_detector"]


class FileDetector:
    """
    文件类型检测器

    通过分析文件头部的魔数（Magic Number）来识别文件的真实类型，
    而非依赖文件扩展名，可有效防止文件伪装攻击。

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
                        result["description"] = signature.description
                        result["mime_type"] = signature.mime_type
                        result["extension"] = ext
                        result["method"] = "magic_numbers"
                        return result
        except Exception as e:
            log.warning(f"magic_string error: {e}")

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
            - mime_type: MIME 类型，如 "application/pdf"
            - extension: 文件扩展名，如 "pdf"
            - description: 文件类型描述，如 "Portable Document Format"
            - size: 文件大小，如 "1.50 MB"

        Raises:
            Exception: 当无法识别文件类型时抛出异常
        """
        result = {
            "method": "",
            "mime_type": "unknown",
            "extension": "unknown",
            "description": "unknown file",
            "size": self._format_size(os.path.getsize(filepath))
        }

        file_extension = "."
        with open(filepath, 'rb') as f:
            file_bytes = f.read()
            file_name = os.path.basename(filepath)
            if file_name.find(".") != -1:
                file_extension = file_name.split(".")[-1]
        if file_extension != "." and file_extension in DANGEROUS_EXTENSIONS:
            temp = self._check_by_puremagic(filepath, result)
            if temp:
                return temp
        else:
            temp = self._check_magic_numbers(file_bytes, result)
            if temp:
                return temp
            temp = self._check_text_file(filepath, result)
            if temp:
                temp["extension"] = file_extension
                return temp
            temp = self._check_by_puremagic(filepath, result)
            if temp:
                return temp
        raise Exception(f"未知文件类型: {filepath}")

    def is_dangerous_file(self, filepath: str) -> bool:
        """
        检查文件是否属于危险类型

        危险文件包括可执行文件、脚本文件等可能存在安全风险的文件类型。

        Args:
            filepath: 文件路径

        Returns:
            True 表示危险文件，False 表示非危险文件
            当检测失败时默认返回 True（安全优先原则）
        """
        try:
            file_info = self.get_file_info(filepath)
            return file_info["extension"] in DANGEROUS_EXTENSIONS
        except Exception as e:
            log.warning(f"is_dangerous_file error: {e}")
            return True  # 检测失败时保守处理，视为危险文件

    def is_safe_file(self, filepath: str) -> bool:
        """
        检查文件是否属于安全类型

        安全文件包括文档、图片、压缩包等允许上传的文件类型。

        Args:
            filepath: 文件路径

        Returns:
            True 表示安全文件，False 表示非安全文件
            当检测失败时默认返回 False（安全优先原则）
        """
        try:
            file_info = self.get_file_info(filepath)
            return file_info["extension"] in SAFE_EXTENSIONS
        except Exception as e:
            log.warning(f"is_safe_file error: {e}")
            return False  # 检测失败时保守处理，视为不安全文件


file_detector = FileDetector()

if __name__ == '__main__':
    test_file_path = abs_path("./main.py")
    print(file_detector.get_file_info(test_file_path))
