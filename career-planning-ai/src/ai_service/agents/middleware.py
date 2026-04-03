from typing import Callable

from langchain.agents import AgentState
from langchain.agents.middleware import before_model, wrap_tool_call
from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.runtime import Runtime
from langgraph.types import Command

from ai_service.agents import log


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
