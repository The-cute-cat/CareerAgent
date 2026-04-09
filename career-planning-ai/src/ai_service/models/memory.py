"""
记忆相关的数据库模型
"""
from datetime import datetime
from typing import Optional

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel, Field
from sqlalchemy import String, Text, Float, Integer, BigInteger, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ai_service.models.base import Base


class Message(BaseModel):
    """消息模型（用于短期记忆）"""
    role: str = Field(..., description="角色：user/assistant/system")
    content: str = Field(..., description="消息内容")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")

    def to_langchain_message(self) -> BaseMessage:
        """转换为 LangChain 消息格式"""
        if self.role == "user":
            return HumanMessage(content=self.content)
        elif self.role == "assistant":
            return AIMessage(content=self.content)
        else:
            return SystemMessage(content=self.content)


class Memory(Base):
    """长期记忆表"""
    __tablename__ = "memories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True, comment="用户ID")
    session_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment="会话ID")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="记忆内容")
    memory_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="记忆类型：preference/decision/fact/goal")
    importance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5, comment="重要性评分(0-1)")
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5, comment="相关性评分(0-1)")
    recency_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5, comment="时效性评分(0-1)")
    uniqueness_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5, comment="独特性评分(0-1)")
    total_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5, comment="综合评分(0-1)")
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="额外元数据(JSON格式)")
    vector_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, comment="向量数据库中的ID")
    is_active: Mapped[bool] = mapped_column(Integer, nullable=False, default=1, comment="是否激活")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    __table_args__ = (
        Index('idx_user_session', 'user_id', 'session_id'),
        Index('idx_total_score', 'total_score'),
        Index('idx_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Memory(id={self.id}, user_id={self.user_id}, type={self.memory_type}, score={self.total_score:.2f})>"


class ConversationSession(Base):
    """会话表"""
    __tablename__ = "conversation_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment="会话ID")
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True, comment="用户ID")
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="会话标题")
    compressed_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="压缩后的摘要")
    message_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="消息数量")
    is_active: Mapped[bool] = mapped_column(Integer, nullable=False, default=1, comment="是否激活")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'session_id', name='uq_user_session'),
        Index('idx_user_session', 'user_id', 'session_id'),
    )
    
    def __repr__(self) -> str:
        return f"<ConversationSession(id={self.id}, session_id={self.session_id}, user_id={self.user_id})>"
