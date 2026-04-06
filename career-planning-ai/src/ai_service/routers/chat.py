"""
对话路由 - Chat Router

提供对话相关的 API 接口：
1. 普通对话（阻塞方式）
2. 流式对话（SSE 方式）
3. 支持文件上传
4. 会话管理（列表、删除、更新标题）
"""
from fastapi import APIRouter, Depends, Form, Request, Query
from fastapi.responses import StreamingResponse

from ai_service.agents.conversation_agent import conversation_agent
from ai_service.response.result import success, error_msg
from ai_service.schemas.auth import validate_token
from ai_service.schemas.file import handle_files
from ai_service.services.database_manage import AsyncSessionLocal
from ai_service.services.extract_text import extract_from_file
from ai_service.utils.logger_handler import log

__all__ = ["router"]

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message")
async def chat_with_message(
        message: str = Form(..., description="消息内容"),
        user_id: str = Form(..., description="用户ID"),
        conversation_id: str | None = Form(None, description="对话ID"),
        auto_extract_memory: bool = Form(True, description="是否自动提取记忆"),
        _: bool = Depends(validate_token)
):
    """纯文本消息对话（阻塞方式）"""
    log.warning("⚠️警告：该接口正在测试中，可能存在问题")
    try:
        session_id = conversation_id or "default_session"
        async with AsyncSessionLocal() as db_session:
            response = await conversation_agent.chat(
                user_id=user_id,
                session_id=session_id,
                user_message=message,
                db_session=db_session,
                auto_extract_memory=auto_extract_memory
            )
            return success({
                "message": response,
                "conversationId": session_id
            })
    except Exception as e:
        log.error(f"对话处理失败: {e}", exc_info=True)
        return error_msg(f"对话处理失败: {str(e)}")


@router.post("/message/stream")
async def chat_with_message_stream(
        request: Request,
        message: str = Form(..., description="消息内容"),
        user_id: str = Form(..., description="用户ID"),
        conversation_id: str | None = Form(None, description="对话ID"),
        auto_extract_memory: bool = Form(True, description="是否自动提取记忆"),
        _: bool = Depends(validate_token)
):
    """纯文本消息对话（流式方式 - SSE）"""
    log.warning("⚠️警告：该接口正在测试中，可能存在问题")
    log.info(f"会话id:{conversation_id}")
    session_id = conversation_id or "default_session"
    return _create_sse_response(
        _create_sse_stream(request, user_id, session_id, message, auto_extract_memory)
    )


@router.post("/files")
async def chat_with_files(
        files: list[dict[str, str]] = Depends(handle_files),
        user_id: str = Form(..., description="用户ID"),
        conversation_id: str | None = Form(None, description="对话ID"),
        auto_extract_memory: bool = Form(False, description="是否自动提取记忆"),
        _: bool = Depends(validate_token)
):
    """仅文件上传对话（阻塞方式）"""
    log.warning("⚠️警告：该接口正在测试中，可能存在问题")
    try:
        session_id = conversation_id or "default_session"
        file_texts = await _extract_files_text(files)
        combined_message = "我上传了以下文件，请帮我分析：\n\n" + "\n\n".join(file_texts)
        async with AsyncSessionLocal() as db_session:
            response = await conversation_agent.chat(
                user_id=user_id,
                session_id=session_id,
                user_message=combined_message,
                db_session=db_session,
                auto_extract_memory=auto_extract_memory
            )
            return success({
                "message": response,
                "conversationId": session_id,
                "fileCount": len(files)
            })
    except Exception as e:
        log.error(f"文件对话处理失败: {e}", exc_info=True)
        return error_msg(f"文件对话处理失败: {str(e)}")


@router.post("/message-and-files")
async def chat_with_message_and_files(
        message: str = Form(..., description="消息内容"),
        files: list[dict[str, str]] = Depends(handle_files),
        user_id: str = Form(..., description="用户ID"),
        conversation_id: str | None = Form(None, description="对话ID"),
        auto_extract_memory: bool = Form(False, description="是否自动提取记忆"),
        _: bool = Depends(validate_token)
):
    """消息+文件对话（阻塞方式）"""
    log.warning("⚠️警告：该接口正在测试中，可能存在问题")
    try:
        session_id = conversation_id or "default_session"
        file_texts = await _extract_files_text(files)
        combined_message = f"{message}\n\n以下是我上传的文件内容：\n\n" + "\n\n".join(file_texts)
        async with AsyncSessionLocal() as db_session:
            response = await conversation_agent.chat(
                user_id=user_id,
                session_id=session_id,
                user_message=combined_message,
                db_session=db_session,
                auto_extract_memory=auto_extract_memory
            )
            return success({
                "message": response,
                "conversationId": session_id,
                "fileCount": len(files)
            })
    except Exception as e:
        log.error(f"消息+文件对话处理失败: {e}", exc_info=True)
        return error_msg(f"消息+文件对话处理失败: {str(e)}")


