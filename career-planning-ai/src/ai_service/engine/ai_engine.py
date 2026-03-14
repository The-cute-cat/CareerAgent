from typing import (
    Type,
    TypeVar,
    Optional,
    Any,
    AsyncIterable,
    Dict,
    List,
    Generic,
)
import litellm
import instructor
from pydantic import BaseModel, Field
from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
)
from config import LLM
from ai_service.engine.ai_state import AIState  # 引入 AIState 类
from ai_service.utils.logger_handler import log
from ai_service.engine.action_type import ActionType

"""
AI引擎模块,封装了与大模型交互的逻辑，提供统一的接口供上层调用，
支持动态配置和参数调整，方便测试和调试。
采用分段建造者模式，将请求构建和模型调用分离，
增强代码的可维护性和可测试性。

阶段设计：
将一次 AI 调用视为一个状态演化过程。通过代码接口强制约束，
开发者必须按照以下五个范畴阶段进行操作：
Compute (算力锚定),选择推理大脑(Model Selection)。
Ingestion (上下文注入),多模态数据输入(Data Ingestion)。
Alignment (行为对齐),推理参数与角色预设(Behavior Tuning)。
Projection (空间投射),输出数据形态定义(Output Shaping)。
Evaluation (坍缩求值),触发 I/O 并获取结果(Action/Execution)。
每个阶段都返回一个新的对象，只有完成当前阶段的操作后才能进入下一阶段，
确保调用流程的正确性和逻辑严谨性。

设计原则：
单一职责：每个阶段对象只负责一个方面的配置或操作，职责清晰。
链式调用：通过方法返回新的阶段对象，支持链式调用，提升开发体验。
错误处理：在每个阶段的关键操作中加入异常捕获和日志记录，确保问题可追踪。
兼容性：设计时考虑到不同大模型的接口差异，尽量提供统一的调用方式，
        方便未来扩展和适配。
"""

T = TypeVar("T", bound=BaseModel)


# =====================================================================
# 阶段基类：流水线级的状态，管理各阶段的初始化
# =====================================================================
class BaseStep:
    """
    阶段基类：流水线级的状态管理器

    负责在各阶段间传递共享资源和上下文状态。
    作为所有阶段类(InputStep, TuneStep, ShapeStep, *ActionStep)的基类。

    Attributes:
        _state (AIState): 当前流水线的状态对象，承载所有配置数据
        _engine (AIEngine): 引擎实例，提供模型调用能力
    """

    def __init__(self, state: "AIState", engine: "AIEngine") -> None:
        """
        初始化阶段基类

        Args:
            state: 当前流水线的状态对象
            engine: AI 引擎实例
        """
        self._state = state
        self._engine = engine


# =====================================================================
# 阶段 5：坍缩与求值 (The Execution Monad)
# =====================================================================
class StructActionStep(Generic[T], BaseStep):
    """
    结构化输出执行步骤：强制要求返回结构化 Pydantic 对象

    使用 Instructor 库将 LLM 输出强制转换为指定的 Pydantic 模型，
    适用于需要精确结构化数据提取的场景（如信息抽取、分类等）。

    Type Parameters:
        T: Pydantic BaseModel 子类，定义输出数据的结构

    Attributes:
        schema (Type[T]): 目标 Pydantic 模型类
    """

    def __init__(self, _state: AIState, _engine: "AIEngine", schema: Type[T]) -> None:
        """
        初始化结构化输出步骤

        Args:
            _state: 当前流水线状态
            _engine: AI 引擎实例
            schema: 目标 Pydantic 模型类
        """
        super().__init__(_state, _engine)
        self.schema = schema

    async def do(self) -> Optional[T]:
        """
        执行结构化提取：调用 LLM 并返回 Pydantic 对象

        使用 MD_JSON 模式避免依赖脆弱的 tool_call 协议，
        让 AI 输出 Markdown JSON 代码块后再解析。

        Returns:
            Optional[T]: 成功时返回 Pydantic 对象，失败时返回 None

        Example:
            >>> class Person(BaseModel):
            ...     name: str
            ...     age: int
            >>> result = await engine.pick_brain(model)\\
            ...     .add_text("John is 25 years old")\\
            ...     .next_step().next_step().into_struct(Person).do()
        """
        try:
            messages = self._state._compile_messages()
            # 准备参数字典，避免传递空的 fallbacks 报错
            kwargs = self._state.to_litellm_params()
            kwargs["response_model"] = (
                self.schema
            )  # 直接传入 Pydantic 模型类，LiteLLM 会自动处理结构化输出
            kwargs["messages"] = messages  # 直接传入编译好的消息列表，避免重复处理
            # 【核心修复点】: 显式指定模式为 MD_JSON
            # 这会告诉 Instructor：不要走脆弱的 tool_call 协议
            # 而是让 AI 输出 ```json ... ``` 块，然后我们来解析
            return await self._engine.struct_client.chat.completions.create(**kwargs)
        except Exception as e:
            log.error(f"结构化提取失败[{self.schema.__name__}]: {e}")
            return None


