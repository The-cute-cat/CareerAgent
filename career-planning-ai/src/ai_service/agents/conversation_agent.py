"""
对话智能体 - ConversationAgent

主智能体，负责协调所有记忆子智能体：
1. 管理对话流程
2. 协调短期和长期记忆
3. 流式输出生成
4. 自动提取和存储记忆
5. 会话持久化管理
"""
import asyncio
import json
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from ai_service.agents import log as logger
from ai_service.agents.memory import LongMemoryAgent

from ai_service.agents.memory.memory_compression_agent import memory_compression_agent
from ai_service.agents.memory.memory_extraction_agent import memory_extraction_agent
from ai_service.agents.memory.short_memory_agent import short_memory_agent
from ai_service.repository.session_repository import SessionRepository
from ai_service.services.database_manage import AsyncSessionLocal
from ai_service.services.prompt_loader import prompt_loader
from config import settings


class ConversationAgent:
    """
    对话智能体
    
    主控制器，负责：
    - 协调短期记忆和长期记忆
    - 管理对话流程
    - 自动提取记忆点
    - 流式输出响应
    - 会话持久化管理
    """

    def __init__(self, db_session: AsyncSession | None = None):
        """
        初始化对话智能体
        
        Args:
            db_session: 数据库会话
        """
        self.llm = ChatOpenAI(
            base_url=settings.conversation.agent.base_url,
            model=settings.conversation.agent.model_name,
            api_key=settings.conversation.agent.api_key.get_secret_value(),
            temperature=settings.conversation.agent.extra.get("temperature", 0.7),
            timeout=settings.conversation.agent.timeout,
            max_retries=settings.conversation.agent.max_retries,
        )
        # 初始化记忆子智能体
        self.short_memory = short_memory_agent
        self.extraction_agent = memory_extraction_agent
        self.compression_agent = memory_compression_agent
        # 长期记忆需要数据库会话
        self.db_session = db_session
        # 会话持久化管理（不再缓存，每次按需创建）
        logger.info("ConversationAgent 初始化完成")

    def _ensure_long_memory(self, db_session: AsyncSession | None = None):
        """确保长期记忆智能体已初始化（每次创建新实例以使用当前 db_session）"""
        session = db_session or self.db_session
        if session:
            return LongMemoryAgent(session=session)
        return None

    def _ensure_session_repo(self, db_session: AsyncSession | None = None):
        """确保会话 Repository 已初始化（每次创建新实例以使用当前 db_session）"""
        session = db_session or self.db_session
        if session:
            return SessionRepository(session)
        return None

    async def chat(
            self,
            user_id: str,
            session_id: str,
            user_message: str,
            db_session: AsyncSession | None = None,
            auto_extract_memory: bool = True
    ) -> str:
        """
        处理用户消息并返回响应
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            user_message: 用户消息
            db_session: 数据库会话（可选）
            auto_extract_memory: 是否自动提取记忆点
            
        Returns:
            AI 响应文本
        """
        # 前置准备
        messages = await self._prepare_chat(user_id, session_id, user_message, db_session)
        # 生成响应
        response = await self.llm.ainvoke(messages)
        ai_message = response.content
        # 添加 AI 响应到短期记忆
        await self.short_memory.add_message(
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=ai_message,
            auto_compress=False
        )
        # 对话后置处理（更新计数、生成标题、提取记忆）
        await self._post_chat_process(
            user_id, session_id, user_message, ai_message, db_session, auto_extract_memory
        )
        return ai_message

    async def chat_stream(
            self,
            user_id: str,
            session_id: str,
            user_message: str,
            db_session: AsyncSession | None = None,
            auto_extract_memory: bool = True,
            show_thinking: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        流式处理用户消息并返回响应
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            user_message: 用户消息
            db_session: 数据库会话（可选）
            auto_extract_memory: 是否自动提取记忆点
            show_thinking: 是否显示思考过程
            
        Yields:
            AI 响应的文本片段（JSON 格式，包含 type 和 content）
        """
        # 前置准备
        messages = await self._prepare_chat(user_id, session_id, user_message, db_session)
        # 流式生成响应
        full_response = ""
        thinking_content = ""
        
        try:
            async for chunk in self.llm.astream(messages):
                # 处理思考过程（DeepSeek R1 特有）
                if show_thinking and hasattr(chunk, 'reasoning_content') and chunk.reasoning_content:
                    thinking_content += chunk.reasoning_content
                    yield json.dumps({
                        "type": "thinking",
                        "content": chunk.reasoning_content
                    }, ensure_ascii=False)
                
                # 处理正式回复内容
                if chunk.content:
                    full_response += chunk.content
                    yield json.dumps({
                        "type": "content",
                        "content": chunk.content
                    }, ensure_ascii=False)
                
                # 主动让出控制权，确保数据立即发送
                await asyncio.sleep(0)
                    
        except Exception as e:
            logger.error(f"流式生成失败: {e}")
            # 回滚：移除已写入的孤儿用户消息，保持数据一致性
            await self.short_memory.remove_last_message(user_id, session_id)
            yield json.dumps({
                "type": "error",
                "content": f"抱歉，生成响应时出现错误：{str(e)}"
            }, ensure_ascii=False)
            return
            
        # 添加完整响应到短期记忆
        await self.short_memory.add_message(
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=full_response,
            auto_compress=False
        )
        
        # 对话后置处理（更新计数、生成标题、提取记忆）
        await self._post_chat_process(
            user_id, session_id, user_message, full_response, db_session, auto_extract_memory
        )

    async def _build_context(
            self,
            user_id: str,
            session_id: str,
            db_session: AsyncSession | None
    ) -> str:
        """
        构建对话上下文
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            db_session: 数据库会话
            
        Returns:
            格式化的上下文字符串
        """
        parts = []
        short_memories = await self.short_memory.get_context_messages(user_id, session_id)
        if short_memories:
            parts.append("[对话历史]")
            for msg in short_memories:
                role = "用户" if isinstance(msg, HumanMessage) else "助手"
                parts.append(f"{role}: {msg.content}")
        long_memory = self._ensure_long_memory(db_session)
        if long_memory:
            memory_summary = await long_memory.get_context_summary(
                user_id=user_id,
                max_memories=10,
                db_session=db_session
            )
            if memory_summary:
                parts.append("\n" + memory_summary)
        return "\n".join(parts)

    @staticmethod
    async def _build_messages(
            context: str,
            user_message: str
    ) -> list[BaseMessage]:
        """
        构建消息列表

        Args:
            context: 上下文
            user_message: 用户消息

        Returns:
            LangChain 消息列表
        """
        system_prompt = prompt_loader.small_prompts.get("conversation_agent_system_prompt").format(context=context)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        return messages

    async def _prepare_chat(
            self,
            user_id: str,
            session_id: str,
            user_message: str,
            db_session: AsyncSession | None = None
    ) -> list[BaseMessage]:
        """
        对话前置准备：确保会话持久化、添加用户消息、构建消息列表

        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            user_message: 用户消息
            db_session: 数据库会话

        Returns:
            构建好的消息列表
        """
        # 确保会话持久化记录存在
        await self._ensure_session_persisted(user_id, session_id, db_session)
        # 添加用户消息到短期记忆
        await self.short_memory.add_message(
            user_id=user_id,
            session_id=session_id,
            role="user",
            content=user_message,
            auto_compress=True
        )
        # 构建上下文
        context = await self._build_context(user_id, session_id, db_session)
        # 构建消息列表
        return await self._build_messages(context, user_message)

    async def _post_chat_process(
            self,
            user_id: str,
            session_id: str,
            user_message: str,
            ai_response: str,
            db_session: AsyncSession | None = None,
            auto_extract_memory: bool = True
    ) -> None:
        """
        对话后置处理：更新消息计数、自动生成标题、异步提取记忆

        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            user_message: 用户消息
            ai_response: AI 回复
            db_session: 数据库会话
            auto_extract_memory: 是否自动提取记忆点
        """
        # 更新会话消息计数
        session_repo = self._ensure_session_repo(db_session)
        if session_repo:
            conversation = await session_repo.update_message_count(user_id, session_id, increment=2)
            # 首轮对话完成后（消息数=2），自动生成会话标题
            if conversation and conversation.message_count == 2:
                asyncio.create_task(
                    self._generate_title_async(user_id, session_id, user_message, ai_response)
                )
        # 异步提取记忆点（后台任务）
        if auto_extract_memory and db_session:
            asyncio.create_task(
                self._extract_and_store_memory_async(user_id, session_id)
            )

    async def _generate_title_async(
            self,
            user_id: str,
            session_id: str,
            user_message: str,
            ai_response: str
    ) -> None:
        """
        异步生成并更新会话标题（后台任务）

        基于首轮对话内容调用 LLM 生成简洁的会话标题。

        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            user_message: 用户的首条消息
            ai_response: AI 的首条回复
        """
        try:
            async with AsyncSessionLocal() as new_session:
                title_messages = [
                    SystemMessage(
                        content="你是一个会话标题生成器。根据用户和AI的对话内容，生成一个简洁的会话标题。"
                                "要求：不超过20个字，直接输出标题内容，不要加引号、不要加任何前缀后缀。"
                    ),
                    HumanMessage(
                        content=f"用户: {user_message}\n助手: {ai_response}"
                    )
                ]
                result = await self.llm.ainvoke(title_messages)
                title = result.content.strip()
                # 清理可能的引号或多余字符
                title = title.strip('"\'').strip()

                session_repo = SessionRepository(new_session)
                await session_repo.update_title(user_id, session_id, title)
                await new_session.commit()
                logger.info(f"✅ 自动生成会话标题: \"{title}\" (用户: {user_id}, 会话: {session_id})")
        except Exception as e:
            logger.error(f"❌ 自动生成会话标题失败: {e}", exc_info=True)

    async def _extract_and_store_memory_async(
            self,
            user_id: str,
            session_id: str
    ) -> None:
        """
        异步提取并存储记忆点（后台任务）
        
        注意：此方法会在后台异步执行，不会阻塞主流程。
        使用单独的数据库会话来避免会话冲突。
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
        """
        try:
            # 创建新的数据库会话（避免与主会话冲突）
            async with AsyncSessionLocal() as new_session:
                # 只获取最近的几条消息（避免重复提取旧信息）
                all_messages = await self.short_memory.get_messages(user_id, session_id)
                if not all_messages:
                    return
                # 只取最近 4 条消息（2 轮对话）
                recent_messages = all_messages[-4:] if len(all_messages) > 4 else all_messages
                # 获取已有记忆（用于避免重复）
                long_memory = LongMemoryAgent(session=new_session)
                existing_memories = await long_memory.get_memories(
                    user_id=user_id,
                    limit=20,
                    db_session=new_session
                )
                existing_memory_contents = [m.content for m in existing_memories]
                
                # 提取记忆点
                memory_points = await self.extraction_agent.extract(
                    messages=recent_messages,
                    min_score=0.6,
                    existing_memories=existing_memory_contents
                )
                if not memory_points:
                    logger.debug(f"会话 {session_id} 未提取到有效记忆点")
                    return
                # 存储到长期记忆
                added_count = await long_memory.add_memories(
                    user_id=user_id,
                    session_id=session_id,
                    memory_points=memory_points,
                    db_session=new_session
                )
                # 提交事务
                await new_session.commit()
                logger.info(
                    f"✅ 异步提取并存储了 {len(added_count)} 个记忆点 "
                    f"(用户: {user_id}, 会话: {session_id})"
                )
        except Exception as e:
            logger.error(f"❌ 异步提取记忆失败: {e}", exc_info=True)

    async def _ensure_session_persisted(
            self,
            user_id: str,
            session_id: str,
            db_session: AsyncSession | None
    ) -> None:
        """
        确保会话在数据库中持久化
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            db_session: 数据库会话
        """
        session_repo = self._ensure_session_repo(db_session)
        if session_repo:
            await session_repo.get_or_create(session_id, user_id)
            await db_session.flush()

    async def _update_session_message_count(
            self,
            user_id: str,
            session_id: str,
            increment: int = 1,
            db_session: AsyncSession | None = None
    ) -> None:
        """
        更新会话消息计数

        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            increment: 增量
            db_session: 数据库会话
        """
        session_repo = self._ensure_session_repo(db_session)
        if session_repo:
            await session_repo.update_message_count(user_id, session_id, increment)

    async def extract_memory_manually(
            self,
            user_id: str,
            session_id: str,
            db_session: AsyncSession
    ) -> int:
        """
        手动触发记忆提取（同步等待）
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            db_session: 数据库会话
            
        Returns:
            提取并存储的记忆点数量
        """
        try:
            # 获取对话消息
            messages = await self.short_memory.get_messages(user_id, session_id)
            if not messages:
                logger.warning(f"会话 {session_id} 没有消息可提取")
                return 0
            # 获取已有记忆
            long_memory = self._ensure_long_memory(db_session)
            if not long_memory:
                return 0
            
            existing_memories = await long_memory.get_memories(
                user_id=user_id,
                limit=20,
                db_session=db_session
            )
            existing_memory_contents = [m.content for m in existing_memories]
            
            # 提取记忆点
            memory_points = await self.extraction_agent.extract(
                messages=messages,
                min_score=0.6,
                existing_memories=existing_memory_contents
            )
            if not memory_points:
                logger.info(f"会话 {session_id} 未提取到有效记忆点")
                return 0
            # 存储到长期记忆
            added_memories = await long_memory.add_memories(
                user_id=user_id,
                session_id=session_id,
                memory_points=memory_points,
                db_session=db_session
            )
            logger.info(f"手动提取并存储了 {len(added_memories)} 个记忆点")
            return len(added_memories)
        except Exception as e:
            logger.error(f"手动提取记忆失败: {e}", exc_info=True)
            return 0

    async def clear_session(
            self,
            user_id: str,
            session_id: str,
            db_session: AsyncSession | None = None
    ) -> bool:
        """
        清除会话的短期记忆并软删除持久化记录

        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            db_session: 数据库会话

        Returns:
            是否成功
        """
        # 清除 Redis 短期记忆
        redis_cleared = await self.short_memory.clear(user_id, session_id)

        # 软删除数据库会话记录
        if db_session:
            session_repo = self._ensure_session_repo(db_session)
            if session_repo:
                db_cleared = await session_repo.soft_delete(user_id, session_id)
                return redis_cleared and db_cleared

        return redis_cleared

    async def get_session_history(
            self,
            user_id: str,
            session_id: str,
            limit: int | None = None
    ) -> list[dict]:
        """
        获取会话历史记录

        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            limit: 限制返回数量

        Returns:
            消息字典列表
        """
        messages = await self.short_memory.get_messages(user_id, session_id)
        if limit:
            messages = messages[-limit:]
        return [msg.model_dump() for msg in messages]

    async def get_user_sessions(
            self,
            user_id: str,
            page: int = 1,
            page_size: int = 20,
            db_session: AsyncSession | None = None
    ) -> dict:
        """
        获取用户的会话列表
        
        Args:
            user_id: 用户 ID
            page: 页码
            page_size: 每页数量
            db_session: 数据库会话
            
        Returns:
            { "total": int, "items": List[dict], "page": int, "page_size": int }
        """
        session_repo = self._ensure_session_repo(db_session)
        if not session_repo:
            return {"total": 0, "items": [], "page": page, "page_size": page_size}

        result = await session_repo.get_list_by_user(
            user_id=user_id,
            page=page,
            page_size=page_size
        )

        # 转换为字典格式
        items = [
            {
                "id": item.id,
                "sessionId": item.session_id,
                "userId": item.user_id,
                "title": item.title,
                "messageCount": item.message_count,
                "createdAt": item.created_at.isoformat() if item.created_at else None,
                "updatedAt": item.updated_at.isoformat() if item.updated_at else None,
            }
            for item in result["items"]
        ]

        return {
            "total": result["total"],
            "items": items,
            "page": result["page"],
            "page_size": result["page_size"]
        }

    async def update_session_title(
            self,
            user_id: str,
            session_id: str,
            title: str,
            db_session: AsyncSession | None = None
    ) -> bool:
        """
        更新会话标题

        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            title: 新标题
            db_session: 数据库会话

        Returns:
            是否成功
        """
        session_repo = self._ensure_session_repo(db_session)
        if not session_repo:
            return False

        result = await session_repo.update_title(user_id, session_id, title)
        return result is not None


conversation_agent = ConversationAgent()
