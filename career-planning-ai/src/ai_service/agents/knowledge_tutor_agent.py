"""
知识导师智能体 - KnowledgeTutorAgent

提供知识图谱节点的深度讲解服务：
1. 分析知识点对岗位的影响和作用
2. 解释知识点的核心内容和实际应用
3. 流式输出生成
"""
import asyncio
import json
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ai_service.agents import log as logger
from ai_service.services.prompt_loader import prompt_loader
from config import settings

__all__ = [
    "knowledge_tutor_agent",
]


class KnowledgeTutorAgent:
    """
    知识导师智能体
    
    负责知识点深度讲解：
    - analysis_llm: 分析知识点对岗位的影响
    - explain_llm: 解释知识点内容本身
    """

    def __init__(self):
        """初始化知识导师智能体"""
        self.analysis_llm = ChatOpenAI(
            api_key=settings.knowledge_graph.analysis.api_key.get_secret_value(),
            model=settings.knowledge_graph.analysis.model_name,
            base_url=settings.knowledge_graph.analysis.base_url,
            timeout=settings.knowledge_graph.analysis.timeout,
            max_retries=settings.knowledge_graph.analysis.max_retries,
            temperature=settings.knowledge_graph.analysis.extra["temperature"]
        )
        self.explain_llm = ChatOpenAI(
            api_key=settings.knowledge_graph.explain.api_key.get_secret_value(),
            model=settings.knowledge_graph.explain.model_name,
            base_url=settings.knowledge_graph.explain.base_url,
            timeout=settings.knowledge_graph.explain.timeout,
            max_retries=settings.knowledge_graph.explain.max_retries,
            temperature=settings.knowledge_graph.explain.extra["temperature"]
        )
        logger.info("KnowledgeTutorAgent 初始化完成")

    @staticmethod
    async def _stream_generate(
            llm: ChatOpenAI,
            system_prompt: str,
            user_prompt: str,
            error_msg_prefix: str
    ) -> AsyncGenerator[str, None]:
        """
        通用的流式生成方法
        
        Args:
            llm: 使用的LLM实例
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            error_msg_prefix: 错误消息前缀
            
        Yields:
            文本片段（JSON格式）
        """
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            async for chunk in llm.astream(messages):
                if chunk.content:
                    yield json.dumps({
                        "type": "content",
                        "content": chunk.content
                    }, ensure_ascii=False)
                await asyncio.sleep(0)
        except Exception as e:
            logger.error(f"{error_msg_prefix}: {e}", exc_info=True)
            yield json.dumps({
                "type": "error",
                "content": f"{error_msg_prefix}：{str(e)}"
            }, ensure_ascii=False)

    async def analyze_knowledge_stream(
            self,
            current_node: str,
            target_position: str,
            graph_context: str = "",
            user_profile: str = "",
            industry_data: str = ""
    ) -> AsyncGenerator[str, None]:
        """
        流式分析知识点对岗位的影响
        
        Args:
            current_node: 当前知识点
            target_position: 目标岗位名称
            graph_context: 图谱关系（前置/后续/关联）
            user_profile: 用户画像
            industry_data: 行业数据（可选）
            
        Yields:
            分析结果的文本片段（JSON格式）
        """
        user_prompt = prompt_loader.small_prompts["career_coach_planner_user"].format(
            current_node=current_node,
            target_position=target_position,
            graph_context=graph_context or "暂无图谱关系信息",
            user_profile=user_profile or "暂无用户画像",
            industry_data=industry_data or "暂无行业数据"
        )
        async for chunk in self._stream_generate(
            llm=self.analysis_llm,
            system_prompt=prompt_loader.career_coach_planner,
            user_prompt=user_prompt,
            error_msg_prefix="分析知识点失败"
        ):
            yield chunk

    async def explain_knowledge_stream(
            self,
            current_node: str,
            target_position: str,
            graph_context: str = "",
            user_profile: str = ""
    ) -> AsyncGenerator[str, None]:
        """
        流式解释知识点内容
        
        Args:
            current_node: 当前知识点
            target_position: 目标岗位名称
            graph_context: 图谱关系（前置/后续/关联）
            user_profile: 用户画像
            
        Yields:
            解释内容的文本片段（JSON格式）
        """
        user_prompt = prompt_loader.small_prompts["knowledge_tutor_explainer_user"].format(
            current_node=current_node,
            target_position=target_position,
            graph_context=graph_context or "暂无图谱关系信息",
            user_profile=user_profile or "暂无用户画像"
        )
        async for chunk in self._stream_generate(
            llm=self.explain_llm,
            system_prompt=prompt_loader.knowledge_tutor_explainer,
            user_prompt=user_prompt,
            error_msg_prefix="解释知识点失败"
        ):
            yield chunk


knowledge_tutor_agent = KnowledgeTutorAgent()