class TextActionStep(BaseStep):
    """
    文本输出执行步骤：要求返回自然语言文本

    适用于开放式对话、内容生成等不需要严格结构化输出的场景。
    支持一次性返回和流式返回两种模式。

    Attributes:
        继承自 BaseStep
    """

    async def do(self) -> str:
        """
        执行文本生成：一次性返回完整文本

        适用于短文本生成或需要完整结果的场景。

        Returns:
            str: LLM 生成的文本内容，失败时返回错误提示

        Raises:
            Exception: 当 API 调用失败时向上抛出异常

        Example:
            >>> result = await engine.pick_brain(model)\\
            ...     .add_text("写一首关于春天的诗")\\
            ...     .next_step().next_step().into_text().do()
        """
        try:
            messages = self._state._compile_messages()
            kwargs = self._state.to_litellm_params()
            kwargs["messages"] = messages  # 直接传入编译好的消息列表，避免重复处理
            response = await self._engine.text_client(**kwargs)

            content = response.choices[0].message.content
            return content if content else "没有返回任何内容。"
        except Exception as e:
            # 建议：生产环境下不要吞掉异常，向上抛出让 Service 层决定如何降级
            log.error(f"文本生成失败: {e}", exc_info=True)
            raise  # 或者返回自定义的错误枚举

    async def stream(self) -> AsyncIterable[str]:
        """
        执行流式文本生成：逐字返回打字机效果

        适用于长文本生成、实时对话等需要即时反馈的场景。

        Yields:
            str: 每次返回一个文本片段（token）

        Example:
            >>> async for chunk in engine.pick_brain(model)\\
            ...     .add_text("讲一个故事")\\
            ...     .next_step().next_step().into_text().stream():
            ...     print(chunk, end="", flush=True)
        """
        try:
            messages = self._state._compile_messages()
            kwargs = self._state.to_litellm_params()
            kwargs["stream"] = True  # 开启流式输出
            kwargs["messages"] = messages

            response = await self._engine.text_client(**kwargs)
            # 异步迭代生成器
            async for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            log.error(f"流式生成中断: {e}")
            yield "\n[网络连接中断，请稍后重试]"


# =====================================================================
# 阶段 4：空间投射 (The Projection Category)
# =====================================================================
class ShapeStep(BaseStep):
    """
    空间投射步骤：定义输出数据的形态

    作为从配置到执行的过渡阶段，负责选择最终的输出格式：
    - into_struct(): 结构化输出，返回 Pydantic 对象
    - into_text(): 自然语言输出，返回文本

    Attributes:
        继承自 BaseStep
    """

    def into_struct(self, schema: Type[T]) -> StructActionStep[T]:
        """
        投射为结构化输出：返回 Pydantic 对象

        Args:
            schema (Type[T]): 目标 Pydantic 模型类，定义输出结构

        Returns:
            StructActionStep[T]: 结构化输出执行步骤

        Example:
            >>> step = engine.pick_brain(model).add_text("...").next_step().next_step()
            >>> result = await step.into_struct(MySchema).do()
        """
        optimized_state = self._state
        if "temperature" not in optimized_state.llm_params:
            optimized_state = optimized_state.evolve(
                ActionType.SET_LLM_PARAMS, {"temperature": 0.1}
            )
        return StructActionStep(self._state, self._engine, schema)

    def into_text(self) -> TextActionStep:
        """
        投射为文本输出：返回自然语言

        Returns:
            TextActionStep: 文本输出执行步骤

        Example:
            >>> step = engine.pick_brain(model).add_text("...").next_step().next_step()
            >>> result = await step.into_text().do()
        """
        return TextActionStep(self._state, self._engine)


