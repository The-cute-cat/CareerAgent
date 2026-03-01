import base64
import time
from typing import Optional

from ai_service.utils.encrypt_sensitive_data import hash_data, check_data


def create_token() -> str:
    """
    创建一个新的 AI 令牌。

    令牌生成流程如下：
    1. 将当前系统时间（毫秒）与预设的固定字符串拼接，用 "|" 分隔。
    2. 对拼接后的原始字符串进行 Base64 编码。
    3. 使用 BCrypt 算法对原始字符串进行哈希。
    4. 最终令牌由以下部分组合而成：BCrypt 哈希值的前 7 位、Base64 编码后的字符串长度、
       Base64 编码后的字符串本身，以及 BCrypt 哈希值的剩余部分。

    :return: 新生成的、唯一的 AI 令牌字符串。
    """
    timestamp = int(time.time() * 1000)
    raw_str = f"{timestamp}|CareerAgent"
    raw_bytes = raw_str.encode('utf-8')
    b64_bytes = base64.b64encode(raw_bytes)
    str_base64 = b64_bytes.decode('utf-8')

    encrypt_str = hash_data(raw_str)
    token = (
            encrypt_str[:7] +
            str(len(str_base64)) +
            "." +
            str_base64 +
            encrypt_str[7:]
    )
    return token


def check_token(token: Optional[str]) -> bool:
    """
    检查给定的令牌是否有效。
    :param token: 要验证的 AI 令牌字符串。
    :return: 如果令牌有效且未过期，则返回 True；否则返回 False。
    """
    if token is None:
        return False
    try:
        index = token.find(".")
        if index == -1:
            return False
        length_str = token[7:index]
        length = int(length_str)
        start_idx = index + 1
        end_idx = start_idx + length
        if end_idx > len(token):
            return False
        b64_part = token[start_idx:end_idx]
        pre_str_bytes = base64.b64decode(b64_part)
        pre_str = pre_str_bytes.decode('utf-8')
        pipe_index = pre_str.find("|")
        if pipe_index == -1:
            return False
        time_str = pre_str[:pipe_index]
        time_val = int(time_str)
        current_time_ms = int(time.time() * 1000)
        if current_time_ms - time_val > 1800 * 1000:
            return False
        wait_check_str = token[:7] + token[end_idx:]
        return check_data(pre_str, wait_check_str)
    except (ValueError, IndexError, Exception):
        return False
