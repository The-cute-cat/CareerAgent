import json
from enum import Enum

from fastapi import APIRouter, Depends, Form, BackgroundTasks

__all__ = ["router"]

from ai_service.agents.test_question_agent import test_question_agent
from ai_service.response.result import success
from ai_service.schemas.auth import validate_token
from ai_service.services.redis_service import RedisService
from ai_service.utils.fingerprint_util import text_fingerprint
from ai_service.utils.logger_handler import log
from config import settings

router = APIRouter(prefix="/question", tags=["question"])
redis = RedisService.get_instance("question")


class QuestionType(str, Enum):
    skill = "skill"
    tool = "tool"


@router.post("/generate")
async def generate_test_question(
        content: str = Form(None, alias="content"),
        question_type: QuestionType = Form(None, alias="question_type"),
        cache_enabled: bool = Form(False, alias="cache_enabled"),
        _: bool = Depends(validate_token),
        background_tasks: BackgroundTasks = None
):
    if cache_enabled:
        try:
            cache = get_cache(content)
            if cache:
                return success(cache)
        except Exception as e:
            log.error(f"获取缓存失败: {str(e)},content:{content}")
    questions = []
    if question_type == QuestionType.skill:
        questions = await test_question_agent.generate_test_questions(skill=content)
    elif question_type == QuestionType.tool:
        questions = await test_question_agent.generate_test_questions(tool=content)
    result = await _check_question(questions, content)
    background_tasks.add_task(save_cache, content, result)
    return success(result)


@router.post("/check_student_answer")
async def check_student_answer(
        questions: str = Form(None, alias="questions"),
        evaluation_criteria=Form(None, alias="evaluation_criteria"),
        student_answer=Form(None, alias="student_answer"),
        _: bool = Depends(validate_token)
):
    result = await test_question_agent.check_student_answer(questions, evaluation_criteria, student_answer)
    return success(json.loads(result))


async def _check_question(questions: str, skill_or_tool: str):
    log.info("问题生成成功,正在检查问题。")
    report = await test_question_agent.check_test_questions(questions, skill_or_tool)
    json_data = json.loads(report)
    if json_data["review_result"] == "Fail":
        log.info("检查到问题存在问题,正在修改问题。")
        questions = await test_question_agent.modify_test_questions(questions, skill_or_tool, report)
    log.info("问题检查成功,返回问题。")
    return json.loads(questions)


def get_cache(content: str):
    if not redis.is_available:
        return None
    fingerprint = text_fingerprint(content)
    return redis.get(fingerprint, None, ttl=settings.redis.cache_timeout.question)


def save_cache(content: str, questions: list[str | dict]):
    if not redis.is_available:
        return
    if not questions or not content or not isinstance(questions, list) or len(questions) == 0:
        return
    fingerprint = text_fingerprint(content)
    redis.set(fingerprint, questions, ttl=settings.redis.cache_timeout.question)
