from enum import Enum, unique

__all__ = [
    "ActionType",
]


@unique
class ActionType(str, Enum):
    """
    定义所有合法的态射动作类型

    用于 AIState.evolve() 方法中标识不同的状态演化操作，
    确保类型安全并提供清晰的语义化操作定义。

    Categories:
        身份与指令: SET_SYSTEM_ROLE, ADD_INSTRUCTION, ADD_CONTEXT, ADD_EXAMPLE
        消息与数据: ADD_TEXT, ADD_IMAGE_URL, ADD_HISTORY_MESSAGE, SET_HISTORY,
                   ADD_LANGCHAIN_MESSAGE
        参数与元数据: SET_LLM_PARAMS, WITH_METADATA
    """

    # 身份与指令层
    SET_SYSTEM_ROLE = "SET_SYSTEM_ROLE"  # 设置系统角色身份
    ADD_INSTRUCTION = "ADD_INSTRUCTION"  # 追加任务指令
    ADD_CONTEXT = "ADD_CONTEXT"  # 注入上下文知识
    ADD_EXAMPLE = "ADD_EXAMPLE"  # 添加 Few-shot 示例

    # 消息与数据层
    ADD_TEXT = "ADD_TEXT"  # 添加文本数据
    ADD_IMAGE_URL = "ADD_IMAGE_URL"  # 添加图像 URL（多模态）
    ADD_HISTORY_MESSAGE = "ADD_HISTORY_MESSAGE"  # 追加单条对话历史
    SET_HISTORY = "SET_HISTORY"  # 设置完整对话历史
    ADD_LANGCHAIN_MESSAGE = "ADD_LANGCHAIN_MESSAGE"  # 注入 LangChain 消息对象

    # 参数与元数据层
    SET_LLM_PARAMS = "SET_LLM_PARAMS"  # 设置 LLM 运行参数
    WITH_METADATA = "WITH_METADATA"  # 附加元数据
