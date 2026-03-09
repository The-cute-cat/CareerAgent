"""文件验证模块

提供文件上传验证功能，包括文件类型检测和 PDF 文件专用验证。
"""
import os
import uuid
from typing import Dict

from fastapi import UploadFile, Depends

from ai_service.exceptions import FileValidationError
from ai_service.services.file_detector import file_detector
from ai_service.utils.logger_handler import log
from config import settings

__all__ = ["validate_file", "validate_pdf"]


async def validate_file(file: UploadFile) -> Dict[str, str]:
    """验证上传文件的安全性和类型，返回文件信息字典"""
    save_path = os.path.join(settings.path_config.temp, uuid.uuid4().hex)
    try:
        file_bytes = await file.read()
        with open(save_path, "wb") as f:
            f.write(file_bytes)
        result = file_detector.is_safe_file(save_path)
        result[1]["save_path"] = save_path
        if result[0]:
            return result[1]
        os.remove(save_path)
        log.error(f"Fileinfo:{result[1]}")
        raise FileValidationError(f"File type is not supported, file name:{file.filename}")
    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        log.error(f"文件验证失败: {e}", exc_info=True)
        raise FileValidationError(f"文件验证失败: {e}")


async def validate_pdf(file_info: Dict[str, str] = Depends(validate_file)):
    """验证文件是否为 PDF 类型，作为 FastAPI 依赖使用"""
    if file_info.get("extension") == "pdf":
        return file_info
    raise FileValidationError(f"File type is not pdf. Extension: {file_info.get('extension')}")
