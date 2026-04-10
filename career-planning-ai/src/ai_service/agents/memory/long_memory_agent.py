"""
长期记忆智能体 - LongMemoryAgent

职责：
1. 管理关键记忆点
2. 持久化到 MySQL
3. 使用 ChromaDB 进行向量检索
4. 记忆评分和容量管理
"""
import json
from datetime import datetime
from typing import Optional
from uuid import uuid4

from langchain_openai import ChatOpenAI
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ai_service.agents.memory.memory_extraction_agent import MemoryPoint
from ai_service.models.memory import Memory
from ai_service.agents import log as logger
from ai_service.services.chroma_service import ChromaService
from config import settings

__all__ = [
    "LongMemoryAgent",
    "long_memory_agent",
]


class LongMemoryAgent:
    """
    长期记忆智能体
    
    管理用户的关键记忆点，使用 MySQL 持久化存储，
    ChromaDB 提供向量检索能力。
    """

    MAX_MEMORY_COUNT = settings.conversation.memory.long.max_memory_count
    MIN_SCORE = settings.conversation.memory.long.min_score
    CHROMA_COLLECTION_NAME = settings.conversation.memory.long.collection_name

    def __init__(self, session: AsyncSession | None = None):
        """
        初始化长期记忆智能体
        
        Args:
            session: 数据库会话（可选，如果不提供需要在使用时传入）
        """
        self.llm = ChatOpenAI(
            base_url=settings.conversation.memory.long.base_url,
            model=settings.conversation.memory.long.model_name,
            api_key=settings.conversation.memory.long.api_key.get_secret_value(),
            temperature=settings.conversation.memory.long.extra.get("temperature", 0.2),
            timeout=settings.conversation.memory.long.timeout,
            max_retries=settings.conversation.memory.long.max_retries,
        )
        self.session = session
        self.chroma = ChromaService.get_instance(
            collection_name=self.CHROMA_COLLECTION_NAME,
            persist_directory=settings.conversation.save_path
        )
        logger.info(
            f"LongMemoryAgent 初始化完成，ChromaDB 可用: {self.chroma.count()} 条记忆"
        )

    async def add_memory(
            self,
            user_id: int,
            session_id: str,
            memory_point: MemoryPoint,
            db_session: AsyncSession | None = None,
            similarity_threshold: float = 0.85
    ) -> Memory | None:
        """
        添加记忆到长期存储
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            memory_point: 记忆点
            db_session: 数据库会话（如果未在初始化时提供）
            similarity_threshold: 语义相似度阈值（0-1），超过此值视为重复
            
        Returns:
            创建的记忆对象，如果失败返回 None
        """
        session = db_session or self.session
        if not session:
            raise ValueError("数据库会话未提供")

        # 计算综合评分
        total_score = (
                memory_point.importance_score * 0.3 +
                memory_point.relevance_score * 0.3 +
                memory_point.recency_score * 0.2 +
                memory_point.uniqueness_score * 0.2
        )

        current_count = await self.get_memory_count(user_id, session)
        if current_count >= self.MAX_MEMORY_COUNT:
            # 需要移除低分记忆
            await self._remove_low_score_memory(user_id, session, total_score)

        # 检查是否有语义相似的记忆（使用向量相似度）
        similar_memory = await self._find_similar_memory(
            user_id, memory_point.content, session, similarity_threshold
        )
        if similar_memory:
            # 更新已有记忆而不是跳过
            logger.info(f"发现相似记忆，更新: {memory_point.content[:50]}...")
            return await self._update_memory(
                similar_memory, memory_point, total_score, session
            )

        vector_id = str(uuid4())
        try:
            self.chroma.add_content(
                content=memory_point.content,
                metadata={
                    "user_id": user_id,
                    "vector_id": vector_id,
                    "memory_type": memory_point.memory_type,
                    "total_score": total_score,
                    "created_at": datetime.now().isoformat()
                },
                id_str=vector_id
            )
            memory = Memory(
                user_id=user_id,
                session_id=session_id,
                content=memory_point.content,
                memory_type=memory_point.memory_type,
                importance_score=memory_point.importance_score,
                relevance_score=memory_point.relevance_score,
                recency_score=memory_point.recency_score,
                uniqueness_score=memory_point.uniqueness_score,
                total_score=total_score,
                metadata_json=json.dumps({"reason": memory_point.reason}),
                vector_id=vector_id,
                is_active=True
            )
            session.add(memory)
            await session.flush()
            logger.info(
                f"添加长期记忆成功: user={user_id}, type={memory_point.memory_type}, "
                f"score={total_score:.2f}, content={memory_point.content[:50]}..."
            )
            return memory
        except Exception as e:
            logger.error(f"添加长期记忆失败: {e}")
            # 清理可能已添加的向量
            if 'vector_id' in locals():
                try:
                    self.chroma.delete_by_ids([vector_id])
                except Exception as e:
                    logger.error(f"清理向量失败: {e}")
            return None

    async def add_memories(
            self,
            user_id: int,
            session_id: str,
            memory_points: list[MemoryPoint],
            db_session: AsyncSession | None = None
    ) -> list[Memory]:
        """
        批量添加记忆
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            memory_points: 记忆点列表
            db_session: 数据库会话
            
        Returns:
            成功添加的记忆列表
        """
        added_memories = []
        for point in memory_points:
            memory = await self.add_memory(
                user_id, session_id, point, db_session
            )
            if memory:
                added_memories.append(memory)
        return added_memories

    async def get_memories(
            self,
            user_id: int,
            limit: int = 20,
            min_score: float | None = None,
            db_session: AsyncSession | None = None
    ) -> list[Memory]:
        """
        获取用户的长期记忆
        
        Args:
            user_id: 用户 ID
            limit: 返回数量限制
            min_score: 最低分数过滤
            db_session: 数据库会话
            
        Returns:
            记忆列表
        """
        session = db_session or self.session
        if not session:
            raise ValueError("数据库会话未提供")
        query = select(Memory).where(
            and_(
                Memory.user_id == user_id,
                Memory.is_active == True
            )
        )
        if min_score is not None:
            query = query.where(Memory.total_score >= min_score)
        query = query.order_by(Memory.total_score.desc()).limit(limit)
        result = await session.execute(query)
        memories = result.scalars().all()
        return list(memories)

    async def search_memories(
            self,
            user_id: int,
            query: str,
            k: int = 5
    ) -> list[tuple[Memory, float]]:
        """
        基于语义相似度搜索记忆
        
        Args:
            user_id: 用户 ID
            query: 查询文本
            k: 返回数量
            
        Returns:
            (记忆对象, 相似度分数) 元组列表
        """
        try:
            results = self.chroma.similarity_search_with_score(
                query=query,
                k=k * 2,
                filter_dict={"user_id": user_id}
            )
            vector_ids = [doc.metadata.get("vector_id") for doc, score in results if doc.metadata.get("vector_id")]

            if not vector_ids:
                return []

            session = self.session
            if not session:
                logger.warning("数据库会话未提供，无法获取完整记忆对象")
                return []
            query_stmt = select(Memory).where(Memory.vector_id.in_(vector_ids))
            result = await session.execute(query_stmt)
            memories = {m.vector_id: m for m in result.scalars().all()}

            memory_scores = []
            for doc, score in results:
                vector_id = doc.metadata.get("vector_id")
                if vector_id in memories:
                    memory_scores.append((memories[vector_id], score))
            return memory_scores[:k]

        except Exception as e:
            logger.error(f"搜索记忆失败: {e}")
            return []

    async def get_memory_count(
            self,
            user_id: int,
            db_session: Optional[AsyncSession] = None
    ) -> int:
        """
        获取用户的记忆数量
        
        Args:
            user_id: 用户 ID
            db_session: 数据库会话
            
        Returns:
            记忆数量
        """
        session = db_session or self.session
        if not session:
            raise ValueError("数据库会话未提供")
        from sqlalchemy import func
        query = select(func.count(Memory.id)).where(
            and_(
                Memory.user_id == user_id,
                Memory.is_active == True
            )
        )
        result = await session.execute(query)
        count = result.scalar()
        return count or 0

    async def delete_memory(
            self,
            memory_id: int,
            user_id: int,
            db_session: Optional[AsyncSession] = None
    ) -> bool:
        """
        删除记忆
        
        Args:
            memory_id: 记忆 ID
            user_id: 用户 ID（用于权限校验）
            db_session: 数据库会话
            
        Returns:
            是否成功
        """
        session = db_session or self.session
        if not session:
            raise ValueError("数据库会话未提供")
        try:
            query = select(Memory).where(
                and_(
                    Memory.id == memory_id,
                    Memory.user_id == user_id,
                    Memory.is_active == True
                )
            )
            result = await session.execute(query)
            memory = result.scalar_one_or_none()
            if not memory:
                return False
            if memory.vector_id:
                self.chroma.delete_by_ids([memory.vector_id])
            memory.is_active = False
            await session.flush()
            logger.info(f"删除记忆成功: id={memory_id}")
            return True
        except Exception as e:
            logger.error(f"删除记忆失败: {e}")
            return False

    async def _remove_low_score_memory(
            self,
            user_id: int,
            db_session: AsyncSession,
            new_score: float
    ) -> bool:
        """
        移除低分记忆以腾出空间
        
        Args:
            user_id: 用户 ID
            db_session: 数据库会话
            new_score: 新记忆的分数
            
        Returns:
            是否成功移除
        """
        try:
            query = select(Memory).where(
                and_(
                    Memory.user_id == user_id,
                    Memory.is_active == True,
                    Memory.total_score < new_score
                )
            ).order_by(Memory.total_score.asc()).limit(1)
            result = await db_session.execute(query)
            lowest_memory = result.scalar_one_or_none()
            if lowest_memory:
                return await self.delete_memory(lowest_memory.id, user_id, db_session)
            return False
        except Exception as e:
            logger.error(f"移除低分记忆失败: {e}")
            return False

    @staticmethod
    async def _check_duplicate(
            user_id: int,
            content: str,
            db_session: AsyncSession
    ) -> bool:
        """
        检查是否存在完全相同的记忆
        
        Args:
            user_id: 用户 ID
            content: 记忆内容
            db_session: 数据库会话
            
        Returns:
            是否重复
        """
        query = select(Memory).where(
            and_(
                Memory.user_id == user_id,
                Memory.is_active == True,
                Memory.content == content
            )
        ).limit(1)
        result = await db_session.execute(query)
        existing = result.scalar_one_or_none()
        return existing is not None

    async def _check_semantic_duplicate(
            self,
            user_id: int,
            content: str,
            db_session: AsyncSession,
            threshold: float = 0.85
    ) -> bool:
        """
        检查是否存在语义相似的记忆（使用向量相似度）
        
        Args:
            user_id: 用户 ID
            content: 记忆内容
            db_session: 数据库会话
            threshold: 相似度阈值（0-1），超过此值视为重复
            
        Returns:
            是否语义重复
        """
        try:
            # 使用 ChromaDB 进行向量相似度搜索
            results = self.chroma.similarity_search_with_score(
                query=content,
                k=3,
                filter_dict={"user_id": user_id}
            )

            for doc, score in results:
                # ChromaDB 返回的是距离，距离越小越相似
                # 对于 cosine 距离，score 范围通常是 0-2
                # 转换为相似度：similarity = 1 - distance/2
                similarity = 1 - score / 2
                if similarity >= threshold:
                    logger.debug(
                        f"发现语义相似记忆: 相似度={similarity:.2f}, "
                        f"新内容={content[:30]}..., 已有内容={doc.page_content[:30]}..."
                    )
                    return True
            return False
        except Exception as e:
            logger.warning(f"语义相似度检查失败，回退到精确匹配: {e}")
            return await self._check_duplicate(user_id, content, db_session)

    async def _find_similar_memory(
            self,
            user_id: int,
            content: str,
            db_session: AsyncSession,
            threshold: float = 0.85
    ) -> Memory | None:
        """
        查找语义相似的记忆
        
        Args:
            user_id: 用户 ID
            content: 记忆内容
            db_session: 数据库会话
            threshold: 相似度阈值（0-1），超过此值视为相似
            
        Returns:
            相似的记忆对象，如果没有返回 None
        """
        try:
            results = self.chroma.similarity_search_with_score(
                query=content,
                k=3,
                filter_dict={"user_id": user_id}
            )

            for doc, score in results:
                similarity = 1 - score / 2
                if similarity >= threshold:
                    # 优先从 metadata 获取 vector_id
                    vector_id = doc.metadata.get("vector_id")

                    # 如果 metadata 中没有 vector_id，尝试通过内容匹配
                    if not vector_id:
                        query_stmt = select(Memory).where(
                            and_(
                                Memory.user_id == user_id,
                                Memory.content == doc.page_content,
                                Memory.is_active == True
                            )
                        )
                    else:
                        query_stmt = select(Memory).where(
                            and_(
                                Memory.vector_id == vector_id,
                                Memory.is_active == True
                            )
                        )

                    result = await db_session.execute(query_stmt)
                    memory = result.scalar_one_or_none()
                    if memory:
                        logger.debug(
                            f"找到相似记忆: id={memory.id}, 相似度={similarity:.2f}"
                        )
                        return memory
            return None
        except Exception as e:
            logger.warning(f"查找相似记忆失败: {e}")
            return None

    async def _update_memory(
            self,
            existing_memory: Memory,
            memory_point: MemoryPoint,
            new_score: float,
            db_session: AsyncSession
    ) -> Memory | None:
        """
        更新已有记忆
        
        Args:
            existing_memory: 已存在的记忆对象
            memory_point: 新的记忆点数据
            new_score: 新的综合评分
            db_session: 数据库会话
            
        Returns:
            更新后的记忆对象
        """
        try:
            # 删除旧的向量
            if existing_memory.vector_id:
                self.chroma.delete_by_ids([existing_memory.vector_id])

            # 创建新的向量
            vector_id = str(uuid4())
            self.chroma.add_content(
                content=memory_point.content,
                metadata={
                    "user_id": existing_memory.user_id,
                    "vector_id": vector_id,
                    "memory_type": memory_point.memory_type,
                    "total_score": new_score,
                    "created_at": datetime.now().isoformat()
                },
                id_str=vector_id
            )

            # 更新数据库记录
            existing_memory.content = memory_point.content
            existing_memory.memory_type = memory_point.memory_type
            existing_memory.importance_score = memory_point.importance_score
            existing_memory.relevance_score = memory_point.relevance_score
            existing_memory.recency_score = memory_point.recency_score
            existing_memory.uniqueness_score = memory_point.uniqueness_score
            existing_memory.total_score = new_score
            existing_memory.metadata_json = json.dumps({"reason": memory_point.reason})
            existing_memory.vector_id = vector_id
            existing_memory.updated_at = datetime.now()

            await db_session.flush()
            logger.info(
                f"更新长期记忆成功: id={existing_memory.id}, "
                f"score={new_score:.2f}, content={memory_point.content[:50]}..."
            )
            return existing_memory
        except Exception as e:
            logger.error(f"更新记忆失败: {e}")
            return None

    async def get_context_summary(
            self,
            user_id: int,
            max_memories: int = 10,
            db_session: Optional[AsyncSession] = None
    ) -> str:
        """
        获取记忆的上下文摘要（用于构建对话上下文）
        
        Args:
            user_id: 用户 ID
            max_memories: 最大记忆数量
            db_session: 数据库会话
            
        Returns:
            格式化的记忆摘要
        """
        memories = await self.get_memories(
            user_id, limit=max_memories, db_session=db_session
        )
        if not memories:
            return ""
        grouped = {}
        for memory in memories:
            if memory.memory_type not in grouped:
                grouped[memory.memory_type] = []
            grouped[memory.memory_type].append(memory)
        parts = ["[用户长期记忆]"]
        type_names = {
            "preference": "偏好",
            "decision": "决策",
            "fact": "事实",
            "goal": "目标"
        }
        for memory_type, type_memories in grouped.items():
            type_name = type_names.get(memory_type, memory_type)
            parts.append(f"\n{type_name}:")
            for memory in type_memories:
                parts.append(f"  - {memory.content}")
        return "\n".join(parts)


long_memory_agent = LongMemoryAgent()
