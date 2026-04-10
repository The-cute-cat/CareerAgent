import json

from fastapi import APIRouter, Depends, Form, BackgroundTasks, Body
from sqlalchemy.ext.asyncio import AsyncSession

from ai_service.agents.growth_plan_agent import growth_plan_agent
from ai_service.agents.report_assistant_agent import report_assistant_agent
from ai_service.agents.user_job_match_analyzer import analyze_user_job_match, get_profile_text
from ai_service.response.result import error_msg, success
from ai_service.schemas.auth import validate_token
from ai_service.services.database_manage import get_db

from ai_service.schemas.report import ReportCheckRequest, ParagraphPolishRequest
from ai_service.services.redis_service import RedisService
from ai_service.utils.fingerprint_util import text_fingerprint
from ai_service.utils.logger_handler import log
from config import settings

__all__ = ["router"]

router = APIRouter(prefix="/report", tags=["report"])
redis = RedisService.get_instance("report")


@router.post("/plan")
async def get_plan(
        job_id: int = Form(0, alias="job_id"),
        user_id: int = Form(0, alias="user_id"),
        cache_enabled: bool = Form(True, alias="cache_enabled"),
        _: bool = Depends(validate_token),
        background_tasks: BackgroundTasks = None
):
    job_profile_text, user_profile_text = None, None
    if cache_enabled:
        try:
            job_profile_text, user_profile_text = await get_profile_text(job_id, user_id)
            cache = _get_plan_cache(job_profile_text, user_profile_text)
            if cache:
                return success(cache)
        except Exception as e:
            log.error(f"获取缓存失败: {str(e)}")
    analyzer_result = await analyze_user_job_match(job_id, user_id, job_profile_text, user_profile_text)
    if "error" in analyzer_result:
        return error_msg(analyzer_result.get("error", ""))
    growth_plan = await growth_plan_agent.generate_growth_plan(
        target_position_profile=analyzer_result.get("job_profile_text", None),
        student_profile=analyzer_result.get("user_profile_text", None),
        ability_gap=analyzer_result.get("analysis", None)
    )
    background_tasks.add_task(_save_plan_cache, job_profile_text, user_profile_text, growth_plan)
    return success(growth_plan)


@router.post("/check", summary="报告完整性检查")
async def check_report_integrity(
        request: ReportCheckRequest = Body(...),
        db: AsyncSession = Depends(get_db),
        _: bool = Depends(validate_token)
):
    """
    检查职业规划报告的完整性

    检查以下4个关键要素是否齐全：
    1. 人岗匹配四维度量化分析（基础要求、职业技能、职业素养、发展潜力）
    2. 职业发展路径规划（垂直晋升或换岗转型）
    3. 分阶段行动计划（短期、中期）
    4. 评估周期与指标

    注意：用户画像会根据 user_id 自动从数据库查询，无需前端传递

    Returns:
        检查结果，包含完整性判断、各维度详情、缺失项列表、总体评分
    """
    try:
        log.info(f"收到报告完整性检查请求 | 用户: {request.user_id} | 岗位: {request.job_title or '未指定'}")
        if not request.report_content or len(request.report_content.strip()) < 50:
            return error_msg("报告内容过短，至少需要50个字符", code=400)
        result = await report_assistant_agent.check_report_integrity(
            report_content=request.report_content,
            db_session=db,
            user_id=request.user_id,
            job_title=request.job_title
        )
        log.info(f"报告完整性检查完成 | 完整性: {result.get('is_complete')} | 评分: {result.get('overall_score')}")
        return success(result)
    except Exception as e:
        log.error(f"报告完整性检查异常: {e}", exc_info=True)
        return error_msg(f"检查失败：{str(e)}", code=500)


@router.post("/polish", summary="段落智能润色")
async def polish_paragraph(
        request: ParagraphPolishRequest = Body(...),
        _: bool = Depends(validate_token)
):
    """
    智能润色报告段落

    根据报告类型动态切换润色策略：
    - match_analysis：人岗匹配分析润色（强制四维度分析）
    - action_plan：行动计划润色（确保SMART原则）
    - other：通用润色（精炼、专业、有指导意义）

    **核心约束：**
    - 防幻觉：不能捏造用户没有的技能、证书或经历
    - 维度红线：匹配分析必须从4个维度进行
    - 质量红线：内容必须具备可操作性和可解释性

    Returns:
        润色后的内容，包含原始内容对比
    """
    try:
        log.info(f"收到段落润色请求 | 类型: {request.report_type}")
        valid_types = ["match_analysis", "action_plan", "other"]
        if request.report_type not in valid_types:
            return error_msg(
                f"无效的报告类型：{request.report_type}，有效值为：{', '.join(valid_types)}",
                code=400
            )
        if not request.original_content or len(request.original_content.strip()) < 20:
            return error_msg("原始内容过短，至少需要20个字符", code=400)
        polished_content = await report_assistant_agent.polish_paragraph(
            original_content=request.original_content,
            report_type=request.report_type,
            context=request.context
        )
        response_data = {
            "original_content": request.original_content,
            "polished_content": polished_content,
            "report_type": request.report_type,
            "length_before": len(request.original_content),
            "length_after": len(polished_content)
        }
        log.info(
            f"段落润色完成 | 类型: {request.report_type} | "
            f"长度变化: {response_data['length_before']} -> {response_data['length_after']}"
        )
        return success(response_data)
    except Exception as e:
        log.error(f"段落润色异常: {e}", exc_info=True)
        return error_msg(f"润色失败：{str(e)}", code=500)


def _get_plan_cache(job_profile_text, user_profile_text):
    if not redis.is_available:
        return None
    json_profile_text = {
        "job_profile_text": job_profile_text,
        "user_profile_text": user_profile_text
    }
    str_profile_text = json.dumps(json_profile_text, ensure_ascii=False, sort_keys=True)
    fingerprint = text_fingerprint(str_profile_text)
    return redis.get(fingerprint, None, ttl=settings.redis.cache_timeout.report)


def _save_plan_cache(job_profile_text, user_profile_text, growth_plan):
    if not redis.is_available:
        return
    if not growth_plan or not job_profile_text or not user_profile_text:
        return
    json_profile_text = {
        "job_profile_text": job_profile_text,
        "user_profile_text": user_profile_text
    }
    str_profile_text = json.dumps(json_profile_text, ensure_ascii=False, sort_keys=True)
    fingerprint = text_fingerprint(str_profile_text)
    redis.set(fingerprint, growth_plan, ttl=settings.redis.cache_timeout.report)
