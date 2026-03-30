"""
指纹计算工具模块

提供文本和文件的哈希指纹计算功能，支持多种哈希算法。
适用于文件完整性校验、数据去重、缓存键生成等场景。
"""
import hashlib
from enum import Enum
from pathlib import Path
from typing import Any, Union

from ai_service.utils.logger_handler import log

__all__ = [
    "HashAlgorithm",
    "text_fingerprint",
    "file_fingerprint",
    "bytes_fingerprint",
    "batch_text_fingerprint",
    "batch_file_fingerprint",
    "verify_text",
    "verify_file",
]

# 默认缓冲区大小（64KB）
DEFAULT_BUFFER_SIZE = 65536


class HashAlgorithm(str, Enum):
    """支持的哈希算法枚举"""
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA512 = "sha512"


def _get_hasher(algorithm: Union[HashAlgorithm, str]) -> Any:
    """
    获取哈希计算器实例

    Args:
        algorithm: 哈希算法

    Returns:
        哈希计算器实例

    Raises:
        ValueError: 不支持的算法
    """
    if isinstance(algorithm, HashAlgorithm):
        algorithm = algorithm.value
    algorithm = algorithm.lower()

    if algorithm == HashAlgorithm.MD5.value:
        return hashlib.md5()
    elif algorithm == HashAlgorithm.SHA1.value:
        return hashlib.sha1()
    elif algorithm == HashAlgorithm.SHA256.value:
        return hashlib.sha256()
    elif algorithm == HashAlgorithm.SHA512.value:
        return hashlib.sha512()
    else:
        raise ValueError(f"不支持的哈希算法: {algorithm}，支持的算法: {[a.value for a in HashAlgorithm]}")


def text_fingerprint(
        text: str,
        algorithm: Union[HashAlgorithm, str] = HashAlgorithm.MD5,
        encoding: str = "utf-8",
) -> str:
    """
    计算文本的哈希指纹

    Args:
        text: 待计算的文本内容
        algorithm: 哈希算法，默认 MD5
        encoding: 文本编码，默认 utf-8

    Returns:
        十六进制格式的哈希指纹字符串

    Example:
        >>> fingerprint = text_fingerprint("Hello, World!")
        >>> print(fingerprint)
        '65a8e27d8879283831b664bd8b7f0ad4'

        >>> fingerprint = text_fingerprint("Hello, World!", algorithm="sha256")
        >>> print(fingerprint)
        'df0fd6021bb2bd...'
    """
    if not text:
        return ""

    try:
        hasher = _get_hasher(algorithm)
        hasher.update(text.encode(encoding))
        return hasher.hexdigest()
    except Exception as e:
        log.error(f"计算文本指纹失败: {e}", exc_info=True)
        raise


def bytes_fingerprint(
        data: bytes,
        algorithm: Union[HashAlgorithm, str] = HashAlgorithm.MD5,
) -> str:
    """
    计算字节数据的哈希指纹

    Args:
        data: 待计算的字节数据
        algorithm: 哈希算法，默认 MD5

    Returns:
        十六进制格式的哈希指纹字符串

    Example:
        >>> fingerprint = bytes_fingerprint(b"Hello, World!")
        >>> print(fingerprint)
        '65a8e27d8879283831b664bd8b7f0ad4'
    """
    if not data:
        return ""

    try:
        hasher = _get_hasher(algorithm)
        hasher.update(data)
        return hasher.hexdigest()
    except Exception as e:
        log.error(f"计算字节指纹失败: {e}", exc_info=True)
        raise


def file_fingerprint(
        file_path: Union[str, Path],
        algorithm: Union[HashAlgorithm, str] = HashAlgorithm.MD5,
        buffer_size: int = DEFAULT_BUFFER_SIZE,
) -> str:
    """
    计算文件的哈希指纹（流式读取，支持大文件）

    Args:
        file_path: 文件路径
        algorithm: 哈希算法，默认 MD5
        buffer_size: 读取缓冲区大小，默认 64KB

    Returns:
        十六进制格式的哈希指纹字符串

    Raises:
        FileNotFoundError: 文件不存在
        IOError: 文件读取失败

    Example:
        >>> fingerprint = file_fingerprint("/path/to/file.txt")
        >>> print(fingerprint)
        'd41d8cd98f00b204e9800998ecf8427e'

        >>> fingerprint = file_fingerprint("/path/to/large_file.zip", algorithm="sha256")
        >>> print(fingerprint)
        'e3b0c44298fc1c...'
    """
    file_path = Path(file_path) if isinstance(file_path, str) else file_path

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"路径不是文件: {file_path}")

    try:
        hasher = _get_hasher(algorithm)

        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(buffer_size)
                if not chunk:
                    break
                hasher.update(chunk)

        return hasher.hexdigest()
    except Exception as e:
        log.error(f"计算文件指纹失败: file={file_path}, error={e}", exc_info=True)
        raise


