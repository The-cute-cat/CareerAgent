"""
会话持久化 Repository

管理 ConversationSession 表的 CRUD 操作
注意：session_id 不再全局唯一，而是 (user_id, session_id) 联合唯一
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ai_service.models.memory import ConversationSession
from ai_service.utils.logger_handler import log as logger


class SessionRepository:
    """会话持久化 Repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
            self,
            session_id: str,
            user_id: int,
            title: Optional[str] = None
    ) -> ConversationSession:
        """
        创建新会话

        Args:
            session_id: 会话 ID
            user_id: 用户 ID
            title: 会话标题（可选）

        Returns:
            创建的会话对象
        """
        conversation = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            title=title,
            message_count=0,
            is_active=True
        )
        self.session.add(conversation)
        await self.session.flush()
        logger.info(f"创建会话: session_id={session_id}, user_id={user_id}")
        return conversation

    async def get_or_create(
            self,
            session_id: str,
            user_id: int,
            title: str | None = None
    ) -> ConversationSession:
        """
        获取或创建会话（Upsert）

        Args:
            session_id: 会话 ID
            user_id: 用户 ID
            title: 会话标题（可选，仅创建时使用）

        Returns:
            会话对象
        """
        existing = await self.get_by_user_and_session_id(user_id, session_id)
        if existing:
            return existing
        return await self.create(session_id, user_id, title)

    async def get_by_id(self, conversation_id: int) -> Optional[ConversationSession]:
        """根据主键 ID 获取会话"""
        stmt = select(ConversationSession).where(
            ConversationSession.id == conversation_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_session_id(
            self,
            user_id: int,
            session_id: str
    ) -> Optional[ConversationSession]:
        """根据用户ID和会话ID获取会话（联合唯一）"""
        stmt = select(ConversationSession).where(
            and_(
                ConversationSession.user_id == user_id,
                ConversationSession.session_id == session_id
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_list_by_user(
            self,
            user_id: int,
            page: int = 1,
            page_size: int = 20,
            active_only: bool = True
    ) -> Dict[str, Any]:
        """
        获取用户的会话列表（分页）

        Args:
            user_id: 用户 ID
            page: 页码
            page_size: 每页数量
            active_only: 是否只返回激活的会话

        Returns:
            { "total": int, "items": List[ConversationSession], "page": int, "page_size": int }
        """
        conditions = [ConversationSession.user_id == user_id]
        if active_only:
            conditions.append(ConversationSession.is_active == True)

        stmt = select(ConversationSession).where(*conditions)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one() or 0
        offset = (page - 1) * page_size
        stmt = stmt.order_by(
            ConversationSession.updated_at.desc()
        ).offset(offset).limit(page_size)
        result = await self.session.execute(stmt)
        items = result.scalars().all()
        return {
            "total": total,
            "items": list(items),
            "page": page,
            "page_size": page_size
        }

    async def get_all_active_by_user(
            self,
            user_id: int
    ) -> List[ConversationSession]:
        """获取用户所有激活的会话（不分页）"""
        stmt = select(ConversationSession).where(
            and_(
                ConversationSession.user_id == user_id,
                ConversationSession.is_active == True
            )
        ).order_by(ConversationSession.updated_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_message_count(
            self,
            user_id: int,
            session_id: str,
            increment: int = 1
    ) -> Optional[ConversationSession]:
        """
        更新会话消息计数

        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            increment: 增量（默认 1）

        Returns:
            更新后的会话对象
        """
        conversation = await self.get_by_user_and_session_id(user_id, session_id)
        if not conversation:
            return None
        conversation.message_count += increment
        conversation.updated_at = datetime.now()
        await self.session.flush()
        return conversation

    async def update_title(
            self,
            user_id: int,
            session_id: str,
            title: str
    ) -> Optional[ConversationSession]:
        """
        更新会话标题

        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            title: 新标题

        Returns:
            更新后的会话对象
        """
        conversation = await self.get_by_user_and_session_id(user_id, session_id)
        if not conversation:
            return None
        conversation.title = title
        conversation.updated_at = datetime.now()
        await self.session.flush()
        return conversation

    async def update_summary(
            self,
            user_id: int,
            session_id: str,
            summary: str
    ) -> Optional[ConversationSession]:
        """
        更新会话压缩摘要

        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            summary: 压缩后的摘要

        Returns:
            更新后的会话对象
        """
        conversation = await self.get_by_user_and_session_id(user_id, session_id)
        if not conversation:
            return None
        conversation.compressed_summary = summary
        conversation.updated_at = datetime.now()
        await self.session.flush()
        return conversation

    async def update(
            self,
            user_id: int,
            session_id: str,
            update_data: Dict[str, Any]
    ) -> Optional[ConversationSession]:
        """
        通用更新方法

        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            update_data: 更新数据字典

        Returns:
            更新后的会话对象
        """
        conversation = await self.get_by_user_and_session_id(user_id, session_id)
        if not conversation:
            return None
        for key, value in update_data.items():
            if hasattr(conversation, key):
                setattr(conversation, key, value)
        conversation.updated_at = datetime.now()
        await self.session.flush()
        return conversation

    async def soft_delete(
            self,
            user_id: int,
            session_id: str
    ) -> bool:
        """
        软删除会话（标记为非激活）

        Args:
            user_id: 用户 ID
            session_id: 会话 ID

        Returns:
            是否成功
        """
        conversation = await self.get_by_user_and_session_id(user_id, session_id)
        if not conversation:
            return False

        conversation.is_active = False
        conversation.updated_at = datetime.now()
        await self.session.flush()
        logger.info(f"软删除会话: user_id={user_id}, session_id={session_id}")
        return True

    async def hard_delete(
            self,
            user_id: int,
            session_id: str
    ) -> bool:
        """
        硬删除会话（从数据库删除）

        Args:
            user_id: 用户 ID
            session_id: 会话 ID

        Returns:
            是否成功
        """
        conversation = await self.get_by_user_and_session_id(user_id, session_id)
        if not conversation:
            return False

        await self.session.delete(conversation)
        await self.session.flush()
        logger.info(f"硬删除会话: user_id={user_id}, session_id={session_id}")
        return True

    async def delete_by_user(self, user_id: int, soft: bool = True) -> int:
        """
        删除用户所有会话

        Args:
            user_id: 用户 ID
            soft: 是否软删除

        Returns:
            删除数量
        """
        if soft:
            stmt = (
                update(ConversationSession)
                .where(ConversationSession.user_id == user_id)
                .values(is_active=False, updated_at=datetime.now())
            )
        else:
            stmt = (
                delete(ConversationSession)
                .where(ConversationSession.user_id == user_id)
            )
        result = await self.session.execute(stmt)
        await self.session.flush()
        # noinspection PyUnresolvedReferences
        count = result.rowcount
        logger.info(f"{'软' if soft else '硬'}删除用户会话: user_id={user_id}, count={count}")
        return count
