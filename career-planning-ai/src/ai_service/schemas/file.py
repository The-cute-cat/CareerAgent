"""文件验证模块

提供文件上传验证功能，包括：
- 文件安全性检测（基于魔数识别真实类型，防止文件伪装攻击）
- PDF 文件专用验证
- Word 文档专用验证（支持 doc 和 docx 格式）
"""
import os
import uuid
from typing import Dict, List

from fastapi import UploadFile, Depends, File

from ai_service.exceptions import FileValidationError
from ai_service.services.file_detector import file_detector
from ai_service.utils.logger_handler import log
from config import settings

__all__ = [
    "handle_file",
    "validate_pdf",
    "validate_docx",
]


async def handle_file(files: List[UploadFile] = File(...)) -> List[Dict[str, str]]:
    """验证上传文件的安全性和类型，返回文件信息字典"""
    return [await _validate_file(file) for file in files]


async def _validate_file(file: UploadFile) -> Dict[str, str]:
    save_path = os.path.join(settings.path_config.temp, uuid.uuid4().hex)
    try:
        bytes_data = await file.read()
        with open(save_path, "wb") as f:
            f.write(bytes_data)
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


async def validate_pdf(file_infos: List[Dict[str, str]] = Depends(handle_file)):
    """
    验证文件是否为 PDF 类型。

    作为 FastAPI 依赖使用，会自动触发 handle_file 完成文件安全检测。

    Args:
        file_infos: 由 handle_file 返回的文件信息列表

    Returns:
        验证通过的文件信息列表

    Raises:
        FileValidationError: 文件类型不是 PDF
    """
    for file_info in file_infos:
        if file_info["extension"] != "pdf":
            raise FileValidationError(f"File type is not pdf, file name:{file_info['file_name']}")
    return file_infos


async def validate_docx(file_infos: List[Dict[str, str]] = Depends(handle_file)):
    """
    验证文件是否为 Word 文档类型（doc 或 docx）。

    作为 FastAPI 依赖使用，会自动触发 handle_file 完成文件安全检测。

    Args:
        file_infos: 由 handle_file 返回的文件信息列表

    Returns:
        验证通过的文件信息列表

    Raises:
        FileValidationError: 文件类型不是 Word 文档
    """
    for file_info in file_infos:
        if file_info["extension"] not in ["docx", "doc"]:
            raise FileValidationError(f"File type is not docx, file name:{file_info['file_name']}")
    return file_infos
