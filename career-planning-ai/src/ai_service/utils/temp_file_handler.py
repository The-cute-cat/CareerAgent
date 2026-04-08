"""
临时文件处理工具模块

提供临时文件的创建、清理和管理功能，支持多线程安全访问。
适用于需要临时存储二进制数据的场景，如图片处理、文件上传等。
"""
import os
import threading
import uuid
from contextlib import contextmanager
from typing import List

from ai_service.utils.logger_handler import log
from config import settings

__all__ = ["create_temp_file", "cleanup_temp_file", "cleanup_all_temp_file", "temp_file"]

temp_file_list: List[str] = []

_temp_file_lock = threading.Lock()


def create_temp_file(data: bytes):
    """
    创建临时文件并写入数据。

    Args:
        data: 要写入的二进制数据

    Returns:
        str: 创建的临时文件的完整路径

    Raises:
        Exception: 文件创建或写入失败时抛出异常
    """
    filename = f"{uuid.uuid4()}"
    save_path = os.path.join(settings.path_config.temp.path, filename)

    try:
        with open(save_path, "wb") as file:
            file.write(data)
        with _temp_file_lock:
            temp_file_list.append(save_path)
        return save_path
    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        log.error(f"创建临时文件失败: {e}", exc_info=True)
        raise e


def cleanup_temp_file(file_path: str) -> None:
    """
    清理指定的临时文件。

    从磁盘删除文件并从跟踪列表中移除。如果文件不存在，仅从列表中移除。

    Args:
        file_path: 要清理的临时文件路径
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        with _temp_file_lock:
            if file_path in temp_file_list:
                temp_file_list.remove(file_path)
    except Exception as e:
        log.error(f"清理临时文件失败: {e}", exc_info=True)


def cleanup_all_temp_file() -> None:
    """
    清理所有已创建的临时文件。

    遍历并删除跟踪列表中的所有临时文件，适用于程序退出前的清理工作。
    """
    for file_path in temp_file_list:
        cleanup_temp_file(file_path)
    temp_file_list.clear()


@contextmanager
def temp_file(data: bytes):
    """
    临时文件上下文管理器。

    自动管理临时文件的生命周期：进入时创建，退出时自动清理。
    推荐使用 with 语句调用，确保资源正确释放。

    Args:
        data: 要写入的二进制数据

    Yields:
        str: 创建的临时文件路径

    Example:
        >>> with temp_file(b"hello") as file:
        ...     print(f"临时文件路径: {file}")
        ...     # 使用文件...
        >>> # 退出 with 块后，文件自动被清理
    """
    file_path = None
    try:
        file_path = create_temp_file(data)
        yield file_path
    finally:
        if file_path:
            cleanup_temp_file(file_path)


if __name__ == '__main__':
    with temp_file(b"123456") as f:
        print(f)
