"""
AI Engine 异常体系

定义了框架中所有可能的异常类型，遵循以下设计原则：
1. 层次化：按错误类型分层，便于上层捕获特定异常
2. 语义化：异常名称清晰表达错误原因
3. 可追溯：所有异常包含上下文信息，便于调试

异常层次结构：

AIEngineError (基类)
├── ConfigurationError (配置错误)
│   ├── ModelNotSpecifiedError
│   └── InvalidActionTypeError
├── ValidationError (验证错误)
│   └── EmptyInputError
├── ExecutionError (执行错误)
│   ├── StructExtractionError
│   ├── TextGenerationError
│   └── StreamInterruptedError
└── ResourceError (资源错误)
    └── StatePollutionError
"""

from typing import Any, Optional, Type
from pydantic import BaseModel


class AIEngineError(Exception):
    """
    AI Engine 异常基类

    所有框架异常的基类，提供统一的异常接口。

    Attributes:
        message: 错误消息
        context: 额外的上下文信息（如模型名称、请求ID等）
        cause: 原始异常（如果有）

    Example:
        >>> try:
        ...     raise AIEngineError(
        ...         "Something went wrong", context={"model": "qwen"}
        ...     )
        ... except AIEngineError as e:
        ...     print(f"Error: {e.message}, Context: {e.context}")
    """

    def __init__(
        self,
        message: str,
        context: Optional[dict] = None,
        cause: Optional[Exception] = None
    ) -> None:
        """
        初始化异常

        Args:
            message: 错误消息
            context: 额外的上下文信息
            cause: 原始异常
        """
        self.message = message
        self.context = context or {}
        self.cause = cause
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """格式化完整的错误消息"""
        parts = [self.message]
        if self.context:
            context_str = ", ".join(
                f"{k}={v}" for k, v in self.context.items()
            )
            parts.append(f"[{context_str}]")
        if self.cause:
            cause_info = f"Caused by: {type(self.cause).__name__}"
            parts.append(f"{cause_info}: {self.cause}")
        return " | ".join(parts)

    def __str__(self) -> str:
        return self._format_message()


# =============================================================================
# 配置错误 (Configuration Errors)
# =============================================================================

class ConfigurationError(AIEngineError):
    """
    配置错误基类

    当框架配置不正确时抛出，如模型未指定、参数无效等。
    这类错误通常在流水线构建阶段（Stage 1-4）发生。
    """
    pass


class ModelNotSpecifiedError(ConfigurationError):
    """
    模型未指定错误

    当调用 pick_brain() 时未提供有效的模型配置时抛出。

    Example:
        >>> raise ModelNotSpecifiedError(
        ...     "必须指定一个有效的模型配置",
        ...     context={"received": None}
        ... )
    """

    def __init__(
        self,
        message: str = "编译错误：必须指定一个有效的模型名称",
        context: Optional[dict] = None
    ) -> None:
        super().__init__(message, context)


class InvalidActionTypeError(ConfigurationError):
    """
    无效的 ActionType 错误

    当 evolve() 接收到未定义的 ActionType 时抛出。

    Example:
        >>> raise InvalidActionTypeError(
        ...     "未定义的演化动作",
        ...     context={"action_type": "UNKNOWN_ACTION"}
        ... )
    """

    def __init__(
        self,
        action_type: Any,
        context: Optional[dict] = None
    ) -> None:
        ctx = context or {}
        ctx["action_type"] = str(action_type)
        super().__init__(f"未定义的演化动作: {action_type}", ctx)


# =============================================================================
# 验证错误 (Validation Errors)
# =============================================================================

class ValidationError(AIEngineError):
    """
    验证错误基类

    当输入数据不符合要求时抛出。
    这类错误通常在 InputStep.next_step() 阶段发生。
    """
    pass


class EmptyInputError(ValidationError):
    """
    空输入错误

    当流水线没有任何有效输入（指令、数据、历史记录）时抛出。

    Example:
        >>> raise EmptyInputError(
        ...     "必须至少注入指令、数据或历史记录中的一项"
        ... )
    """

    def __init__(
        self,
        message: str = "编译错误：必须至少注入 指令、数据 或 历史记录 中的一项。",
        context: Optional[dict] = None
    ) -> None:
        super().__init__(message, context)