# =====================================================================
# 阶段 3：行为对齐 (The Behavior Category)
# =====================================================================
class TuneStep(BaseStep):
    """
    行为对齐步骤：调整推理参数与元数据

    用于微调 LLM 的行为特性，如温度、重试次数、请求元数据等。
    这是可选的阶段，可以直接调用 next_step() 跳过。

    Attributes:
        继承自 BaseStep
    """

    def set_llm_params(self, **params: Any) -> "TuneStep":
        """
        设置底层 LLM 参数：提供最大灵活性

        支持所有 LiteLLM 支持的参数，如 temperature, max_tokens, top_p 等。

        Args:
            **params: LLM 参数键值对

        Returns:
            TuneStep: 新的对齐步骤实例

        Example:
            >>> step = engine.pick_brain(model).add_text("...").next_step()\\
            ...     .set_llm_params(temperature=0.7, max_tokens=1000)
        """
        return TuneStep(self._state.evolve(ActionType.SET_LLM_PARAMS, params), self._engine)

    def with_metadata(self, **kwargs: Any) -> "TuneStep":
        """
        附加请求元数据：用于追踪、监控和调试

        元数据会随请求传递，可用于日志记录、性能监控等场景。

        Args:
            **kwargs: 元数据键值对

        Returns:
            TuneStep: 新的对齐步骤实例

        Example:
            >>> step.with_metadata(request_id="req-123", user_id="user-456")
        """
        return TuneStep(self._state.evolve(ActionType.WITH_METADATA, kwargs), self._engine)

    def next_step(self) -> ShapeStep:
        """
        完成对齐，进入投射阶段

        Returns:
            ShapeStep: 空间投射步骤实例
        """
        return ShapeStep(self._state, self._engine)


