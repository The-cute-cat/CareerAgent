"""
AI Engine 模块

基于范畴论思想的分段建造者模式 LLM 调用框架。
"""

from ai_service.utils.logger_handler import get_logger

log = get_logger("engine")

__all__ = [
    "log",
    "action_type",
    "ai_engine",
    "ai_state",
    "exceptions",
]