@router.post("/message-and-files/stream")
async def chat_with_message_and_files_stream(
        request: Request,
        message: str = Form(..., description="消息内容"),
        files: list[dict[str, str]] = Depends(handle_files),
        user_id: str = Form(..., description="用户ID"),
        conversation_id: str | None = Form(None, description="对话ID"),
        auto_extract_memory: bool = Form(True, description="是否自动提取记忆"),
        _: bool = Depends(validate_token)
):
    """消息+文件对话（流式方式 - SSE）"""
    log.warning("⚠️警告：该接口正在测试中，可能存在问题")
    session_id = conversation_id or "default_session"
    async def event_stream():
        try:
            file_texts = await _extract_files_text(files)
            combined_message = f"{message}\n\n以下是我上传的文件内容：\n\n" + "\n\n".join(file_texts)
            async for chunk in _create_sse_stream(
                    request, user_id, session_id, combined_message, auto_extract_memory
            ):
                yield chunk
        except Exception as e:
            log.error(f"流式消息+文件对话处理失败: {e}", exc_info=True)
            yield f"data: [ERROR] {str(e)}\n\n"

    return _create_sse_response(event_stream())


@router.get("/history/{session_id}")
async def get_chat_history(
        session_id: str,
        limit: int | None = None,
        _: bool = Depends(validate_token)
):
    """获取会话历史记录"""
    log.warning("⚠️警告：该接口正在测试中，可能存在问题")
    try:
        history = await conversation_agent.get_session_history(session_id, limit)
        return success({
            "sessionId": session_id,
            "history": history,
            "count": len(history)
        })
    except Exception as e:
        log.error(f"获取会话历史失败: {e}", exc_info=True)
        return error_msg(f"获取会话历史失败: {str(e)}")


@router.delete("/session/{session_id}")
async def clear_session(
        session_id: str,
        _: bool = Depends(validate_token)
):
    """清除会话的短期记忆并软删除持久化记录"""
    log.warning("⚠️警告：该接口正在测试中，可能存在问题")
    try:
        async with AsyncSessionLocal() as db_session:
            success_flag = await conversation_agent.clear_session(session_id, db_session)
            if success_flag:
                return success({"message": f"会话 {session_id} 已清除"})
            else:
                return error_msg(f"清除会话失败", 500)
    except Exception as e:
        log.error(f"清除会话失败: {e}", exc_info=True)
        return error_msg(f"清除会话失败: {str(e)}")


@router.get("/sessions")
async def get_user_sessions(
        user_id: str = Query(..., description="用户ID"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        _: bool = Depends(validate_token)
):
    """获取用户的会话列表"""
    log.warning("⚠️警告：该接口正在测试中，可能存在问题")
    try:
        async with AsyncSessionLocal() as db_session:
            result = await conversation_agent.get_user_sessions(
                user_id=user_id,
                page=page,
                page_size=page_size,
                db_session=db_session
            )
            return success(result)
    except Exception as e:
        log.error(f"获取会话列表失败: {e}", exc_info=True)
        return error_msg(f"获取会话列表失败: {str(e)}")


@router.put("/session/{session_id}/title")
async def update_session_title(
        session_id: str,
        title: str = Form(..., description="会话标题"),
        _: bool = Depends(validate_token)
):
    """更新会话标题"""
    log.warning("⚠️警告：该接口正在测试中，可能存在问题")
    try:
        async with AsyncSessionLocal() as db_session:
            success_flag = await conversation_agent.update_session_title(
                session_id=session_id,
                title=title,
                db_session=db_session
            )
            await db_session.commit()
            if success_flag:
                return success({"message": f"会话标题已更新"})
            else:
                return error_msg(f"会话不存在", 404)
    except Exception as e:
        log.error(f"更新会话标题失败: {e}", exc_info=True)
        return error_msg(f"更新会话标题失败: {str(e)}")


async def _extract_files_text(files: list[dict[str, str]]) -> list[str]:
    """
    提取所有文件的文本内容

    Args:
        files: 文件信息列表，包含字段：
            - save_path: 服务器保存的完整路径
            - extension: 文件真实扩展名
            - original_name: 用户上传时的原始文件名
            - file_name: 服务器保存的文件名（UUID）
            - size: 文件大小
            - mime_type: MIME 类型

    Returns:
        文件文本列表（格式：【文件: original_name】\n内容）
    """
    file_texts = []
    for file_info in files:
        text = await extract_from_file(file_info["save_path"], file_info["extension"])
        file_texts.append(f"【文件: {file_info.get('original_name', 'unknown')}】\n{text}")
    return file_texts


async def _create_sse_stream(
        request: Request,
        user_id: str,
        session_id: str,
        message: str,
        auto_extract_memory: bool
):
    """
    SSE 事件流生成器

    Args:
        request: FastAPI 请求对象
        user_id: 用户 ID
        session_id: 会话 ID
        message: 消息内容
        auto_extract_memory: 是否自动提取记忆

    Yields:
        SSE 格式的数据流
    """
    try:
        async with AsyncSessionLocal() as db_session:
            async for chunk in conversation_agent.chat_stream(
                    user_id=user_id,
                    session_id=session_id,
                    user_message=message,
                    db_session=db_session,
                    auto_extract_memory=auto_extract_memory
            ):
                if await request.is_disconnected():
                    log.info(f"客户端断开连接，停止流式传输: session_id={session_id}")
                    break
                yield f"data: {chunk}\n\n"
            yield f"data: [DONE]\n\n"
    except Exception as e:
        log.error(f"流式对话处理失败: {e}", exc_info=True)
        yield f"data: [ERROR] {str(e)}\n\n"


def _create_sse_response(stream_generator):
    """
    创建 SSE 流式响应

    Args:
        stream_generator: 流生成器

    Returns:
        StreamingResponse 对象
    """
    return StreamingResponse(
        stream_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
