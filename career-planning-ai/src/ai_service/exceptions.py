from typing import Any

__all__ = [
    "ApiException",
    "FileValidationError",
    "TokenValidationError",
    "ConversationIDValidationError",
    "CommonHandleError",
]


class ApiException(Exception):
    """自定义API异常"""

    def __init__(self, code: int, msg: str = None, data: Any = None):
        self.code = code
        self.msg = msg
        self.data = data


class FileValidationError(ApiException):
    """文件验证失败异常"""

    def __init__(self, msg: str = "文件类型不安全或不被允许"):
        super().__init__(code=400, msg=msg)


class TokenValidationError(ApiException):
    """Token验证失败异常"""

    def __init__(self, msg: str = "Token验证失败"):
        super().__init__(code=401, msg=msg)


class CommonHandleError(ApiException):
    """通用处理异常"""

    def __init__(self, msg: str = "通用处理异常"):
        super().__init__(code=500, msg=msg)


class ConversationIDValidationError(ApiException):
    """
    会话 ID 验证失败异常

    当请求中缺少 conversationId 或 conversationId 格式无效时抛出。
    通常用于需要关联会话上下文的接口。
    """

    def __init__(self, msg: str = "ConversationID验证失败"):
        super().__init__(code=401, msg=msg)
