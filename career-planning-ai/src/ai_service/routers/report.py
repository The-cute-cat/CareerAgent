import json

from fastapi import APIRouter, Depends, Form, BackgroundTasks

from ai_service.agents.growth_plan_agent import growth_plan_agent
from ai_service.agents.user_job_match_analyzer import analyze_user_job_match, get_profile_text
from ai_service.response.result import error_msg, success
from ai_service.schemas.auth import validate_token

__all__ = ["router"]

from ai_service.services.redis_service import RedisService

from ai_service.utils.fingerprint_util import text_fingerprint
from ai_service.utils.logger_handler import log
from config import settings

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
            cache = get_cache(job_profile_text, user_profile_text)
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
    background_tasks.add_task(save_cache, job_profile_text, user_profile_text, growth_plan)
    return success(growth_plan)


def get_cache(job_profile_text, user_profile_text):
    if not redis.is_available:
        return None
    json_profile_text = {
        "job_profile_text": job_profile_text,
        "user_profile_text": user_profile_text
    }
    str_profile_text = json.dumps(json_profile_text, ensure_ascii=False, sort_keys=True)
    fingerprint = text_fingerprint(str_profile_text)
    return redis.get(fingerprint, None, ttl=settings.redis.cache_timeout.report)


def save_cache(job_profile_text, user_profile_text, growth_plan):
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
