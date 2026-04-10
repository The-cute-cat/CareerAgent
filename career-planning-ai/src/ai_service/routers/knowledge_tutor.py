"""
知识导师路由 - Knowledge Tutor Router

提供知识图谱节点讲解的 API 接口：
1. 知识点岗位影响分析（流式）
2. 知识点详细解释（流式）

注意：分析和解释分别用于两个不同的标签页
"""
import asyncio
import json

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ai_service.agents.knowledge_tutor_agent import knowledge_tutor_agent
from ai_service.agents.user_job_match_analyzer import get_profile_text
from ai_service.schemas.auth import validate_token
from ai_service.utils.logger_handler import log

__all__ = ["router"]

router = APIRouter(prefix="/knowledge_tutor", tags=["knowledge_tutor"])


class KnowledgeExplainRequest(BaseModel):
    """知识点解释请求"""
    current_node: str = Field(..., description="当前知识点名称")
    target_position: str = Field(..., description="目标岗位名称")
    graph_context: str = Field("", description="图谱关系（前置/后续/关联）")
    user_profile: str = Field("", description="用户画像")
    industry_data: str = Field("", description="行业数据（可选）")


@router.post("/analyze/stream")
async def analyze_knowledge_stream(
        request: Request,
        current_node: str = Form(..., description="当前知识点名称"),
        job_id: int = Form(..., description="目标岗位ID"),
        user_id: int = Form(..., description="用户ID"),
        graph_context: str = Form("", description="图谱关系"),
        industry_data: str = Form("", description="行业数据"),
        _: bool = Depends(validate_token)
):
    """
    流式分析知识点对岗位的影响（SSE）
    
    用于"岗位影响"标签页
    """
    job_profile_text, user_profile_text = await get_profile_text(job_id, user_id)
    return _create_sse_response(
        _knowledge_sse_stream(
            request=request,
            stream_generator=knowledge_tutor_agent.analyze_knowledge_stream(
                current_node=current_node,
                target_position=job_profile_text,
                graph_context=graph_context,
                user_profile=user_profile_text,
                industry_data=industry_data
            )
        )
    )


@router.post("/explain/stream")
async def explain_knowledge_stream(
        request: Request,
        current_node: str = Form(..., description="当前知识点名称"),
        job_id: int = Form(..., description="目标岗位ID"),
        user_id: int = Form(..., description="用户ID"),
        graph_context: str = Form("", description="图谱关系"),
        _: bool = Depends(validate_token)
):
    """
    流式解释知识点内容（SSE）
    
    用于"知识精讲"标签页
    """
    job_profile_text, user_profile_text = await get_profile_text(job_id, user_id)
    return _create_sse_response(
        _knowledge_sse_stream(
            request=request,
            stream_generator=knowledge_tutor_agent.explain_knowledge_stream(
                current_node=current_node,
                target_position=job_profile_text,
                graph_context=graph_context,
                user_profile=user_profile_text
            )
        )
    )


async def _knowledge_sse_stream(
        request: Request,
        stream_generator
):
    """
    通用 SSE 事件流生成器
    
    Args:
        request: FastAPI 请求对象
        stream_generator: 流生成器
        
    Yields:
        SSE 格式的数据流
    """
    event_id = 0
    try:
        async for chunk in stream_generator:
            if await request.is_disconnected():
                log.info(f"客户端断开连接，停止流式传输")
                break

            event_id += 1
            chunk_data = json.loads(chunk)
            chunk_type = chunk_data.get("type", "content")

            # 标准 SSE 格式
            yield f"event: {chunk_type}\n"
            yield f"data: {chunk}\n"
            yield f"id: {event_id}\n\n"

            await asyncio.sleep(0)

        # 发送结束事件
        yield f"event: done\n"
        yield f"data: {json.dumps({'status': 'completed'})}\n"
        yield f"id: {event_id + 1}\n\n"

    except Exception as e:
        log.error(f"知识点讲解失败: {e}", exc_info=True)
        yield f"event: error\n"
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


def _create_sse_response(stream_generator):
    """
    创建 SSE 流式响应
    
    Args:
        stream_generator: 流生成器
        
    Returns:
        StreamingResponse 对象
    """
    # noinspection SpellCheckingInspection
    return StreamingResponse(
        stream_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Content-Type-Options": "nosniff",
            "Access-Control-Allow-Origin": "*",
        }
    )
