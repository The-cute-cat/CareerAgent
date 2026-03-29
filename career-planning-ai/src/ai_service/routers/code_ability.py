"""
代码能力评估API路由
"""
from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel, Field

from ai_service.response.result import success, error_msg
from ai_service.schemas.auth import validate_token
from ai_service.services import log
from ai_service.services.code_ability_evaluator import code_ability_evaluator

__all__ = ["router"]

router = APIRouter(prefix="/code-ability", tags=["code-ability"])


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
        _: bool = Depends(validate_token)
):
    """
    代码能力评估接口

    接收用户的GitHub/Gitee主页URL，返回代码能力评分和AI分析报告。
    基础评分约需3-5秒，开启AI分析约需8-15秒。
    """
    try:
        result = await code_ability_evaluator.evaluate(
            url=request.url,
            use_ai=request.use_ai
        )
        return success({
            "platform": result["platform"],
            "username": result["username"],
            "composite_score": result["composite_score"],
            "level": result["level"],
            "features": result["features"],
            "ai_analysis": result["ai_analysis"]
        })
    except ValueError as e:
        log.error(f"评估过程出现错误: {str(e)}")
        return error_msg(str(e), code=400)
    except Exception as e:
        log.error(f"评估过程出现未知错误: {str(e)}")
        return error_msg(f"评估过程出现未知错误: {str(e)}", code=500)
