"""
记忆提取智能体 - MemoryExtractionAgent

职责：
1. 从对话中自动提取记忆点
2. 对记忆点进行评分
3. 过滤低价值信息
"""
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from ai_service.models.memory import Message
from ai_service.agents import log as logger
from ai_service.services.prompt_loader import prompt_loader
from config import settings


__all__=[
    "MemoryExtractionAgent",
    "MemoryPoint",
    "ExtractionResult",
    "memory_extraction_agent",
]

class MemoryPoint(BaseModel):
    """记忆点模型"""
    content: str = Field(..., description="记忆内容（简洁概括）")
    memory_type: str = Field(..., description="记忆类型：preference/decision/fact/goal")
    importance_score: float = Field(..., ge=0, le=1, description="重要性评分")
    relevance_score: float = Field(..., ge=0, le=1, description="相关性评分")
    recency_score: float = Field(..., ge=0, le=1, description="时效性评分")
    uniqueness_score: float = Field(..., ge=0, le=1, description="独特性评分")
    reason: str = Field(..., description="评分理由")


class ExtractionResult(BaseModel):
    """提取结果模型"""
    memory_points: list[MemoryPoint] = Field(default_factory=list, description="记忆点列表")


class MemoryExtractionAgent:
    """
    记忆提取智能体
    
    从对话中提取有价值的记忆点，
    包括用户偏好、重要决策、关键事实和目标。
    """

    def __init__(self):
        """初始化记忆提取智能体"""
        self.llm = ChatOpenAI(
            base_url=settings.conversation.memory.extraction.base_url,
            model=settings.conversation.memory.extraction.model_name,
            api_key=settings.conversation.memory.extraction.api_key.get_secret_value(),
            temperature=settings.conversation.memory.extraction.extra.get("temperature", 0.2),
            timeout=settings.conversation.memory.extraction.timeout,
            max_retries=settings.conversation.memory.extraction.max_retries,
        )

        logger.info("MemoryExtractionAgent 初始化完成")

    async def extract(
            self,
            messages: list[Message],
            min_score: float = 0.6
    ) -> list[MemoryPoint]:
        """
        从对话中提取记忆点
        
        Args:
            messages: 消息列表
            min_score: 最低综合评分阈值
            
        Returns:
            记忆点列表
        """
        if not messages:
            return []
        # 格式化对话内容
        conversation_text = self._format_messages(messages)
        # 构建提示
        prompt = ChatPromptTemplate.from_template(prompt_loader.extraction_prompt)
        chain = prompt | self.llm
        content = None
        try:
            # 调用 LLM 提取记忆点
            response = await chain.ainvoke({"conversation": conversation_text})
            content = response.content.strip()
            # 清理可能的 markdown 代码块标记
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            # 解析 JSON
            result_data = json.loads(content)
            result = ExtractionResult(**result_data)
            # 计算综合评分并过滤
            filtered_points = []
            for point in result.memory_points:
                # 计算加权综合评分
                total_score = (
                        point.importance_score * 0.3 +
                        point.relevance_score * 0.3 +
                        point.recency_score * 0.2 +
                        point.uniqueness_score * 0.2
                )
                # 创建新的记忆点，添加综合评分
                point_dict = point.model_dump()
                point_dict['total_score'] = total_score
                # 过滤低分记忆
                if total_score >= min_score:
                    filtered_points.append(point)
            logger.info(
                f"记忆提取完成，提取到 {len(result.memory_points)} 个记忆点，"
                f"过滤后保留 {len(filtered_points)} 个"
            )
            return filtered_points
        except json.JSONDecodeError as e:
            logger.error(f"记忆提取 JSON 解析失败: {e}\n原始内容: {content}")
            return []
        except Exception as e:
            logger.error(f"记忆提取失败: {e}")
            return []

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

    async def extract_single_message(self, message: Message) -> list[MemoryPoint]:
        """
        从单条消息中提取记忆点
        
        Args:
            message: 单条消息
            
        Returns:
            记忆点列表
        """
        return await self.extract([message], min_score=0.5)


memory_extraction_agent = MemoryExtractionAgent()