# =============================================================================
# 执行错误 (Execution Errors)
# =============================================================================

class ExecutionError(AIEngineError):
    """
    执行错误基类

    当 LLM API 调用失败时抛出。
    这类错误通常在 Evaluation 阶段（Stage 5）发生。
    """

    def __init__(
        self,
        message: str,
        context: Optional[dict] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, context, cause)


class StructExtractionError(ExecutionError):
    """
    结构化提取错误

    当结构化输出提取失败时抛出。

    Example:
        >>> raise StructExtractionError(
        ...     schema=PersonModel,
        ...     cause=original_exception,
        ...     context={"model": "qwen-max"}
        ... )
    """

    def __init__(
        self,
        schema: Type[BaseModel],
        message: str = "结构化提取失败",
        context: Optional[dict] = None,
        cause: Optional[Exception] = None
    ) -> None:
        ctx = context or {}
        ctx["schema"] = schema.__name__
        super().__init__(f"{message}[{schema.__name__}]", ctx, cause)


class TextGenerationError(ExecutionError):
    """
    文本生成错误

    当文本生成失败时抛出。

    Example:
        >>> raise TextGenerationError(
        ...     message="文本生成失败",
        ...     cause=original_exception,
        ...     context={"model": "qwen-max"}
        ... )
    """
    pass


class StreamInterruptedError(ExecutionError):
    """
    流式输出中断错误

    当流式输出过程中发生错误时抛出。

    Example:
        >>> raise StreamInterruptedError(
        ...     message="流式生成中断",
        ...     cause=original_exception,
        ...     context={"model": "qwen-max"}
        ... )
    """

    def __init__(
        self,
        message: str = "流式生成中断",
        context: Optional[dict] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, context, cause)


class ModelConfigNotFoundError(ExecutionError):
    """
    模型配置不存在错误

    当尝试访问不存在的模型配置时抛出。

    Example:
        >>> raise ModelConfigNotFoundError(
        ...     context={"field": "model"}
        ... )
    """

    def __init__(
        self,
        message: str = "模型配置不存在",
        context: Optional[dict] = None
    ) -> None:
        super().__init__(message, context)


# =============================================================================
# 资源错误 (Resource Errors)
# =============================================================================

class ResourceError(AIEngineError):
    """
    资源错误基类

    当违反资源使用约束时抛出。
    """
    pass


class StatePollutionError(ResourceError):
    """
    状态污染错误

    当尝试在 AIState 中存储物理资源或长生命周期对象时抛出。
    这是严重错误，可能导致 RecursionError。

    Example:
        >>> raise StatePollutionError(
        ...     field="db_conn",
        ...     reason="物理资源（数据库连接）禁止存入 AIState，会导致 model_copy(deep=True) 栈溢出"
        ... )
    """

    def __init__(
        self,
        field: str,
        reason: str = "物理资源禁止存入 AIState",
        context: Optional[dict] = None
    ) -> None:
        ctx = context or {}
        ctx["field"] = field
        message = f"状态污染风险: 字段 '{field}' - {reason}"
        super().__init__(message, ctx)


# =============================================================================
# 异常工具函数
# =============================================================================

def wrap_exception(
    error: Exception,
    wrapper_class: Type[AIEngineError],
    message: Optional[str] = None,
    context: Optional[dict] = None
) -> AIEngineError:
    """
    将原始异常包装为框架异常

    Args:
        error: 原始异常
        wrapper_class: 包装异常类
        message: 自定义消息（可选）
        context: 上下文信息

    Returns:
        AIEngineError: 包装后的异常

    Example:
        >>> try:
        ...     response = await client.call()
        ... except Exception as e:
        ...     raise wrap_exception(e, TextGenerationError, "API 调用失败")
    """
    msg = message or str(error)
    return wrapper_class(msg, context, cause=error)
