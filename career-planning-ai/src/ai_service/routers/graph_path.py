from typing import List

from fastapi import APIRouter, Body, HTTPException, Depends
from pydantic import BaseModel, Field

from ai_service.response.result import success, JSONResponse
from ai_service.models.career_graph import CareerPathBundle
from ai_service.models.struct_job_txt import JDAnalysisResult
from ai_service.services.career_analyst_agent import DeepAnalysisResult
from ai_service.services.graph_planner import GraphPlanner
from ai_service.repository.career_repository import CareerRepository
from ai_service.services import log
from config import settings


__all__ = ["router"]
router = APIRouter(prefix="/graph_path", tags=["graph_path"])


class TargetJob(BaseModel):
    """起始岗位（前端单个元素）"""

    job_id: str = Field(description="岗位ID")
    score: float = Field(description="匹配分数")
    raw_data: JDAnalysisResult = Field(description="原始岗位数据")
    deep_analysis: DeepAnalysisResult = Field(description="深度分析结果")


StartingJob = TargetJob


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
    "/transfer_path/batch",
    response_model=List[CareerPathBundle],
    summary="获取职业发展路径（批量处理）",
)
async def get_career_paths_batch(
    request: List[StartingJob] = Body(
        ..., description="前端批量查询传来的起始岗位列表"
    ),
    planner: GraphPlanner = Depends(get_graph_planner),
) -> JSONResponse:
    """批量：每个元素为起始岗位，后端读取其横向转岗意向并规划纯岗位间路径"""
    try:
        bundles: List[CareerPathBundle] = []
        for starting_job in request:
            bundle = await planner.build_lateral_paths_with_llm(
                starting_job=starting_job,
            )
            bundles.append(bundle)
        return success(bundles)
    except Exception as e:
        log.error(f"批量计算职业路径失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/transfer_path/single",
    response_model=CareerPathBundle,
    summary="获取职业发展路径（单个目标）",
)
async def get_career_path_single(
    request: StartingJob = Body(..., description="前端单次查询传来的起始岗位"),
    planner: GraphPlanner = Depends(get_graph_planner),
) -> JSONResponse:
    """单个：读取起始岗位横向转岗意向并规划纯岗位间路径"""
    try:
        bundle = await planner.build_lateral_paths_with_llm(
            starting_job=request,
        )
        return success(bundle)
    except Exception as e:
        log.error(f"单个计算职业路径失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/promotion_path/batch",
    response_model=List[CareerPathBundle],
    summary="获取垂直晋升路径（批量处理）",
)
async def get_vertical_paths_batch(
    request: List[StartingJob] = Body(
        ..., description="前端批量查询传来的起始岗位列表"
    ),
    planner: GraphPlanner = Depends(get_graph_planner),
) -> JSONResponse:
    """批量：为每个起始岗位规划纯岗位间的垂直晋升路径。"""
    try:
        bundles: List[CareerPathBundle] = []
        for starting_job in request:
            bundle = await planner.build_vertical_paths_with_llm(
                starting_job=starting_job,
            )
            bundles.append(bundle)
        return success(bundles)
    except Exception as e:
        log.error(f"批量计算晋升路径失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/promotion_path/single",
    response_model=CareerPathBundle,
    summary="获取垂直晋升路径（单个目标）",
)
async def get_vertical_path_single(
    request: StartingJob = Body(..., description="前端单次查询传来的起始岗位"),
    planner: GraphPlanner = Depends(get_graph_planner),
) -> JSONResponse:
    """单个：为起始岗位规划纯岗位间的垂直晋升路径。"""
    try:
        bundle = await planner.build_vertical_paths_with_llm(
            starting_job=request,
        )
        return success(bundle)
    except Exception as e:
        log.error(f"单个计算晋升路径失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="健康检查", description="检查图路径服务是否正常")
async def health_check():
    """健康检查端点"""
    return success({"status": "healthy", "service": "graph_path"})