# =====================================================================
# 阶段 2：上下文注入 (The Information Category)
# =====================================================================
class InputStep(BaseStep):
    """
    上下文注入步骤：构建多层次的提示词架构

    负责注入身份、指令、上下文、示例、数据等多层次信息，
    支持文本和多模态（图像）输入，是流水线的核心构建阶段。

    Attributes:
        继承自 BaseStep
    """

    def set_system_role(self, role: str) -> "InputStep":
        """
        设置系统角色身份：定义 AI 的核心身份

        这是提示词工程的第一层，决定 AI 的基本行为模式和视角。
        通常设置为专家身份，如"你是一个专业的翻译助手"。

        Args:
            role (str): 角色身份描述

        Returns:
            InputStep: 新的输入步骤实例

        Example:
            >>> engine.pick_brain(model).set_system_role("你是一个资深的 Python 开发专家")
        """
        return InputStep(self._state.evolve(ActionType.SET_SYSTEM_ROLE, role), self._engine)

    def set_history(self, history: List[Dict[str, Any]]) -> "InputStep":
        """
        设置完整对话历史：支持多轮对话场景

        一次性设置完整的对话历史记录，通常用于恢复会话上下文。

        Args:
            history (List[Dict[str, Any]]): 对话历史列表，
                格式为 [{"role": "user/assistant", "content": "..."}]

        Returns:
            InputStep: 新的输入步骤实例

        Example:
            >>> history = [
            ...     {"role": "user", "content": "你好"},
            ...     {"role": "assistant", "content": "你好！"}
            ... ]
            >>> engine.pick_brain(model).set_history(history)
        """
        return InputStep(
            self._state.evolve(ActionType.SET_HISTORY, history), self._engine
        )

    def add_history_message(self, role: str, content: str) -> "InputStep":
        """
        追加单条对话历史：逐步构建对话上下文

        Args:
            role (str): 角色，可选 "user", "assistant", "system"
            content (str): 消息内容

        Returns:
            InputStep: 新的输入步骤实例

        Example:
            >>> engine.pick_brain(model)\\
            ...     .add_history_message("user", "什么是 Python？")\\
            ...     .add_history_message("assistant", "Python 是一种编程语言...")
        """
        new_message = {"role": role, "content": content}
        return InputStep(
            self._state.evolve(ActionType.ADD_HISTORY_MESSAGE, new_message),
            self._engine,
        )

    def add_instruction(self, task: str) -> "InputStep":
        """
        添加任务指令：定义具体的执行动作

        这是提示词工程的核心层，告诉 AI 需要完成什么任务。
        支持链式调用多次添加，形成多步骤指令。

        Args:
            task (str): 任务指令描述

        Returns:
            InputStep: 新的输入步骤实例

        Example:
            >>> engine.pick_brain(model)\\
            ...     .add_instruction("请分析以下文本的情感")\\
            ...     .add_instruction("输出格式：正面/负面/中性")
        """
        return InputStep(
            self._state.evolve(ActionType.ADD_INSTRUCTION, task), self._engine
        )

    def add_context(self, knowledge: str) -> "InputStep":
        """
        添加上下文知识：注入背景信息或行业标准

        为 AI 提供必要的背景知识，帮助其更好地理解任务。
        适用于 RAG（检索增强生成）场景。

        Args:
            knowledge (str): 上下文知识内容

        Returns:
            InputStep: 新的输入步骤实例

        Example:
            >>> engine.pick_brain(model)\\
            ...     .add_context("公司背景：这是一家成立于 2020 年的 AI 初创公司...")
        """
        return InputStep(
            self._state.evolve(ActionType.ADD_CONTEXT, knowledge), self._engine
        )

    def add_example(self, input_val: str, output_val: str) -> "InputStep":
        """
        添加 Few-shot 示例：提供输入输出样例

        通过示例教学，帮助 AI 理解期望的输出格式和风格。

        Args:
            input_val (str): 示例输入
            output_val (str): 期望的示例输出

        Returns:
            InputStep: 新的输入步骤实例

        Example:
            >>> engine.pick_brain(model)\\
            ...     .add_example("今天天气真好", "正面")\\
            ...     .add_example("我很难过", "负面")
        """
        example_data = {"input": input_val, "output": output_val}
        return InputStep(
            self._state.evolve(ActionType.ADD_EXAMPLE, example_data), self._engine
        )

    def add_langchain_message(self, msg: List[BaseMessage]) -> "InputStep":
        """
        注入 LangChain 消息对象：兼容 LangChain 生态

        自动将 LangChain 的消息对象转换为内部协议格式，
        方便与 LangChain 工作流集成。

        Args:
            msg (List[BaseMessage]): LangChain 消息对象列表

        Returns:
            InputStep: 新的输入步骤实例

        Example:
            >>> from langchain_core.messages import HumanMessage
            >>> engine.pick_brain(model).add_langChain_message([HumanMessage("你好")])
        """
        return InputStep(
            self._state.evolve(ActionType.ADD_LANGCHAIN_MESSAGE, msg), self._engine
        )

    def add_text(self, text: str) -> "InputStep":
        """
        添加文本数据：提供待处理的原始文本

        支持链式多次添加，数据会被合并到 user 消息中。

        Args:
            text (str): 文本内容

        Returns:
            InputStep: 新的输入步骤实例

        Example:
            >>> engine.pick_brain(model)\\
            ...     .add_text("文章标题：AI 的未来")\\
            ...     .add_text("文章内容：人工智能正在改变世界...")
        """
        return InputStep(
            self._state.evolve(ActionType.ADD_TEXT, text), self._engine
        )

    def add_image_url(self, base64_or_url: str) -> "InputStep":
        """
        添加图像 URL：支持多模态视觉识别

        支持传入图像 URL 或 Base64 编码的图像数据，
        需要模型支持视觉能力（如 GPT-4V, Qwen-VL 等）。

        Args:
            base64_or_url (str): 图像 URL 或 Base64 编码字符串

        Returns:
            InputStep: 新的输入步骤实例

        Example:
            >>> engine.pick_brain(model)\\
            ...     .add_text("请描述这张图片")\\
            ...     .add_image_url("https://example.com/image.jpg")
        """
        return InputStep(
            self._state.evolve(ActionType.ADD_IMAGE_URL, base64_or_url), self._engine
        )

    def next_step(self) -> TuneStep:
        """
        完成数据注入，进入行为对齐阶段

        验证至少注入了指令、数据或历史记录中的一项，
        否则抛出异常提示用户补充必要信息。

        Returns:
            TuneStep: 行为对齐步骤实例

        Raises:
            ValueError: 当没有任何有效输入时抛出

        Example:
            >>> tune_step = engine.pick_brain(model)\\
            ...     .add_text("你好")\\
            ...     .next_step()
        """
        has_input = (
            self._state.user_data
            or self._state.instructions
            or self._state.history
        )
        if not has_input:
            raise ValueError(
                "编译错误：必须至少注入 指令、数据 或 历史记录 中的一项。"
            )
        return TuneStep(self._state, self._engine)


