from typing import Any

__all__ = [
    "ApiException",
    "FileValidationError",
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
