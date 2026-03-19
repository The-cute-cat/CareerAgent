import json

from fastapi import APIRouter, Depends, Form

__all__ = ["router"]

from ai_service.agents.test_question_agent import test_question_agent
from ai_service.response.result import success
from ai_service.schemas.auth import validate_token

router = APIRouter(prefix="/test_question", tags=["test_question"])


@router.post("/skill_generate")
async def generate_test_question_skill(skill: str = Form(None, alias="skill"), _: bool = Depends(validate_token)):
    questions = await test_question_agent.generate_test_questions(skill=skill)
    return success(await _check_question(questions, skill))


@router.post("/tool_generate")
async def generate_test_question_tool(
        tool: str = Form(None, alias="tool"),
        _: bool = Depends(validate_token)
):
    questions = await test_question_agent.generate_test_questions(tool=tool)
    return success(await _check_question(questions, tool))


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
    report = await test_question_agent.check_test_questions(questions, skill_or_tool)
    json_data = json.loads(report)
    if json_data["review_result"] == "Fail":
        questions = await test_question_agent.modify_test_questions(questions, skill_or_tool, report)
    return json.loads(questions)
