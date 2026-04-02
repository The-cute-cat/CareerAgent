"""
代码能力评估API路由
"""
import json

from fastapi import APIRouter, Depends, Body, BackgroundTasks
from pydantic import BaseModel, Field

from ai_service.response.result import success, error_msg
from ai_service.schemas.auth import validate_token
from ai_service.services import log
from ai_service.services.code_ability_evaluator import code_ability_evaluator

__all__ = ["router"]

from ai_service.services.redis_service import RedisService
from ai_service.utils.fingerprint_util import text_fingerprint
from config import settings

router = APIRouter(prefix="/code-ability", tags=["code-ability"])

redis = RedisService.get_instance("code_ability")


class EvaluateRequest(BaseModel):
    """代码能力评估请求体"""
    url: str = Field(
        ...,
        description="GitHub或Gitee主页URL",
        examples=["https://github.com/torvalds"]
    )
    use_ai: bool = Field(
        default=True,
        description="是否使用AI大模型进行深度分析"
    )


@router.post("/evaluate")
async def evaluate(
        request: EvaluateRequest = Body(..., description="评估请求体"),
        _: bool = Depends(validate_token),
        background_tasks: BackgroundTasks = None
):
    """
    代码能力评估接口

    接收用户的GitHub/Gitee主页URL，返回代码能力评分和AI分析报告。
    基础评分约需3-5秒，开启AI分析约需8-15秒。
    """
    try:
        try:
            cache = get_cache(request)
            if cache:
                return success(cache)
        except Exception as e:
            log.error(f"获取缓存失败: {str(e)}")
        result = await code_ability_evaluator.evaluate(
            url=request.url,
            use_ai=request.use_ai
        )
        temp = {
            "platform": result["platform"],
            "username": result["username"],
            "composite_score": result["composite_score"],
            "level": result["level"],
            "features": result["features"],
            "ai_analysis": result["ai_analysis"]
        }
        background_tasks.add_task(save_cache, temp, request)
        return success(temp)
    except ValueError as e:
        log.error(f"评估过程出现错误: {str(e)}", exc_info=True)
        return error_msg(str(e), code=400)
    except Exception as e:
        log.error(f"评估过程出现未知错误: {str(e)}", exc_info=True)
        return error_msg(f"评估过程出现未知错误: {str(e)}", code=500)


def get_cache(request: EvaluateRequest):
    if not redis.is_available:
        return None
    str_request = json.dumps(request.model_dump(), sort_keys=True)
    fingerprint = text_fingerprint(str_request)
    return redis.get(fingerprint, None, ttl=settings.redis.cache_timeout.code_ability)


def save_cache(result: dict, request: EvaluateRequest):
    if not redis.is_available:
        return
    str_request = json.dumps(request.model_dump(), sort_keys=True)
    fingerprint = text_fingerprint(str_request)
    redis.set(fingerprint, result, settings.redis.cache_timeout.code_ability)
