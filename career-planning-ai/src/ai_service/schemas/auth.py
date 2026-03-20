"""认证与授权模块

提供 FastAPI 依赖注入函数，用于验证请求中的 Token 和会话 ID。
"""
from typing import Optional

from fastapi import Depends, Form
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ai_service.exceptions import TokenValidationError, ConversationIDValidationError
from ai_service.utils.ai_token_util import check_token

# HTTP Bearer 认证方案，auto_error=True 表示未提供 Token 时自动返回 403 错误
security = HTTPBearer(auto_error=True)

__all__ = ["validate_token"]


async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    conversation_id: Optional[str] = Form(None, alias="conversationId")
) -> str:
    """
    验证请求的 Token 和会话 ID。

    作为 FastAPI 依赖使用，从 Authorization Header 提取 Token 进行验证，
    并从 Multipart Form 中提取 conversationId。

    Args:
        credentials: HTTP Bearer 认证凭据，由 FastAPI 自动注入
        conversation_id: 会话 ID，从 Multipart Form 的 conversationId 字段获取

    Returns:
        验证通过后返回 conversation_id 字符串

    Raises:
        TokenValidationError: Token 无效或已过期
        ConversationIDValidationError: conversationId 缺失
    """
    token = credentials.credentials
    if not check_token(token):
        raise TokenValidationError()
    if not conversation_id:
        raise ConversationIDValidationError()
    return conversation_id
