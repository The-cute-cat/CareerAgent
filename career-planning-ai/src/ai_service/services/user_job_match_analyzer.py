import asyncio
import json
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field, ConfigDict

from ai_service.models.stu_profile import StuProfile
from ai_service.repository.job_portrait_repository import JobPortraitRepository
from ai_service.repository.stu_portrait_repository import StuProfileRepository
from ai_service.services import log
from config import settings

from ai_service.repository.connection_session import AsyncSessionLocal

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

SYSTEM_PROMPT = """
你是一位资深职业规划顾问、招聘专家、技术面试辅导师。

你的任务是：根据【岗位画像】和【用户画像】，详细分析该用户与目标岗位的匹配情况，并以以下 JSON 格式返回结果：

{{
  "总体评价总结": "简短总结整体匹配情况",
  "匹配等级": "高/中/低",
  "优势分析": {{
    "技能优势": ["具体优势描述"],
    "经验优势": ["具体优势描述"],
    "能力优势": ["具体优势描述"]
  }},
  "不足分析": {{
    "技能不足": ["具体不足描述"],
    "经验不足": ["具体不足描述"],
    "能力不足": ["具体不足描述"]
  }},
  "改进建议": {{
    "技能提升": ["具体学习建议"],
    "项目补充": ["具体项目建议"],
    "实习建议": ["具体实习建议"],
    "工具学习": ["具体工具建议"]
  }},
  "面试风险点": {{
    "风险点1": "具体风险描述",
    "风险点2": "具体风险描述"
  }},
  "最终建议": "整体建议总结"
}}

分析维度：
1. 技能匹配情况
2. 工具使用能力匹配情况
3. 实习经历匹配情况
4. 项目经历匹配情况
5. 能力素质匹配情况
6. 用户的优势
7. 用户的不足
8. 明确的改进方向
9. 求职和面试风险点
10. 最终提升建议

要求：
1. 评价必须具体，不能空泛。
2. 要明确指出"为什么是优势 / 为什么是不足"。
3. 改进建议必须可执行，尽量细化到学习方向、补项目方向、补实习方向、补工具方向。
4. 输出必须是合法 JSON，严格按照上述格式。
5. 不要输出 Markdown，不要输出代码块，不要输出额外解释文字。
6. 所有输出必须使用简体中文。
7. 如果某项信息不足，请明确说明"用户画像未体现"或"岗位画像未明确要求"，不要胡乱编造。
"""

USER_PROMPT = """
请根据以下内容进行岗位匹配分析：

【岗位画像】
{job_profile_text}

【用户画像】
{user_profile_text}

请严格输出 JSON。
"""


# =========================
# 3. 创建 LLM
# =========================

def _create_llm(
    api_key: str,
    model_name: str,
) -> ChatTongyi:
    return ChatTongyi(
        api_key=api_key,
        model=model_name,
        temperature=0.2,
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
    api_key: Optional[str] = settings.llm.api_key.get_secret_value(),
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