# =====================================================================
# 阶段 1：算力锚定 (The Compute Category)
# =====================================================================
class AIEngine:
    """
    AI 引擎：作为全系统的唯一调用入口点

    采用分段建造者模式，将 AI 调用拆分为五个强制阶段：
    1. Compute (算力锚定) - pick_brain(): 选择推理模型
    2. Ingestion (上下文注入) - InputStep: 注入多层次数据
    3. Alignment (行为对齐) - TuneStep: 调整推理参数
    4. Projection (空间投射) - ShapeStep: 定义输出形态
    5. Evaluation (坍缩求值) - *ActionStep: 执行调用

    Attributes:
        struct_client: 结构化输出客户端（Instructor + LiteLLM）
        text_client: 文本输出客户端（LiteLLM）

    Example:
        >>> engine = AIEngine()
        >>> result = await engine.pick_brain(model)\\
        ...     .set_system_role("你是一个专业的翻译助手")\\
        ...     .add_instruction("将以下英文翻译成中文")\\
        ...     .add_text("Hello, World!")\\
        ...     .next_step().next_step().into_text().do()
    """

    # ==========================================
    # 层级 1：全局共享资源 (应用级单例)
    # ==========================================
    # 应用启动时初始化一次，所有流水线共享
    _converter = instructor.from_litellm(
        litellm.acompletion, mode=instructor.Mode.MD_JSON
    )

    def __init__(self) -> None:
        """
        初始化 AI 引擎实例

        创建流水线级的客户端实例，确保并发安全。
        """
        # ==========================================
        # 层级 2：流水线级隔离资源 (每次 pick_brain 新建)
        # ==========================================
        # 每条流水线独立拥有，随流水线销毁，天然并发安全
        self.struct_client = self._converter
        self.text_client = litellm.acompletion

    def pick_brain(
        self, model: LLM, model_fallbacks: Optional[List[LLM]] = None
    ) -> InputStep:
        """
        开启新的推理流水线：选择推理大脑

        这是流水线的起点，必须指定一个有效的模型配置。
        支持设置备选模型列表，在主模型失败时自动降级。

        Args:
            model (LLM): 主模型配置对象，包含 API 密钥、模型名称等
            model_fallbacks (Optional[List[LLM]]): 备选模型列表，用于容错降级

        Returns:
            InputStep: 上下文注入步骤，开始构建提示词

        Raises:
            ValueError: 当模型配置无效时抛出

        Example:
            >>> from config import settings
            >>> engine = AIEngine()
            >>> pipeline = engine.pick_brain(
            ...     model=settings.llm.qwen,
            ...     model_fallbacks=[settings.llm.deepseek]
            ... )
        """
        state = AIState(
            model=model,
            model_fallbacks=model_fallbacks or []
        )

        if not state.model:
            raise ValueError("编译错误：必须指定一个有效的模型名称")

        return InputStep(state, self)
