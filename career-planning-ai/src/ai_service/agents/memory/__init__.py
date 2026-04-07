"""
记忆智能体模块

提供完整的记忆管理功能：
- 短期记忆（对话历史）
- 长期记忆（关键信息）
- 记忆提取
- 对话压缩
"""
from ai_service.agents.memory.short_memory_agent import ShortMemoryAgent
from ai_service.agents.memory.long_memory_agent import LongMemoryAgent
from ai_service.agents.memory.memory_extraction_agent import (
    MemoryExtractionAgent,
    MemoryPoint,
    ExtractionResult
)
from ai_service.agents.memory.memory_compression_agent import MemoryCompressionAgent
from ai_service.models.memory import Message

__all__ = [
    # 短期记忆
    "ShortMemoryAgent",
    "Message",
    
    # 长期记忆
    "LongMemoryAgent",
    
    # 记忆提取
    "MemoryExtractionAgent",
    "MemoryPoint",
    "ExtractionResult",
    
    # 对话压缩
    "MemoryCompressionAgent",
]
