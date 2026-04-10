from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from starlette.responses import JSONResponse

from ai_service.response.result import success
from ai_service.models.career_graph import CareerPathBundle
from ai_service.services.graph_planner import GraphPlanner
from ai_service.repository.career_repository import CareerRepository
from ai_service.services import log
from config import settings


__all__ = ["router"]
router = APIRouter(prefix="/graph_path", tags=["graph_path"])


class JobIdRequest(BaseModel):
    """仅用 job_id 请求路径（证据优先接口）。"""

    job_id: str = Field(description="起点岗位ID")


class GoalPathRequest(BaseModel):
    """目标设定与职业路径规划请求。"""

    start_job_id: str = Field(description="起点岗位ID")
    target_job_id: str = Field(description="目标岗位ID")
    limit_paths: int = Field(
        default=10, ge=1, le=50, description="返回最大候选路径条数"
    )


def get_career_repository() -> CareerRepository:
    """获取 CareerRepository 实例"""
    return CareerRepository(
        url=settings.neo4j.url,
        username=settings.neo4j.username,
        password=settings.neo4j.password.get_secret_value(),
    )


def get_graph_planner(
    repo: CareerRepository = Depends(get_career_repository),
) -> GraphPlanner:
    """获取 GraphPlanner 实例"""
    return GraphPlanner(repository=repo)


@router.post(
    "/promotion_path/single",
    response_model=CareerPathBundle,
    summary="获取垂直晋升路径（1-5跳）",
)
async def get_vertical_promotion_paths(
    request: JobIdRequest,
    planner: GraphPlanner = Depends(get_graph_planner),
) -> JSONResponse:
    """垂直晋升：同 micro 赛道内深挖技能与跃迁（每跳不跨微/宏社区，salary_gain>0）。"""
    try:
        bundle = planner.build_vertical_promotion_bundle(request.job_id)
        return success(bundle)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ 垂直晋升路径计算失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/transfer_path/single",
    response_model=CareerPathBundle,
    summary="获取换岗路径（1-2跳）",
)
async def get_lateral_transfer_paths(
    request: JobIdRequest,
    planner: GraphPlanner = Depends(get_graph_planner),
) -> JSONResponse:
    """换岗：同 macro 行业内不同 micro 赛道（每跳跨微社区且不跨宏社区）。"""
    try:
        bundle = planner.build_lateral_transfer_bundle(request.job_id)
        if not bundle.paths:
            raise HTTPException(status_code=404, detail="未找到符合换岗条件的路径")
        return success(bundle)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ 换岗路径计算失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/career_path/cross_industry",
    response_model=CareerPathBundle,
    summary="获取跨界跃迁路径（1-2跳）",
)
async def get_cross_industry_paths(
    request: JobIdRequest,
    planner: GraphPlanner = Depends(get_graph_planner),
) -> JSONResponse:
    """跨界跃迁：路径中至少一跳跨宏观社区（is_cross_macro=true）。"""
    try:
        bundle = planner.build_cross_industry_bundle(request.job_id)
        if not bundle.paths:
            raise HTTPException(status_code=404, detail="未找到符合跨界条件的路径")
        return success(bundle)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ 跨界跃迁路径计算失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/goal_path/single",
    response_model=CareerPathBundle,
    summary="目标设定与职业路径规划（start→target，多路径）",
)
async def get_goal_planning_paths(
    request: GoalPathRequest,
    planner: GraphPlanner = Depends(get_graph_planner),
) -> JSONResponse:
    """给定起点岗位与目标岗位，返回多条候选发展路径（总成本低的优先）。"""

    try:
        bundle = planner.build_goal_planning_bundle(
            start_job_id=request.start_job_id,
            target_job_id=request.target_job_id,
            limit_paths=request.limit_paths,
        )
        if not bundle.paths:
            raise HTTPException(status_code=404, detail="未找到从起点到目标的可达路径")
        return success(bundle)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ 目标路径规划计算失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="健康检查", description="检查图路径服务是否正常")
async def health_check():
    """健康检查端点"""
    return success({"status": "healthy", "service": "graph_path"})
