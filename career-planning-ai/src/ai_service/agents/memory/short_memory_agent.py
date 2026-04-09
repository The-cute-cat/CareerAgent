"""
短期记忆智能体 - ShortMemoryAgent

职责：
1. 管理最近 N 轮对话历史
2. 存储在 Redis 中
3. 支持对话压缩
4. 提供对话上下文构建

注意：Redis 键使用 (user_id, session_id) 组合，支持不同用户有相同 session_id
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from langchain_core.messages import BaseMessage

from ai_service.models.memory import Message
from ai_service.agents import log as logger

if TYPE_CHECKING:
    from ai_service.agents.memory.memory_compression_agent import MemoryCompressionAgent
from ai_service.services.redis_service import RedisService
from config import settings

__all__ = [
    "ShortMemoryAgent",
    "short_memory_agent",
]


class ShortMemoryAgent:
    """
    短期记忆智能体
    
    管理最近 N 轮对话历史，存储在 Redis 中。
    当对话过长时，自动触发压缩。
    """

    MAX_MESSAGES = settings.conversation.memory.short.max_messages
    MAX_TOKENS = settings.conversation.memory.short.max_tokens
    COMPRESSION_TRIGGER_RATIO = settings.conversation.memory.short.compression_trigger_raito
    KEEP_RECENT_MESSAGES = settings.conversation.memory.short.keep_recent_messages

    def __init__(
            self,
            redis_prefix: str = "conversation",
            compression_agent: Optional["MemoryCompressionAgent"] = None
    ):
        """
        初始化短期记忆智能体
        
        Args:
            redis_prefix: Redis 键前缀
            compression_agent: 对话压缩智能体实例
        """
        from ai_service.agents.memory.memory_compression_agent import MemoryCompressionAgent
        self.redis = RedisService.get_instance(prefix=redis_prefix)
        self.compression_agent = compression_agent or MemoryCompressionAgent()
        logger.info(f"ShortMemoryAgent 初始化完成，Redis可用: {self.redis.is_available}")

    @staticmethod
    def _build_key(user_id: str, session_id: str) -> str:
        """构建 Redis 键名（包含 user_id 以支持不同用户有相同 session_id）"""
        return f"short_memory:{user_id}:{session_id}"

    async def get_messages(
            self,
            user_id: str,
            session_id: str
    ) -> list[Message]:
        """
        获取会话的所有消息
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            
        Returns:
            消息列表
        """
        key = self._build_key(user_id, session_id)
        messages_data = self.redis.get(key, default=[])
        if isinstance(messages_data, list):
            return [Message(**msg) for msg in messages_data]
        return []

    async def add_message(
            self,
            user_id: str,
            session_id: str,
            role: str,
            content: str,
            auto_compress: bool = True
    ) -> list[Message]:
        """
        添加消息到短期记忆
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            role: 角色（user/assistant/system）
            content: 消息内容
            auto_compress: 是否自动压缩
            
        Returns:
            更新后的消息列表
        """
        messages = await self.get_messages(user_id, session_id)
        new_message = Message(role=role, content=content)
        messages.append(new_message)
        if auto_compress and self.should_compress(messages):
            logger.info(f"用户 {user_id} 会话 {session_id} 触发压缩条件，开始压缩...")
            messages = await self.compress_messages(user_id, session_id, messages)
        key = self._build_key(user_id, session_id)
        messages_data = [msg.model_dump() for msg in messages]
        self.redis.set(key, messages_data, ttl=None)
        logger.debug(f"用户 {user_id} 会话 {session_id} 添加消息，当前消息数: {len(messages)}")
        return messages

    def should_compress(self, messages: list[Message]) -> bool:
        """
        判断是否需要压缩
        
        Args:
            messages: 消息列表
            
        Returns:
            是否需要压缩
        """
        if len(messages) <= self.KEEP_RECENT_MESSAGES:
            return False
        if len(messages) >= self.MAX_MESSAGES * self.COMPRESSION_TRIGGER_RATIO:
            return True
        total_tokens = self._estimate_tokens(messages)
        if total_tokens >= self.MAX_TOKENS * self.COMPRESSION_TRIGGER_RATIO:
            return True
        return False

    @staticmethod
    def _estimate_tokens(messages: list[Message]) -> int:
        """
        估算消息的 token 数量
        
        Args:
            messages: 消息列表
            
        Returns:
            估算的 token 数量
        """
        total = 0
        for msg in messages:
            chinese_chars = sum(1 for c in msg.content if '\u4e00' <= c <= '\u9fff')
            english_words = len([w for w in msg.content.split() if w.isascii()])
            total += int(chinese_chars * 0.5 + english_words * 1.3)
        return total

    async def compress_messages(
            self,
            user_id: str,
            session_id: str,
            messages: list[Message]
    ) -> list[Message]:
        """
        压缩消息列表
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            messages: 消息列表
            
        Returns:
            压缩后的消息列表
        """
        if len(messages) <= self.KEEP_RECENT_MESSAGES:
            return messages
        to_compress = messages[:-self.KEEP_RECENT_MESSAGES]
        to_keep = messages[-self.KEEP_RECENT_MESSAGES:]
        compressed_summary = await self.compression_agent.compress(to_compress)
        summary_message = Message(
            role="system",
            content=f"[历史对话摘要]\n{compressed_summary}",
            timestamp=datetime.now().isoformat()
        )
        compressed_messages = [summary_message] + to_keep
        logger.info(
            f"用户 {user_id} 会话 {session_id} 压缩完成: {len(messages)} -> {len(compressed_messages)} 条消息"
        )
        return compressed_messages

    async def remove_last_message(
            self,
            user_id: str,
            session_id: str
    ) -> bool:
        """
        移除短期记忆中的最后一条消息

        Args:
            user_id: 用户 ID
            session_id: 会话 ID

        Returns:
            是否成功移除
        """
        messages = await self.get_messages(user_id, session_id)
        if not messages:
            return False
        messages.pop()
        key = self._build_key(user_id, session_id)
        messages_data = [msg.model_dump() for msg in messages]
        self.redis.set(key, messages_data, ttl=None)
        return True

    async def clear(
            self,
            user_id: str,
            session_id: str
    ) -> bool:
        """
        清除会话的短期记忆
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            
        Returns:
            是否成功
        """
        key = self._build_key(user_id, session_id)
        return self.redis.delete(key)

    async def get_context_messages(
            self,
            user_id: str,
            session_id: str,
            limit: Optional[int] = None
    ) -> list[BaseMessage]:
        """
        获取用于构建上下文的 LangChain 消息列表
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            limit: 限制返回的消息数量
            
        Returns:
            LangChain 消息列表
        """
        messages = await self.get_messages(user_id, session_id)

        if limit:
            messages = messages[-limit:]

        return [msg.to_langchain_message() for msg in messages]

    async def get_message_count(
            self,
            user_id: str,
            session_id: str
    ) -> int:
        """
        获取消息数量
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            
        Returns:
            消息数量
        """
        messages = await self.get_messages(user_id, session_id)
        return len(messages)


short_memory_agent = ShortMemoryAgent(redis_prefix="conversation")
