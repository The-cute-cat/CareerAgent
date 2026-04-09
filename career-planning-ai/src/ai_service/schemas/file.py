"""文件验证模块

提供文件上传验证功能，包括：
- 文件安全性检测（基于魔数识别真实类型，防止文件伪装攻击）
- PDF 文件专用验证
- Word 文档专用验证（支持 doc 和 docx 格式）
- 临时文件队列管理（自动清理过期文件）
"""
import asyncio
import os
import time
import uuid
from dataclasses import dataclass, field
from threading import Lock
from typing import ClassVar

from fastapi import UploadFile, Depends, File

from ai_service.exceptions import FileValidationError
from ai_service.schemas.auth import validate_token
from ai_service.services.file_detector import file_detector
from ai_service.utils.logger_handler import log
from config import settings

__all__ = [
    "handle_file",
    "handle_files",
    "validate_pdf",
    "validate_some_pdf",
    "validate_docx",
    "validate_some_docx",
    "validate_image",
    "validate_some_image",
    "temp_file_queue",
    "",
]


async def handle_files(
        files: list[UploadFile] = File(...),
        _: bool = Depends(validate_token)
) -> list[dict[str, str]]:
    """验证上传文件的安全性和类型，返回文件信息字典列表"""
    return [await _validate_file(file) for file in files]


async def handle_file(
        file: UploadFile = File(...),
        _: bool = Depends(validate_token)
) -> dict[str, str]:
    """验证上传文件的安全性和类型，返回文件信息字典"""
    return await _validate_file(file)


async def _validate_file(file: UploadFile) -> dict[str, str]:
    """
    验证单个上传文件的安全性和类型。

    Returns:
        dict[str, str]: 文件信息字典，包含以下字段：
            - method: 检测方法，如 "magic_numbers", "puremagic", "ole2_deep", "zip_deep"
            - mime_type: MIME 类型，如 "application/pdf"
            - extension: 文件真实扩展名（基于魔数检测，非文件名扩展名）
            - description: 文件类型描述，如 "Portable Document Format"
            - file_name: 服务器保存的文件名（UUID格式）
            - size: 文件大小，如 "1.50 MB"
            - save_path: 服务器保存的完整路径
            - original_name: 用户上传时的原始文件名

    Raises:
        FileValidationError: 文件类型不支持或验证失败
    """
    save_path = os.path.join(settings.path_config.temp.path, uuid.uuid4().hex)
    try:
        os.makedirs(settings.path_config.temp.path, exist_ok=True)
        bytes_data = await file.read()
        with open(save_path, "wb") as f:
            f.write(bytes_data)
        result = await file_detector.is_safe_file(save_path)
        result[1]["save_path"] = save_path
        result[1]["original_name"] = file.filename
        if result[0]:
            if settings.path_config.temp.run_is_clean:
                temp_file_queue.add(save_path, ttl_seconds=settings.path_config.temp.expire)
            return result[1]
        os.remove(save_path)
        log.error(f"Fileinfo:{result[1]}")
        raise FileValidationError(f"File type is not supported, file name:{file.filename}")
    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        log.error(f"文件验证失败: {e}", exc_info=True)
        raise FileValidationError(f"文件验证失败: {e}")


async def validate_some_pdf(
        file_infos: list[dict[str, str]] = Depends(handle_files)
) -> list[dict[str, str]]:
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
            raise FileValidationError(f"File type is not pdf, file info:{file_info}")
    return file_infos


async def validate_pdf(file_info: dict[str, str] = Depends(handle_file)) -> dict[str, str]:
    if file_info["extension"] != "pdf":
        raise FileValidationError(f"File type is not pdf, file info:{file_info}")
    return file_info


async def validate_some_docx(
        file_infos: list[dict[str, str]] = Depends(handle_files)
) -> list[dict[str, str]]:
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
            raise FileValidationError(f"File type is not docx, file info:{file_info}")
    return file_infos


async def validate_docx(file_info: dict[str, str] = Depends(handle_file)) -> dict[str, str]:
    if file_info["extension"] not in ["docx", "doc"]:
        raise FileValidationError(f"File type is not docx, file info:{file_info}")
    return file_info


async def validate_some_image(
        file_infos: list[dict[str, str]] = Depends(handle_files)
) -> list[dict[str, str]]:
    """
    验证文件是否为图片类型（png、jpg、jpeg）。
    """
    for file_info in file_infos:
        if file_info["extension"] not in ["png", "jpg", "jpeg"]:
            raise FileValidationError(f"File type is not image, file info:{file_info}")
    return file_infos


