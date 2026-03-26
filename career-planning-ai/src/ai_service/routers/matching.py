from fastapi import APIRouter, Body, Depends

from ai_service.models.struct_txt import StudentProfile
from ai_service.response.result import success
from ai_service.schemas.auth import validate_token
from ai_service.services import log
from ai_service.services.career_analyst_agent import CareerAnalystAgent
from ai_service.utils.job_vector_store import JobVectorStore

__all__ = ["router"]

router = APIRouter(prefix="/matching", tags=["match"])

# 初始化组件 (建议在全局作用域或 lifespan 中初始化以复用连接和模型加载)
store = JobVectorStore()
agent = CareerAnalystAgent()


@router.post("/jobs", summary="基于人物画像进行人岗匹配与深度分析")
async def match_jobs(
        student_profile: StudentProfile = Body(..., description="学生人物画像数据"),
        recall_top_k: int = Body(20, description="向量库初步召回数量"),
        final_top_k: int = Body(5, description="Agent 最终深度分析并返回的数量"),
        _: bool = Depends(validate_token)
):
    """
    传入学生画像，通过向量库召回相关岗位，并使用 LLM Agent 进行深度匹配差距分析。
    """
    try:
        log.info(f"--- 正在为学生匹配最合适的岗位 ---")

        # 1. 向量数据库初步召回
        # 注意：如果 match_jobs_for_student 是同步阻塞方法且耗时较长，建议使用 asyncio.to_thread 包裹
        matches = store.match_jobs_for_student(student_profile, top_k=recall_top_k)

        if not matches:
            log.warning("未召回任何相关岗位")
            return success([])

        # 2. Agent 深度分析与重排 (并发执行)
        # 直接使用 await 调用异步方法，无需 asyncio.run
        final_results = await agent.batch_analyze_async(
            student_profile=student_profile,
            retrieved_jobs=matches,
            top_k=final_top_k
        )

        log.info(f"匹配完成，成功返回 {len(final_results)} 条深度分析结果。")

        # 3. 使用统一的成功响应结构返回 JSON
        return success(final_results)

    except Exception as e:
        log.error(f"人岗匹配接口发生异常: {str(e)}")
        # 假设你有一个错误处理机制或特定的 Error 返回格式
        # 这里可以直接抛出你项目中定义的 CommonHandleError
        from ai_service.exceptions import CommonHandleError
        raise CommonHandleError(f"匹配失败: {str(e)}")
