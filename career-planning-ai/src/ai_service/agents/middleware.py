from contextvars import ContextVar
from typing import Callable
from dataclasses import dataclass

from langchain.agents import AgentState
from langchain.agents.middleware import before_model, after_model, wrap_tool_call
from langchain_core.messages import ToolMessage, AIMessage
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.runtime import Runtime
from langgraph.types import Command

from ai_service.agents import log

__all__ = [
    "monitor_tool",
    "log_before_model",
    "track_token_usage",
    "reset_token_stats",
    "get_token_stats",
]

@dataclass
class TokenStats:
    """Token 统计信息"""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    call_count: int = 0  # 模型调用次数


_token_stats: ContextVar[TokenStats] = ContextVar("token_stats", default=TokenStats())


def reset_token_stats() -> None:
    """重置 Token 统计（每次生成计划前调用）"""
    _token_stats.set(TokenStats())


def get_token_stats() -> TokenStats:
    """获取当前 Token 统计"""
    return _token_stats.get()


@dataclass
class TokenStats:
    """Token 统计信息"""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    call_count: int = 0  # 模型调用次数


_token_stats: ContextVar[TokenStats] = ContextVar("token_stats", default=TokenStats())


def reset_token_stats() -> None:
    """重置 Token 统计（每次生成计划前调用）"""
    _token_stats.set(TokenStats())


def get_token_stats() -> TokenStats:
    """获取当前 Token 统计"""
    return _token_stats.get()


@wrap_tool_call
def monitor_tool(
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    log.info(f"[tool monitor]执行工具：{request.tool_call['name']}")
    log.info(f"[tool monitor]传入参数：{request.tool_call['args']}")
    try:
        result = handler(request)
        log.info(f"[tool monitor]工具{request.tool_call['name']}调用成功")
        return result
    except Exception as e:
        log.error(
            f"工具{request.tool_call['name']}调用失败，原因：{str(e)}", exc_info=True
        )
        raise e


@before_model
def log_before_model(state: AgentState, runtime: Runtime) -> None:
    log.info(
        f"[log_before_model]即将调用模型,带有{len(state['messages'])}条消息,runtime:{runtime}"
    )
    return None


@after_model
def track_token_usage(state: AgentState, _: Runtime) -> None:
    """追踪模型调用的 Token 消耗并累计统计"""
    messages = state.get("messages", [])
    if not messages:
        return None

    last_msg = messages[-1]
    if not isinstance(last_msg, AIMessage):
        return None

    input_tokens = 0
    output_tokens = 0
    total_tokens = 0

    usage_metadata = getattr(last_msg, "usage_metadata", None)
    if usage_metadata:
        input_tokens = usage_metadata.get("input_tokens", 0)
        output_tokens = usage_metadata.get("output_tokens", 0)
        total_tokens = usage_metadata.get("total_tokens", input_tokens + output_tokens)
    else:
        response_metadata = getattr(last_msg, "response_metadata", {})
        if response_metadata:
            token_usage = response_metadata.get("token_usage", {})
            if token_usage:
                input_tokens = token_usage.get("prompt_tokens", 0)
                output_tokens = token_usage.get("completion_tokens", 0)
                total_tokens = token_usage.get("total_tokens", input_tokens + output_tokens)

    if total_tokens > 0:
        # 累计统计
        stats = _token_stats.get()
        stats.input_tokens += input_tokens
        stats.output_tokens += output_tokens
        stats.total_tokens += total_tokens
        stats.call_count += 1

        log.info(
            f"[token usage] 本次: input={input_tokens}, output={output_tokens}, total={total_tokens} | "
            f"累计: input={stats.input_tokens}, output={stats.output_tokens}, total={stats.total_tokens}, "
            f"调用次数={stats.call_count}"
        )
    else:
        log.debug("[token usage] 未找到 token 消耗信息")

    return None
