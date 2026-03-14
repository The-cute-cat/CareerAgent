# AI Engine 模块技术文档

> 基于范畴论思想的分段建造者模式 LLM 调用框架

---

## 目录

- [概述](#概述)
- [核心架构](#核心架构)
- [快速开始](#快速开始)
- [详细教程](#详细教程)
- [API 参考](#api-参考)
- [高级用法](#高级用法)
- [最佳实践](#最佳实践)
- [设计原理](#设计原理)
- [常见问题](#常见问题)

---

## 概述

### 什么是 AI Engine？

AI Engine 是一个封装了大语言模型（LLM）交互逻辑的统一框架，采用**分段建造者模式**（Staged Builder Pattern）设计。它将一次 AI 调用视为一个**状态演化过程**，通过代码接口强制约束开发者按照五个阶段进行操作，确保调用流程的正确性和逻辑严谨性。

### 核心特性

- **五阶段流水线**：Compute → Ingestion → Alignment → Projection → Evaluation
- **类型安全**：基于 Pydantic 的结构化输出验证
- **多模型支持**：通过 LiteLLM 支持 OpenAI、Azure、Anthropic、通义千问等主流模型
- **容错降级**：支持模型级别的 fallback 机制
- **流式输出**：支持打字机效果的实时文本生成
- **多模态输入**：支持文本和图像混合输入
- **LangChain 兼容**：无缝集成 LangChain 消息协议

### 设计理念

本框架借鉴范畴论（Category Theory）的思想，将 AI 调用抽象为**对象**（Object）和**态射**（Morphism）的组合：

- **对象**：`AIState` — 承载流水线状态的纯数据容器
- **态射**：`ActionType` — 定义合法的状态演化操作
- **态射组合**：通过链式调用将多个态射组合成完整的请求流程

---

## 核心架构

### 五阶段流水线

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI 调用流水线                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Stage 1          Stage 2           Stage 3          Stage 4       │
│  ┌─────────┐     ┌─────────┐       ┌─────────┐     ┌─────────┐     │
│  │ Compute │────▶│Ingestion│──────▶│Alignment│────▶│Projection│    │
│  │算力锚定  │     │上下文注入│       │行为对齐  │     │空间投射   │    │
│  └─────────┘     └─────────┘       └─────────┘     └─────────┘     │
│       │               │                 │               │          │
│  pick_brain()    InputStep         TuneStep        ShapeStep       │
│                                                                     │
│                           Stage 5                                  │
│                    ┌──────────────────┐                            │
│                    │   Evaluation     │                            │
│                    │    坍缩求值       │                            │
│                    └──────────────────┘                            │
│                           │                                        │
│              ┌────────────┴────────────┐                           │
│              ▼                         ▼                           │
│      StructActionStep           TextActionStep                     │
│       (结构化输出)                (文本输出)                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 阶段说明

| 阶段 | 名称 | 职责 | 对应类 | 强制性 |
|------|------|------|--------|--------|
| 1 | Compute（算力锚定） | 选择推理模型 | `AIEngine.pick_brain()` | ✅ 必须 |
| 2 | Ingestion（上下文注入） | 注入多层次提示词 | `InputStep` | ✅ 必须 |
| 3 | Alignment（行为对齐） | 调整推理参数 | `TuneStep` | ⚪ 可选 |
| 4 | Projection（空间投射） | 定义输出形态 | `ShapeStep` | ✅ 必须 |
| 5 | Evaluation（坍缩求值） | 执行调用获取结果 | `StructActionStep` / `TextActionStep` | ✅ 必须 |

### 模块组成

```
src/ai_service/engine/
├── __init__.py          # 包初始化
├── action_type.py       # 态射类型枚举
├── ai_state.py          # 状态容器（对象）
├── ai_engine.py         # 引擎与阶段类（态射）
└── README.md            # 本文档
```

---

## 快速开始

### 安装依赖

```bash
pip install litellm instructor pydantic langchain-core
```

### 基础示例：文本生成

```python
from ai_service.engine import AIEngine
from config import settings

# 1. 创建引擎实例
engine = AIEngine()

# 2. 构建并执行流水线
result = await (
    engine.pick_brain(settings.llm.qwen)
    .set_system_role("你是一个专业的翻译助手")
    .add_instruction("将以下英文翻译成中文")
    .add_text("Hello, World!")
    .next_step()  # 进入对齐阶段
    .next_step()  # 进入投射阶段
    .into_text()  # 选择文本输出
    .do()         # 执行调用
)

print(result)  # 输出: 你好，世界！
```

### 基础示例：结构化输出

```python
from pydantic import BaseModel
from ai_service.engine import AIEngine
from config import settings

# 定义输出结构
class Person(BaseModel):
    name: str
    age: int
    occupation: str

# 构建并执行流水线
engine = AIEngine()
person = await (
    engine.pick_brain(settings.llm.qwen)
    .add_text("John is a 28-year-old software engineer from Beijing.")
    .add_instruction("提取人物信息")
    .next_step()
    .next_step()
    .into_struct(Person)  # 选择结构化输出
    .do()
)

print(person)
# 输出: Person(name='John', age=28, occupation='software engineer')
```

---

## 详细教程

### Stage 1：算力锚定（Compute）

这是流水线的起点，负责选择推理模型。

```python
from ai_service.engine import AIEngine
from config import settings, LLM

engine = AIEngine()

# 基础用法：指定单个模型
pipeline = engine.pick_brain(settings.llm.qwen)

# 高级用法：配置容错降级
pipeline = engine.pick_brain(
    model=settings.llm.qwen,
    model_fallbacks=[
        settings.llm.deepseek,  # 主模型失败时降级到 DeepSeek
        settings.llm.gpt4o      # DeepSeek 也失败时降级到 GPT-4o
    ]
)
```

**模型配置说明：**

模型配置（`LLM` 类型）需要包含以下字段：
- `model_name`: 模型标识符（如 `qwen/qwen-max`）
- `api_key`: API 密钥（SecretStr 类型）
- `base_url`: API 基础地址
- `timeout`: 请求超时时间
- `max_retries`: 最大重试次数

### Stage 2：上下文注入（Ingestion）

这是提示词工程的核心阶段，支持多层次的信息注入。

#### 2.1 身份层：设置系统角色

```python
pipeline = (
    engine.pick_brain(model)
    .set_system_role("你是一个资深的 Python 开发专家，精通 FastAPI 框架")
)
```

#### 2.2 指令层：添加任务指令

```python
pipeline = (
    engine.pick_brain(model)
    .add_instruction("请分析以下代码的性能瓶颈")
    .add_instruction("输出格式：1. 问题列表 2. 优化建议")
)
```

#### 2.3 上下文层：注入知识库

```python
pipeline = (
    engine.pick_brain(model)
    .add_context("项目背景：这是一个高并发的电商系统，日活用户 100 万")
    .add_context("技术栈：Python 3.11 + FastAPI + PostgreSQL + Redis")
)
```

#### 2.4 示例层：Few-shot 学习

```python
pipeline = (
    engine.pick_brain(model)
    .add_example(
        input_val="今天天气真好，阳光明媚",
        output_val="正面"
    )
    .add_example(
        input_val="心情很糟糕，什么都不想做",
        output_val="负面"
    )
)
```

#### 2.5 数据层：添加待处理数据

```python
# 添加文本数据
pipeline = (
    engine.pick_brain(model)
    .add_text("文章标题：AI 的未来发展")
    .add_text("文章内容：人工智能正在改变我们的生活方式...")
)

# 添加图像数据（多模态）
pipeline = (
    engine.pick_brain(model)
    .add_text("请描述这张图片的内容")
    .add_image_url("https://example.com/image.jpg")
)

# 添加 Base64 编码的图像
pipeline = (
    engine.pick_brain(model)
    .add_image_url("data:image/jpeg;base64,/9j/4AAQSkZJRg...")
)
```

#### 2.6 历史层：多轮对话

```python
# 方式一：设置完整历史
history = [
    {"role": "user", "content": "什么是 Python？"},
    {"role": "assistant", "content": "Python 是一种高级编程语言..."},
    {"role": "user", "content": "它有什么特点？"}
]
pipeline = engine.pick_brain(model).set_history(history)

# 方式二：逐条添加历史
pipeline = (
    engine.pick_brain(model)
    .add_history_message("user", "什么是 Python？")
    .add_history_message("assistant", "Python 是一种高级编程语言...")
)

# 方式三：注入 LangChain 消息对象
from langchain_core.messages import HumanMessage, AIMessage

pipeline = (
    engine.pick_brain(model)
    .add_langchain_message([
        HumanMessage("什么是 Python？"),
        AIMessage("Python 是一种高级编程语言...")
    ])
)
```

### Stage 3：行为对齐（Alignment）

可选阶段，用于微调模型行为。

```python
# 设置 LLM 参数
pipeline = (
    engine.pick_brain(model)
    .add_text("写一首关于春天的诗")
    .next_step()  # 进入对齐阶段
    .set_llm_params(
        temperature=0.8,    # 提高创造性
        max_tokens=500,     # 限制输出长度
        top_p=0.95
    )
    .with_metadata(
        request_id="req-12345",
        user_id="user-001",
        session_id="sess-abc"
    )
    .next_step()  # 进入投射阶段
)
```

**常用 LLM 参数：**

| 参数 | 说明 | 建议值 |
|------|------|--------|
| `temperature` | 随机性控制 | 结构化任务: 0.1, 创意任务: 0.7-1.0 |
| `max_tokens` | 最大输出长度 | 根据任务需求设置 |
| `top_p` | 核采样概率 | 默认 0.9-1.0 |
| `frequency_penalty` | 频率惩罚 | 0.0-2.0 |
| `presence_penalty` | 存在惩罚 | 0.0-2.0 |

### Stage 4：空间投射（Projection）

定义输出数据的形态。

```python
# 选择结构化输出
step = (
    engine.pick_brain(model)
    .add_text("...")
    .next_step()
    .next_step()
    .into_struct(MySchema)  # 传入 Pydantic 模型类
)

# 选择文本输出
step = (
    engine.pick_brain(model)
    .add_text("...")
    .next_step()
    .next_step()
    .into_text()
)
```

### Stage 5：坍缩求值（Evaluation）

执行调用并获取结果。

#### 5.1 结构化输出执行

```python
from pydantic import BaseModel, Field
from typing import List

class AnalysisResult(BaseModel):
    """分析结果模型"""
    summary: str = Field(description="文本摘要")
    keywords: List[str] = Field(description="关键词列表")
    sentiment: str = Field(description="情感倾向")

result = await (
    engine.pick_brain(model)
    .add_text("人工智能正在改变各行各业...")
    .add_instruction("分析文本并提取关键信息")
    .next_step()
    .next_step()
    .into_struct(AnalysisResult)
    .do()
)

if result:
    print(f"摘要: {result.summary}")
    print(f"关键词: {result.keywords}")
    print(f"情感: {result.sentiment}")
```

#### 5.2 文本输出执行

```python
# 一次性返回完整文本
result = await (
    engine.pick_brain(model)
    .add_text("写一篇关于 AI 的短文")
    .next_step()
    .next_step()
    .into_text()
    .do()
)
print(result)

# 流式返回（打字机效果）
async for chunk in (
    engine.pick_brain(model)
    .add_text("讲一个故事")
    .next_step()
    .next_step()
    .into_text()
    .stream()
):
    print(chunk, end="", flush=True)
```

---

## API 参考

### AIEngine

AI 引擎的入口类，负责初始化客户端和启动流水线。

```python
class AIEngine:
    """
    AI 引擎：作为全系统的唯一调用入口点
    
    Attributes:
        struct_client: 结构化输出客户端（Instructor + LiteLLM）
        text_client: 文本输出客户端（LiteLLM）
    """
    
    def pick_brain(
        self, 
        model: LLM, 
        model_fallbacks: Optional[List[LLM]] = None
    ) -> InputStep:
        """
        开启新的推理流水线
        
        Args:
            model: 主模型配置对象
            model_fallbacks: 备选模型列表，用于容错降级
            
        Returns:
            InputStep: 上下文注入步骤
            
        Raises:
            ValueError: 当模型配置无效时抛出
        """
```

### InputStep

上下文注入步骤，支持多层次提示词构建。

```python
class InputStep(BaseStep):
    """上下文注入步骤：构建多层次的提示词架构"""
    
    def set_system_role(self, role: str) -> InputStep:
        """设置系统角色身份"""
        
    def set_history(self, history: List[Dict[str, Any]]) -> InputStep:
        """设置完整对话历史"""
        
    def add_history_message(self, role: str, content: str) -> InputStep:
        """追加单条对话历史"""
        
    def add_instruction(self, task: str) -> InputStep:
        """添加任务指令"""
        
    def add_context(self, knowledge: str) -> InputStep:
        """添加上下文知识"""
        
    def add_example(self, input_val: str, output_val: str) -> InputStep:
        """添加 Few-shot 示例"""
        
    def add_langchain_message(self, msg: List[BaseMessage]) -> InputStep:
        """注入 LangChain 消息对象"""
        
    def add_text(self, text: str) -> InputStep:
        """添加文本数据"""
        
    def add_image_url(self, base64_or_url: str) -> InputStep:
        """添加图像 URL"""
        
    def next_step(self) -> TuneStep:
        """
        完成数据注入，进入行为对齐阶段
        
        Raises:
            ValueError: 当没有任何有效输入时抛出
        """
```

### TuneStep

行为对齐步骤，用于调整推理参数。

```python
class TuneStep(BaseStep):
    """行为对齐步骤：调整推理参数与元数据"""
    
    def set_llm_params(self, **params: Any) -> TuneStep:
        """设置底层 LLM 参数"""
        
    def with_metadata(self, **kwargs: Any) -> TuneStep:
        """附加请求元数据"""
        
    def next_step(self) -> ShapeStep:
        """完成对齐，进入投射阶段"""
```

### ShapeStep

空间投射步骤，定义输出形态。

```python
class ShapeStep(BaseStep):
    """空间投射步骤：定义输出数据的形态"""
    
    def into_struct(self, schema: Type[T]) -> StructActionStep[T]:
        """
        投射为结构化输出
        
        Args:
            schema: 目标 Pydantic 模型类
            
        Returns:
            StructActionStep: 结构化输出执行步骤
        """
        
    def into_text(self) -> TextActionStep:
        """
        投射为文本输出
        
        Returns:
            TextActionStep: 文本输出执行步骤
        """
```

### StructActionStep[T]

结构化输出执行步骤。

```python
class StructActionStep(Generic[T], BaseStep):
    """结构化输出执行步骤：强制要求返回结构化 Pydantic 对象"""
    
    async def do(self) -> Optional[T]:
        """
        执行结构化提取
        
        Returns:
            Optional[T]: 成功时返回 Pydantic 对象，失败时返回 None
        """
```

### TextActionStep

文本输出执行步骤。

```python
class TextActionStep(BaseStep):
    """文本输出执行步骤：要求返回自然语言文本"""
    
    async def do(self) -> str:
        """
        执行文本生成：一次性返回完整文本
        
        Returns:
            str: LLM 生成的文本内容
        """
        
    async def stream(self) -> AsyncIterable[str]:
        """
        执行流式文本生成：逐字返回打字机效果
        
        Yields:
            str: 每次返回一个文本片段
        """
```

### AIState

内部状态容器，承载流水线数据。

```python
class AIState(BaseModel):
    """
    内部状态容器：承载流水线在各阶段间流转的上下文数据
    
    Attributes:
        model: 主模型配置
        model_fallbacks: 备选模型列表
        system_role: 系统角色身份定义
        instructions: 任务指令列表
        contexts: 上下文知识列表
        examples: Few-shot 示例列表
        user_data: 原始用户数据
        history: 多轮对话历史
        llm_params: LLM 运行参数
        metadata: 请求元数据
    """
    
    def evolve(self, action_type: ActionType, data: Any) -> AIState:
        """
        中央状态演化器
        
        Args:
            action_type: 动作类型枚举
            data: 待处理的原始数据
            
        Returns:
            AIState: 包含更新后状态的新实例
        """
        
    def _compile_messages(self) -> List[Dict[str, Any]]:
        """将内部状态组装成符合大模型 API 协议的消息列表"""
        
    def to_litellm_params(self) -> Dict[str, Any]:
        """将内部配置转换为 LiteLLM API 调用参数"""
```

### ActionType

态射类型枚举，定义合法的状态演化操作。

```python
class ActionType(str, Enum):
    """定义所有合法的态射动作类型"""
    
    # 身份与指令层
    SET_SYSTEM_ROLE = "SET_SYSTEM_ROLE"     # 设置系统角色身份
    ADD_INSTRUCTION = "ADD_INSTRUCTION"     # 追加任务指令
    ADD_CONTEXT = "ADD_CONTEXT"             # 注入上下文知识
    ADD_EXAMPLE = "ADD_EXAMPLE"             # 添加 Few-shot 示例
    
    # 消息与数据层
    ADD_TEXT = "ADD_TEXT"                   # 添加文本数据
    ADD_IMAGE_URL = "ADD_IMAGE_URL"         # 添加图像 URL
    ADD_HISTORY_MESSAGE = "ADD_HISTORY_MESSAGE"  # 追加单条对话历史
    SET_HISTORY = "SET_HISTORY"             # 设置完整对话历史
    ADD_LANGCHAIN_MESSAGE = "ADD_LANGCHAIN_MESSAGE"  # 注入 LangChain 消息
    
    # 参数与元数据层
    SET_LLM_PARAMS = "SET_LLM_PARAMS"       # 设置 LLM 运行参数
    WITH_METADATA = "WITH_METADATA"         # 附加元数据
```

---

## 高级用法

### 多模态视觉识别

```python
from pydantic import BaseModel
from typing import List

class ImageDescription(BaseModel):
    """图像描述结果"""
    main_subject: str
    colors: List[str]
    mood: str
    objects: List[str]

result = await (
    engine.pick_brain(settings.llm.gpt4o)  # 需要支持视觉的模型
    .set_system_role("你是一个专业的图像分析师")
    .add_instruction("分析图像并提取关键信息")
    .add_text("请详细描述这张图片")
    .add_image_url("https://example.com/photo.jpg")
    .next_step()
    .next_step()
    .into_struct(ImageDescription)
    .do()
)
```

### 流式对话机器人

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()
engine = AIEngine()

@app.post("/chat/stream")
async def chat_stream(message: str):
    async def generate():
        async for chunk in (
            engine.pick_brain(settings.llm.qwen)
            .set_system_role("你是一个友好的对话助手")
            .add_instruction("请用简洁的语言回答用户问题")
            .add_text(message)
            .next_step()
            .set_llm_params(temperature=0.7)
            .next_step()
            .into_text()
            .stream()
        ):
            yield chunk
    
    return StreamingResponse(generate(), media_type="text/plain")
```

### 复杂结构化输出

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Task(BaseModel):
    """任务模型"""
    title: str = Field(description="任务标题")
    description: str = Field(description="任务描述")
    priority: Priority = Field(description="优先级")
    estimated_hours: float = Field(description="预估工时")

class ProjectPlan(BaseModel):
    """项目计划"""
    project_name: str = Field(description="项目名称")
    summary: str = Field(description="项目摘要")
    tasks: List[Task] = Field(description="任务列表")
    total_hours: float = Field(description="总工时")

plan = await (
    engine.pick_brain(settings.llm.qwen)
    .set_system_role("你是一个专业的项目经理")
    .add_instruction("根据以下需求生成项目计划")
    .add_context("需求：开发一个用户管理系统，包含注册、登录、权限管理功能")
    .add_context("团队规模：3 人，技术栈 Python + FastAPI + PostgreSQL")
    .next_step()
    .set_llm_params(temperature=0.3)  # 结构化任务使用较低温度
    .next_step()
    .into_struct(ProjectPlan)
    .do()
)

if plan:
    print(f"项目: {plan.project_name}")
    print(f"总工时: {plan.total_hours} 小时")
    for task in plan.tasks:
        print(f"  - [{task.priority.value}] {task.title}")
```

### 容错降级策略

```python
# 配置多级降级链
result = await (
    engine.pick_brain(
        model=settings.llm.qwen,
        model_fallbacks=[
            settings.llm.deepseek,
            settings.llm.gpt4o,
        ]
    )
    .add_text("解释量子计算的原理")
    .next_step()
    .next_step()
    .into_text()
    .do()
)
# 如果 qwen 失败，自动降级到 deepseek，再失败则降级到 gpt4o
```

### RAG 场景集成

```python
from typing import List
from pydantic import BaseModel

class SearchResult(BaseModel):
    """搜索结果"""
    answer: str
    sources: List[str]
    confidence: float

async def rag_query(query: str, retrieved_docs: List[str]) -> SearchResult:
    """RAG 查询"""
    engine = AIEngine()
    
    # 构建上下文
    context = "\n\n".join([f"文档 {i+1}: {doc}" for i, doc in enumerate(retrieved_docs)])
    
    return await (
        engine.pick_brain(settings.llm.qwen)
        .set_system_role("你是一个专业的知识库助手，请基于提供的文档回答问题")
        .add_instruction("基于以下文档回答用户问题，并标注信息来源")
        .add_instruction("如果文档中没有相关信息，请明确说明")
        .add_context(context)
        .add_text(query)
        .next_step()
        .set_llm_params(temperature=0.1)  # RAG 场景使用低温度
        .next_step()
        .into_struct(SearchResult)
        .do()
    )
```

---

## 最佳实践

### 1. 提示词层次化设计

推荐按照以下层次构建提示词：

```python
pipeline = (
    engine.pick_brain(model)
    # 第 1 层：身份定义（可选但推荐）
    .set_system_role("你是一个 [角色] ，擅长 [领域]")
    # 第 2 层：上下文知识（RAG 场景必选）
    .add_context("背景知识...")
    # 第 3 层：Few-shot 示例（复杂任务推荐）
    .add_example("输入示例", "输出示例")
    # 第 4 层：任务指令（必须）
    .add_instruction("请执行以下任务...")
    # 第 5 层：待处理数据（必须）
    .add_text("数据内容...")
)
```

### 2. 温度参数选择

| 任务类型 | 推荐 temperature | 说明 |
|----------|------------------|------|
| 结构化提取 | 0.0 - 0.2 | 最确定性输出 |
| 分类任务 | 0.0 - 0.1 | 减少随机性 |
| RAG 问答 | 0.1 - 0.3 | 基于事实回答 |
| 翻译任务 | 0.2 - 0.4 | 保持一致性 |
| 创意写作 | 0.7 - 1.0 | 提高多样性 |

### 3. 结构化输出设计

```python
# ✅ 推荐：使用 Field 添加描述
class GoodModel(BaseModel):
    title: str = Field(description="文章标题，不超过 50 字")
    summary: str = Field(description="文章摘要，100-200 字")
    tags: List[str] = Field(description="文章标签，最多 5 个")

# ❌ 不推荐：缺少描述信息
class BadModel(BaseModel):
    title: str
    summary: str
    tags: List[str]
```

### 4. 错误处理

```python
# 结构化输出：检查 None
result = await pipeline.into_struct(MySchema).do()
if result is None:
    # 处理提取失败的情况
    return {"error": "提取失败"}

# 文本输出：捕获异常
try:
    result = await pipeline.into_text().do()
except Exception as e:
    log.error(f"生成失败: {e}")
    result = "服务暂时不可用，请稍后重试"
```

### 5. 流式输出的取消处理

```python
import asyncio

async def stream_with_timeout():
    try:
        async with asyncio.timeout(30):  # 30 秒超时
            async for chunk in pipeline.into_text().stream():
                yield chunk
    except asyncio.TimeoutError:
        yield "\n[响应超时，请重试]"
    except Exception as e:
        yield f"\n[发生错误: {e}]"
```

---

## 设计原理

### 范畴论视角

本框架借鉴范畴论的核心概念：

```
┌─────────────────────────────────────────────────────────────────┐
│                         范畴论映射                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Category Theory          AI Engine                            │
│   ─────────────────        ──────────                           │
│   Object (对象)      ───▶   AIState (状态容器)                   │
│   Morphism (态射)    ───▶   ActionType (演化操作)                │
│   Composition (组合)  ───▶   链式调用 (Pipeline)                 │
│   Functor (函子)     ───▶   Step Classes (阶段类)                │
│   Monad (单子)       ───▶   do()/stream() (执行方法)             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 状态不可变性

所有状态操作都返回新的 `AIState` 实例，遵循不可变设计原则：

```python
# 内部实现：model_copy 创建新实例
def evolve(self, action_type: ActionType, data: Any) -> "AIState":
    # ... 处理数据 ...
    return self.model_copy(update=update_data, deep=True)
```

### 消息编译协议

最终发送给 LLM 的消息结构：

```python
[
    {
        "role": "system",
        "content": "<identity>\n你是一个...\n</identity>\n\n<knowledge>\n...\n</knowledge>"
    },
    {
        "role": "user",
        "content": "<instruction>\n请执行任务...\n</instruction>\n\n<data>\n原始数据...\n</data>"
    }
]
```

---

## 常见问题

### Q1: 为什么必须调用 `next_step()`？

**A:** 这是分段建造者模式的核心约束。每个阶段有明确的职责边界，必须完成当前阶段才能进入下一阶段，这样可以：

1. 防止跳过必要的配置步骤
2. 在编译时（而非运行时）发现配置错误
3. 提供清晰的调用流程

### Q2: `into_struct()` 和 `into_text()` 有什么区别？

**A:**

| 特性 | `into_struct()` | `into_text()` |
|------|-----------------|---------------|
| 输出类型 | Pydantic 对象 | 字符串 |
| 验证 | 自动验证结构 | 无验证 |
| 底层实现 | Instructor + MD_JSON | LiteLLM 原生 |
| 适用场景 | 信息提取、分类 | 对话、内容生成 |

### Q3: 如何选择合适的模型？

**A:** 建议根据任务类型选择：

- **结构化提取**：推理能力强的模型（GPT-4o, Qwen-Max, DeepSeek-V3）
- **简单对话**：性价比高的模型（GPT-3.5, Qwen-Turbo）
- **多模态任务**：支持视觉的模型（GPT-4o, Qwen-VL）

### Q4: 流式输出和一次性输出如何选择？

**A:**

| 场景 | 推荐方式 |
|------|----------|
| 短文本生成（< 500 tokens） | `do()` 一次性返回 |
| 长文本生成（> 500 tokens） | `stream()` 流式返回 |
| 结构化输出 | 仅支持 `do()` |
| 实时对话界面 | `stream()` 流式返回 |

### Q5: 如何处理 API 调用失败？

**A:** 框架提供了多层次的容错机制：

1. **模型级降级**：配置 `model_fallbacks`
2. **重试机制**：通过 `llm_params.max_retries` 设置
3. **业务级降级**：在 Service 层捕获异常并返回默认值

```python
try:
    result = await pipeline.into_struct(Schema).do()
except Exception as e:
    log.error(f"API 调用失败: {e}")
    result = Schema.default_value()  # 返回默认值
```

---

## 更新日志

### v1.0.0 (2024-01)

- 初始版本发布
- 支持五阶段流水线架构
- 支持结构化输出和文本输出
- 支持多模态输入
- 支持流式输出

---

## 贡献指南

欢迎提交 Issue 和 Pull Request。在提交代码前，请确保：

1. 通过所有单元测试
2. 新增代码有完整的类型注解
3. 新增功能有对应的文档说明

---

## 许可证

MIT License
