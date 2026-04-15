import asyncio
import json

from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from pydantic import ConfigDict, SecretStr

from ai_service.repository.connection_session import AsyncSessionLocal
from ai_service.repository.job_portrait_repository import JobPortraitRepository
from ai_service.repository.stu_portrait_repository import StuProfileRepository
from ai_service.services import log
from ai_service.services.prompt_loader import prompt_loader
from config import settings

load_dotenv()

# =========================
# 1. 定义输出结构
# =========================

from pydantic import BaseModel, Field
from typing import Dict, Any


class UserJobMatchResult(BaseModel):
    overall_summary: str = Field(..., description="总体评价总结", alias="总体评价总结")
    match_level: str = Field(..., description="匹配等级，如 高 / 中 / 低", alias="匹配等级")
    strengths: Dict[str, Any] = Field(..., description="用户优势分析", alias="优势分析")
    weaknesses: Dict[str, Any] = Field(..., description="用户不足分析", alias="不足分析")
    improvement_suggestions: Dict[str, Any] = Field(..., description="改进建议", alias="改进建议")
    interview_risk_points: Dict[str, Any] = Field(..., description="求职/面试风险点", alias="面试风险点")
    final_advice: str = Field(..., description="最终建议", alias="最终建议")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow"  # ✅ 允许AI返回任意多余字段，不会报错
    )


# =========================
# 2. Prompt
# =========================

SYSTEM_PROMPT = prompt_loader.user_job_match_analyzer

USER_PROMPT = prompt_loader.small_prompts["user_job_match_analyzer_user"]


# =========================
# 3. 创建 LLM
# =========================

def _create_llm(
        api_key: str | SecretStr,
        model_name: str,
) -> ChatTongyi:
    return ChatTongyi(
        api_key=api_key,
        model=model_name,
        streaming=True,
    )


# =========================
# 4. 序列化画像
# =========================

def _safe_json_dumps(data: Any) -> str:
    try:
        return json.dumps(data, ensure_ascii=False, indent=2, default=str)
    except Exception:
        return str(data)


def _build_profile_json_text(data: Any, default_text: str = "未提及") -> str:
    if data is None:
        log.warning(f"画像数据为空，回退到默认文本: {default_text}")
        return default_text
    try:
        return json.dumps(data, ensure_ascii=False, indent=2, default=str)
    except Exception:
        log.warning(f"序列化画像失败，回退到 str: {data}")
        return str(data)


# =========================
# 5. 解析 JSON
# =========================

def _extract_json_text(raw_content: str) -> Dict[str, Any]:
    """
    尝试从 LLM 返回内容中提取 JSON
    """
    raw_content = raw_content.strip()

    try:
        return json.loads(raw_content)
    except Exception:
        pass

    start = raw_content.find("{")
    end = raw_content.rfind("}")
    if start != -1 and end != -1 and end > start:
        json_str = raw_content[start:end + 1]
        return json.loads(json_str)

    raise ValueError("LLM 返回内容不是合法 JSON")


# =========================
# 6. 主函数
# =========================

async def analyze_user_job_match(
        job_id: int,
        user_id: int,
        api_key: str | None = settings.llm.api_key.get_secret_value(),
        model_name: str = settings.vector.llm_model_name,
) -> Dict[str, Any]:
    """
    根据岗位ID和用户ID，分析用户与岗位的匹配情况
    函数内部自行创建 session 和 repository
    """

    job_profile_text = ""
    user_profile_text = ""

    try:

        # 2. 内部创建 session 和 repo
        async with AsyncSessionLocal() as session:
            job_portrait_repo = JobPortraitRepository(session)
            user_portrait_repo = StuProfileRepository(session)

            # 3. 查询岗位画像
            job_profile = await job_portrait_repo.get_by_id(job_id)
            if not job_profile:
                raise ValueError(f"未找到岗位画像，job_id={job_id}")

            # 4. 查询用户画像
            user_profile = await user_portrait_repo.get_by_stu_id(user_id)
            if not user_profile:
                raise ValueError(f"未找到用户画像，user_id={user_id}")

            # 5. 构造输入文本
            job_profile_text = _build_profile_json_text(job_profile.skills_req)
            user_profile_text = _build_profile_json_text(user_profile.skills_stu)

        # 6. 创建模型
        llm = _create_llm(api_key=api_key, model_name=model_name)
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", USER_PROMPT),
        ])
        log.info("提示词构造完成")

        chain = prompt | llm

        try:
            raw_result = await chain.ainvoke({
                "job_profile_text": job_profile_text,
                "user_profile_text": user_profile_text,
            })
        except Exception as async_error:
            log.warning(f"ainvoke 调用失败，回退到线程池 invoke: {async_error}")
            raw_result = await asyncio.to_thread(
                chain.invoke,
                {
                    "job_profile_text": job_profile_text,
                    "user_profile_text": user_profile_text,
                }
            )

        content = getattr(raw_result, "content", str(raw_result))
        try:
            parsed = _extract_json_text(content)
            log.info(f"解析后的JSON: {json.dumps(parsed, ensure_ascii=False)[:500]}...")  # 记录解析结果
        except Exception as e:
            log.error(f"JSON解析失败: {e}, 原始内容: {content}")
            raise ValueError(f"AI 返回的内容无法解析为 JSON: {e}")

        result = UserJobMatchResult.model_validate(parsed)
        return {
            "job_profile_text": job_profile_text,
            "user_profile_text": user_profile_text,
            "analysis": result.model_dump(by_alias=True),
        }

    except Exception as e:
        log.error(f"用户岗位匹配分析失败: {e}", exc_info=True)
        return {
            "error": str(e),
            "job_id": job_id,
            "user_id": user_id,
            "job_profile_text": job_profile_text,
            "user_profile_text": user_profile_text,
        }

# if __name__ == '__main__':
## 简单测试
# test_job_id = 65  # 替换为实际 job_id
# test_user_id = 1  # 替换为实际 user_id
#
# result = asyncio.run(analyze_user_job_match(test_job_id, test_user_id))
# if "error" in result:
#     print(f"❌ 分析失败: {result['error']}")
# else:
#     print("✅ 分析结果:")
#     print(str(result.get("analysis", {})))
