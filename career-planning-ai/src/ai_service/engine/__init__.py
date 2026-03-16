"""
AI Engine 模块

基于范畴论思想的分段建造者模式 LLM 调用框架。
"""

from ai_service.engine.action_type import ActionType
from ai_service.engine.ai_state import AIState
from ai_service.engine.ai_engine import (
    AIEngine,
    BaseStep,
    InputStep,
    TuneStep,
    ShapeStep,
    StructActionStep,
    TextActionStep,
)
from ai_service.engine.exceptions import (
    AIEngineError,
    ConfigurationError,
    ModelNotSpecifiedError,
    InvalidActionTypeError,
    ValidationError,
    EmptyInputError,
    ExecutionError,
    StructExtractionError,
    TextGenerationError,
    StreamInterruptedError,
    ModelConfigNotFoundError,
    ResourceError,
    StatePollutionError,
)

__all__ = [
    # 核心类
    "AIEngine",
    "AIState",
    "ActionType",
    # 阶段类
    "BaseStep",
    "InputStep",
    "TuneStep",
    "ShapeStep",
    "StructActionStep",
    "TextActionStep",
    # 异常类
    "AIEngineError",
    "ConfigurationError",
    "ModelNotSpecifiedError",
    "InvalidActionTypeError",
    "ValidationError",
    "EmptyInputError",
    "ExecutionError",
    "StructExtractionError",
    "TextGenerationError",
    "StreamInterruptedError",
    "ModelConfigNotFoundError",
    "ResourceError",
    "StatePollutionError",
]