def batch_text_fingerprint(
        texts: list[str],
        algorithm: Union[HashAlgorithm, str] = HashAlgorithm.MD5,
        encoding: str = "utf-8",
) -> dict[str, str]:
    """
    批量计算文本的哈希指纹

    Args:
        texts: 文本列表
        algorithm: 哈希算法，默认 MD5
        encoding: 文本编码，默认 utf-8

    Returns:
        文本到指纹的映射字典

    Example:
        >>> texts = ["hello", "world", "hello"]  # 相同内容产生相同指纹
        >>> result = batch_text_fingerprint(texts)
        >>> print(result)
        {'hello': '5d41402abc4b2a76b9719d911017c592', 'world': '7d793037a076...'}
    """
    result = {}
    for text in texts:
        if text not in result:  # 避免重复计算
            result[text] = text_fingerprint(text, algorithm, encoding)
    return result


def batch_file_fingerprint(
        file_paths: list[Union[str, Path]],
        algorithm: Union[HashAlgorithm, str] = HashAlgorithm.MD5,
        buffer_size: int = DEFAULT_BUFFER_SIZE,
) -> dict[str, str]:
    """
    批量计算文件的哈希指纹

    Args:
        file_paths: 文件路径列表
        algorithm: 哈希算法，默认 MD5
        buffer_size: 读取缓冲区大小，默认 64KB

    Returns:
        文件路径到指纹的映射字典

    Example:
        >>> files = ["/path/to/file1.txt", "/path/to/file2.txt"]
        >>> result = batch_file_fingerprint(files)
        >>> print(result)
        {'/path/to/file1.txt': 'd41d8cd98f...', '/path/to/file2.txt': 'e99a18c428...'}
    """
    result = {}
    for file_path in file_paths:
        path_str = str(file_path)
        try:
            result[path_str] = file_fingerprint(file_path, algorithm, buffer_size)
        except Exception as e:
            log.warning(f"批量计算跳过文件: {path_str}, error={e}")
            result[path_str] = ""
    return result


def verify_text(
        text: str,
        fingerprint: str,
        algorithm: Union[HashAlgorithm, str] = HashAlgorithm.MD5,
        encoding: str = "utf-8",
) -> bool:
    """
    验证文本的哈希指纹是否匹配

    Args:
        text: 待验证的文本内容
        fingerprint: 预期的哈希指纹
        algorithm: 哈希算法，默认 MD5
        encoding: 文本编码，默认 utf-8

    Returns:
        指纹是否匹配

    Example:
        >>> is_valid = verify_text("Hello", "8b1a9953c4611296a827abf8c47804d7")
        >>> print(is_valid)
        True
    """
    try:
        computed = text_fingerprint(text, algorithm, encoding)
        return computed.lower() == fingerprint.lower()
    except Exception as e:
        log.error(f"验证文本指纹失败: text={text}, error={e}", exc_info=True)
        return False


def verify_file(
        file_path: Union[str, Path],
        fingerprint: str,
        algorithm: Union[HashAlgorithm, str] = HashAlgorithm.MD5,
        buffer_size: int = DEFAULT_BUFFER_SIZE,
) -> bool:
    """
    验证文件的哈希指纹是否匹配

    Args:
        file_path: 文件路径
        fingerprint: 预期的哈希指纹
        algorithm: 哈希算法，默认 MD5
        buffer_size: 读取缓冲区大小，默认 64KB

    Returns:
        指纹是否匹配

    Example:
        >>> is_valid = verify_file("/path/to/file.txt", "d41d8cd98f00b204e9800998ecf8427e")
        >>> print(is_valid)
        True
    """
    try:
        computed = file_fingerprint(file_path, algorithm, buffer_size)
        return computed.lower() == fingerprint.lower()
    except Exception as e:
        log.error(f"验证文件指纹失败: file={file_path}, error={e}", exc_info=True)
        return False


def main():
    print("=== 文本指纹测试 ===")
    text = "Hello, World!"
    print(f"MD5:    {text_fingerprint(text, HashAlgorithm.MD5)}")
    print(f"SHA1:   {text_fingerprint(text, HashAlgorithm.SHA1)}")
    print(f"SHA256: {text_fingerprint(text, HashAlgorithm.SHA256)}")
    print(f"SHA512: {text_fingerprint(text, HashAlgorithm.SHA512)}")

    print("\n=== 字节指纹测试 ===")
    print(f"MD5: {bytes_fingerprint(b'test data')}")

    print("\n=== 验证测试 ===")
    fp = text_fingerprint("test")
    print(f"验证 'test': {verify_text('test', fp)}")
    print(f"验证 'test1': {verify_text('test1', fp)}")

    print("\n=== 批量测试 ===")
    texts = ["hello", "world", "hello"]
    print(f"批量文本指纹: {batch_text_fingerprint(texts)}")


if __name__ == "__main__":
    main()
