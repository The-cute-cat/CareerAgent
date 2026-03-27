from typing import List, Dict, Any, Optional

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field

from ai_service.engine.action_type import ActionType
from ai_service.engine.exceptions import (
    InvalidActionTypeError,
    ModelConfigNotFoundError,
)
from config import LLMModelBase

__all__ = [
    "AIState"
]


# =====================================================================
# 状态容器：承载流转的"对象" (The Object in Category)
# =====================================================================
class AIState(BaseModel):
    """
    内部状态容器：承载流水线在各阶段间流转的上下文数据

    作为纯数据对象，不存储共享资源，确保状态的可序列化和线程安全。
    通过 evolve() 方法实现不可变的状态演化，每次操作返回新的状态实例。

    Attributes:
        model (Optional[LLMModelBase]): 主模型配置
        model_fallbacks (List[LiteLLMBase]): 备选模型列表，用于容错降级
        system_role (str): 系统角色身份定义（身份层）
        instructions (List[str]): 任务指令列表（指令层）
        contexts (List[str]): 上下文知识列表（上下文层）
        examples (List[Dict[str, Any]]): Few-shot 示例列表（示例层）
        user_data (List[Dict[str, Any]]): 原始用户数据（数据层）
        history (List[Dict[str, Any]]): 多轮对话历史
        llm_params (Dict[str, Any]): LiteLLMBase 运行参数
        metadata (Dict[str, Any]): 请求元数据
    """

    model: Optional[LLMModelBase] = None
    model_fallbacks: List[LLMModelBase] = Field(default_factory=list)

    # 提示词层次架构
    system_role: str = ""  # 身份层：定义 AI 的核心身份
    instructions: List[str] = Field(default_factory=list)  # 指令层：具体的任务指令
    contexts: List[str] = Field(default_factory=list)  # 上下文层：知识库或背景信息
    examples: List[Dict[str, Any]] = Field(default_factory=list)  # 示例层：Few-shot 学习样本
    user_data: List[Dict[str, Any]] = Field(
        default_factory=list
    )  # 原始数据层 (add_text/add_image)

    # 支持多轮对话
    history: List[Dict[str, Any]] = Field(default_factory=list)

    llm_params: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # 利用 Enum 分类逻辑（更安全且可读）
    _APPEND_LIST_ACTIONS = {
        ActionType.ADD_INSTRUCTION,
        ActionType.ADD_CONTEXT,
        ActionType.ADD_EXAMPLE,
        ActionType.ADD_HISTORY_MESSAGE,
        ActionType.ADD_TEXT,
        ActionType.ADD_IMAGE_URL,
        ActionType.ADD_LANGCHAIN_MESSAGE,
    }
    _REPLACE_ACTIONS = {
        ActionType.SET_SYSTEM_ROLE,
        ActionType.SET_HISTORY
    }
    _MERGE_DICT_ACTIONS = {
        ActionType.SET_LLM_PARAMS,
        ActionType.WITH_METADATA
    }

    # 2. 建立 Action 到 字段 的精准映射
    _MAP = {
        ActionType.SET_SYSTEM_ROLE: "system_role",
        ActionType.ADD_INSTRUCTION: "instructions",
        ActionType.ADD_CONTEXT: "contexts",
        ActionType.ADD_EXAMPLE: "examples",
        ActionType.ADD_TEXT: "user_data",
        ActionType.ADD_IMAGE_URL: "user_data",
        ActionType.ADD_HISTORY_MESSAGE: "history",
        ActionType.SET_HISTORY: "history",
        ActionType.ADD_LANGCHAIN_MESSAGE: "history",
        ActionType.SET_LLM_PARAMS: "llm_params",
        ActionType.WITH_METADATA: "metadata",
    }

    def evolve(self, action_type: ActionType, data: Any) -> "AIState":
        """
        中央状态演化器：将异构动作映射为内部状态更新

        根据 ActionType 枚举值，将输入数据规范化并合并到对应的状态字段。
        采用不可变设计，返回新的 AIState 实例而非修改当前实例。

        Args:
            action_type: 动作类型枚举，决定数据如何被处理和存储
            data: 待处理的原始数据，类型根据 action_type 而异

        Returns:
            AIState: 包含更新后状态的新实例

        Raises:
            ValueError: 当传入未定义的 action_type 时抛出

        Example:
            >>> state.evolve(ActionType.ADD_INSTRUCTION, "请帮我分析这段文本")
        """

        replace_actions = self._REPLACE_ACTIONS
        append_list_action = self._APPEND_LIST_ACTIONS
        merge_dict_action = self._MERGE_DICT_ACTIONS
        t_map = self._MAP

        if action_type not in t_map:
            raise InvalidActionTypeError(action_type)

        target_field = t_map[action_type]
        processed_val = self._normalize_data(action_type, data)

        # 3. 执行物理合并策略
        update_data = {}
        old_val = getattr(self, target_field)

        if action_type in append_list_action:
            update_data[target_field] = old_val + (
                processed_val if isinstance(processed_val, list) else [processed_val])
        elif action_type in merge_dict_action:
            update_data[target_field] = {**old_val, **processed_val}
        elif action_type in replace_actions:
            update_data[target_field] = processed_val

        return self.model_copy(update=update_data, deep=True)

    def _normalize_data(self, action_type: ActionType, data: Any) -> Any:
        """
        内部数据规范化器：将各阶段传来的原始数据转换为标准 JSON 协议

        根据 action_type 对数据进行预处理，确保数据格式符合内部协议规范。
        例如将纯文本转换为 {"type": "text", "text": "..."} 格式。

        Args:
            action_type: 动作类型枚举
            data: 原始输入数据

        Returns:
            Any: 规范化后的数据，通常是字典或列表
        """
        if action_type == ActionType.ADD_TEXT:
            return {"type": "text", "text": str(data)}

        if action_type == ActionType.ADD_IMAGE_URL:
            return {"type": "image_url", "image_url": {"url": str(data)}}

        if action_type == ActionType.ADD_LANGCHAIN_MESSAGE:
            # 自动处理 List[BaseMessage] 或单个 BaseMessage
            msgs = data if isinstance(data, list) else [data]
            return [self._lc_to_dict(m) for m in msgs]

        if action_type == ActionType.ADD_HISTORY_MESSAGE or action_type == ActionType.SET_HISTORY:
            # data 预期为 {"role": "...", "content": "..."}
            return data

        return data

    def _lc_to_dict(self, msg: Any) -> Dict[str, Any]:
        """
        LangChain 消息对象转换器：将 LangChain 消息对象转换为字典格式

        支持 SystemMessage, HumanMessage, AIMessage 等类型的自动识别和转换。

        Args:
            msg: LangChain 消息对象或字典

        Returns:
            Dict[str, Any]: 标准的 {"role": "...", "content": "..."} 格式字典
        """
        if isinstance(msg, SystemMessage):
            return {"role": "system", "content": msg.content}
        if isinstance(msg, HumanMessage):
            return {"role": "user", "content": msg.content}
        if isinstance(msg, AIMessage):
            return {"role": "assistant", "content": msg.content}
        if isinstance(msg, dict):
            return msg
        return {"role": "user", "content": str(msg)}

    def _compile_messages(self) -> List[Dict[str, Any]]:
        """
        消息编译器：将内部状态组装成符合大模型 API 协议的消息列表

        按照以下层次结构组装：
        1. System 层：身份 + 上下文 + 示例
        2. History 层：历史对话记录
        3. User 层：指令 + 数据

        Returns:
            List[Dict[str, Any]]: 符合 OpenAI/Anthropic 等主流模型协议的消息列表
        """
        messages = []
        # System 层 (Identity + Context + Examples)
        sys_content = []
        if self.system_role:
            sys_content.append(f"<identity>\n{self.system_role}\n</identity>")
        if self.contexts:
            ctx = "\n".join(self.contexts)
            sys_content.append(f"<knowledge>\n{ctx}\n</knowledge>")
        if self.examples:
            ex_str = "\n".join(
                [f"In: {e['input']}\nOut: {e['output']}" for e in self.examples]
            )
            sys_content.append(f"<examples>\n{ex_str}\n</examples>")

        if sys_content:
            sys_msg = "\n\n".join(sys_content)
        else:
            sys_msg = "You are a professional assistant."
        messages.append({"role": "system", "content": sys_msg})

        # History 层
        if self.history:
            messages.extend(self.history)

        # User 层 (Instructions + Data)
        user_parts = []
        if self.instructions:
            instr = "\n".join(self.instructions)
            user_parts.append(
                {"type": "text", "text": f"<instruction>\n{instr}\n</instruction>"}
            )

        has_image = False
        for data in self.user_data:
            # 此时 evolve 已经保证了 data 必含 type
            if data["type"] == "text":
                user_parts.append(
                    {"type": "text", "text": f"<data>\n{data['text']}\n</data>"}
                )
            elif data["type"] == "image_url":
                has_image = True
                user_parts.append(data)

        if not has_image:
            user_msg = "\n\n".join([p["text"] for p in user_parts])
            messages.append({"role": "user", "content": user_msg})
        else:
            messages.append({"role": "user", "content": user_parts})

        return messages

    def to_litellm_params(self) -> Dict[str, Any]:
        """
        LiteLLM 参数转换器：将内部配置转换为 LiteLLM API 调用参数

        处理 API 密钥解密、模型名称映射、超时配置等关键参数，
        确保敏感凭证在请求级别的隔离。

        Returns:
            Dict[str, Any]: 符合 LiteLLM acompletion() 接口的参数字典

        Raises:
            ValueError: 当模型配置不存在时抛出
        """
        conf = self.model
        if not conf:
            raise ModelConfigNotFoundError(
                context={"state_id": id(self)}
            )
        params = {
            "model": conf.model_name,
            "api_key": conf.api_key.get_secret_value(),
            "api_base": conf.base_url,
            "timeout": conf.timeout,
            "num_retries": self.llm_params.get("max_retries", conf.max_retries),
            "temperature": self.llm_params.get("temperature", 0.1),
            "metadata": self.metadata,
            "skip_validation": True,
        }
        if self.model_fallbacks:
            fallbacks = [
                {
                    "model": fb.model_name,
                    "api_key": fb.api_key.get_secret_value(),
                    "api_base": fb.base_url,
                }
                for fb in self.model_fallbacks
            ]
            params["fallbacks"] = fallbacks

        extra = {
            k: v
            for k, v in self.llm_params.items()
            if k not in ["temperature", "max_retries"]
        }
        params.update(extra)
        return params
