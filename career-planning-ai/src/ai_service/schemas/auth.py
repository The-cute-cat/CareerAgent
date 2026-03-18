"""认证与授权模块

提供 FastAPI 依赖注入函数，用于验证请求中的 Token 和会话 ID。
"""
from typing import Optional

from fastapi import Depends, Form
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ai_service.exceptions import TokenValidationError, ConversationIDValidationError
from ai_service.utils.ai_token_util import check_token
from ai_service.utils.logger_handler import log

security = HTTPBearer(auto_error=False)

__all__ = [
    "validate_token",
    "validate_conversation_id",
]


async def validate_token(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> bool:
    """
    验证请求的 Token。

    作为 FastAPI 依赖使用，从 Authorization Header 提取 Token 进行验证。

    Args:
        credentials: HTTP Bearer 认证凭据，由 FastAPI 自动注入

    Returns:
        验证通过后返回 True

    Raises:
        TokenValidationError: Token 无效或已过期
    """
    if not credentials:
        raise TokenValidationError("未提供认证Token")
    token = credentials.credentials
    if not check_token(token):
        raise TokenValidationError()
    return True


async def validate_conversation_id(
        conversation_id: Optional[str] = Form(None, alias="conversationId"),
        _: bool = Depends(validate_token)
) -> str:
    if not conversation_id:
        raise ConversationIDValidationError()
    return conversation_id