async def validate_image(file_info: dict[str, str] = Depends(handle_file)) -> dict[str, str]:
    if file_info["extension"].lower() not in [suffix.lower() for suffix in settings.image.suffix]:
        raise FileValidationError(f"File type is not image, file info:{file_info}")
    return file_info


@dataclass
class TempFileItem:
    """临时文件项"""
    file_path: str
    created_at: float = field(default_factory=time.time)
    ttl_seconds: int = 900  # 默认15分钟

    def is_expired(self) -> bool:
        """检查文件是否已过期"""
        return time.time() - self.created_at > self.ttl_seconds


class TempFileQueue:
    """
    临时文件队列管理器

    功能：
    - 添加临时文件到队列，设置过期时间
    - 后台任务自动清理过期文件
    - 线程安全操作

    使用示例：
        queue = TempFileQueue()
        queue.add("/path/to/temp/file.txt", ttl_seconds=900)
        await queue.start_cleanup_task()  # 在应用启动时调用
        await queue.stop_cleanup_task()   # 在应用关闭时调用
    """

    _instance: ClassVar["TempFileQueue | None"] = None
    _lock: ClassVar[Lock] = Lock()
    _files: dict[str, TempFileItem]
    _file_lock: Lock
    _cleanup_task: asyncio.Task | None
    _running: bool

    def __new__(cls) -> "TempFileQueue":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._files = {}
                    instance._file_lock = Lock()
                    instance._cleanup_task = None
                    instance._running = False
                    cls._instance = instance
        log.info("TempFileQueue 初始化完成")
        return cls._instance

    def add(self, file_path: str, ttl_seconds: int = settings.path_config.temp.expire) -> str:
        """
        添加临时文件到队列

        Args:
            file_path: 文件路径
            ttl_seconds: 存活时间（秒），默认900秒（15分钟）

        Returns:
            文件路径
        """
        with self._file_lock:
            self._files[file_path] = TempFileItem(
                file_path=file_path,
                ttl_seconds=ttl_seconds
            )
        log.debug(f"临时文件已加入队列: {file_path}, TTL: {ttl_seconds}秒")
        return file_path

    def remove(self, file_path: str) -> bool:
        """
        从队列中移除文件（不删除物理文件）

        Args:
            file_path: 文件路径

        Returns:
            是否成功移除
        """
        with self._file_lock:
            if file_path in self._files:
                del self._files[file_path]
                return True
            return False

    def delete(self, file_path: str) -> bool:
        """
        删除临时文件（从队列移除并删除物理文件）

        Args:
            file_path: 文件路径

        Returns:
            是否成功删除
        """
        self.remove(file_path)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                log.debug(f"临时文件已删除: {file_path}")
                return True
            except Exception as e:
                log.error(f"删除临时文件失败: {file_path}, 错误: {e}")
                return False
        return True

    def get_count(self) -> int:
        """获取队列中的文件数量"""
        with self._file_lock:
            return len(self._files)

    def cleanup_expired(self) -> int:
        """
        清理过期的临时文件

        Returns:
            清理的文件数量
        """
        expired_files = []
        with self._file_lock:
            for file_path, item in list(self._files.items()):
                if item.is_expired():
                    expired_files.append(file_path)

        cleaned = 0
        for file_path in expired_files:
            if self.delete(file_path):
                cleaned += 1
                log.info(f"过期临时文件已清理: {file_path}")

        return cleaned

    async def _cleanup_loop(self, interval: int = settings.path_config.temp.cleanup_interval):
        """
        清理循环

        Args:
            interval: 清理间隔（秒），默认60秒
        """
        while self._running:
            try:
                cleaned = self.cleanup_expired()
                if cleaned > 0:
                    log.info(f"本次清理了 {cleaned} 个过期临时文件")
            except Exception as e:
                log.error(f"临时文件清理任务出错: {e}", exc_info=True)

            await asyncio.sleep(interval)

    async def start_cleanup_task(self, interval: int = settings.path_config.temp.cleanup_interval):
        """
        启动后台清理任务

        Args:
            interval: 清理间隔（秒），默认60秒
        """
        if self._running:
            log.warning("临时文件清理任务已在运行")
            return

        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop(interval))
        log.info(f"临时文件清理任务已启动，清理间隔: {interval}秒")

    async def stop_cleanup_task(self):
        """停止后台清理任务"""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
        log.info("临时文件清理任务已停止")


temp_file_queue = TempFileQueue()
