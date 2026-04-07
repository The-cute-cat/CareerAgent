"""
记忆压缩智能体 - MemoryCompressionAgent

职责：
1. 压缩过长的对话历史
2. 生成对话摘要
3. 保留关键信息和决策
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ai_service.models.memory import Message
from ai_service.agents import log as logger
from ai_service.services.prompt_loader import prompt_loader
from config import settings

__all__=[
    "MemoryCompressionAgent",
    "memory_compression_agent",
]

class MemoryCompressionAgent:
    """
    记忆压缩智能体
    
    使用 LLM 将长对话压缩为简洁的摘要，
    保留关键决策、重要事实和用户偏好。
    """
    def __init__(self):
        """初始化压缩智能体"""
        self.llm = ChatOpenAI(
            base_url=settings.conversation.memory.compression.base_url,
            model=settings.conversation.memory.compression.model_name,
            api_key=settings.conversation.memory.compression.api_key.get_secret_value(),
            temperature=settings.conversation.memory.compression.extra.get("temperature", 0.2),
            timeout=settings.conversation.memory.compression.timeout,
            max_retries=settings.conversation.memory.compression.max_retries,
        )
        logger.info("MemoryCompressionAgent 初始化完成")
    
    async def compress(self, messages: list[Message]) -> str:
        """
        压缩对话消息列表
        
        Args:
            messages: 消息列表
            
        Returns:
            压缩后的摘要文本
        """
        if not messages:
            return ""
        if len(messages) <= 3:
            return self._simple_summarize(messages)
        conversation_text = self._format_messages(messages)
        prompt = ChatPromptTemplate.from_template(prompt_loader.small_prompts["compression_prompt"])
        chain = prompt | self.llm
        try:
            response = await chain.ainvoke({"conversation": conversation_text})
            summary = response.content.strip()
            logger.info(f"对话压缩完成，原文长度: {len(conversation_text)}，摘要长度: {len(summary)}")
            return summary
        except Exception as e:
            logger.error(f"对话压缩失败: {e}")
            # 失败时返回简单摘要
            return self._simple_summarize(messages)
    
    @staticmethod
    def _format_messages(messages: list[Message]) -> str:
        """
        格式化消息列表为文本
        
        Args:
            messages: 消息列表
            
        Returns:
            格式化后的文本
        """
        lines = []
        for msg in messages:
            role_name = {
                "user": "用户",
                "assistant": "助手",
                "system": "系统"
            }.get(msg.role, msg.role)
            lines.append(f"{role_name}: {msg.content}")
        return "\n".join(lines)
    
    @staticmethod
    def _simple_summarize(messages: list[Message]) -> str:
        """
        简单摘要（当 LLM 调用失败时使用）
        
        Args:
            messages: 消息列表
            
        Returns:
            简单摘要
        """
        if not messages:
            return ""
        # 提取用户消息
        user_messages = [msg for msg in messages if msg.role == "user"]
        if not user_messages:
            return "无有效对话内容"
        # 提取前几条用户消息
        summary_parts = []
        for msg in user_messages[:5]:
            # 截取每条消息的 前50个字符
            content = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
            summary_parts.append(content)
        return "用户主要讨论了：" + "；".join(summary_parts)
    
    async def extract_key_points(self, messages: list[Message]) -> list[str]:
        """
        从对话中提取关键点
        
        Args:
            messages: 消息列表
            
        Returns:
            关键点列表
        """
        if not messages:
            return []
        # 使用压缩生成的摘要作为关键点
        summary = await self.compress(messages)
        # 将摘要按句号分割为关键点
        key_points = []
        for sentence in summary.split("。"):
            sentence = sentence.strip()
            if sentence and len(sentence) > 5:
                key_points.append(sentence)
        return key_points[:5]  # 最多返回5个关键点

memory_compression_agent = MemoryCompressionAgent()