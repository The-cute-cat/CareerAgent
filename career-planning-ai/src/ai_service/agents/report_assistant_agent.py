"""
职业规划报告辅助智能体 - ReportAssistantAgent

提供职业规划报告的质量检查与润色服务：
1. 报告完整性检查（四维度量化分析、职业路径、行动计划、评估指标）
2. 段落智能润色（匹配分析、行动计划、通用润色）
"""
import json
import re
from typing import Any, Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from ai_service.agents import log as logger
from ai_service.repository.stu_portrait_repository import StuProfileRepository
from ai_service.services.prompt_loader import prompt_loader
from config import settings

__all__ = [
    "report_assistant_agent",
]


class ReportAssistantAgent:
    """
    职业规划报告辅助智能体
    
    负责：
    - 报告完整性检查：验证关键要素是否齐全
    - 段落智能润色：根据类型动态优化内容
    - 用户画像查询：从数据库自动获取用户信息
    """

    def __init__(self):
        """初始化报告辅助智能体"""
        self.llm = ChatOpenAI(
            api_key=settings.report_assistant.api_key.get_secret_value(),
            model=settings.report_assistant.model_name,
            base_url=settings.report_assistant.base_url,
            timeout=settings.report_assistant.timeout,
            max_retries=settings.report_assistant.max_retries,
            temperature=settings.report_assistant.extra.get("temperature", 0.2)
        )
        logger.info("ReportAssistantAgent 初始化完成")

    async def check_report_integrity(
            self,
            report_content: str,
            db_session: AsyncSession,
            user_id: int,
            job_title: Optional[str] = None
    ) -> dict[str, Any]:
        """
        检查报告内容的完整性
        
        Args:
            report_content: 报告文本内容
            db_session: 数据库会话
            user_id: 用户ID（用于查询用户画像）
            job_title: 目标岗位名称（可选）
            
        Returns:
            检查结果字典，包含：
            - is_complete: 是否完整
            - check_results: 各维度检查详情
            - missing_items: 缺失项列表
            - overall_score: 总体评分
            - summary: 整体评价
        """
        response_text = []
        try:
            logger.info(f"开始检查报告完整性 | 用户: {user_id} | 岗位: {job_title or '未指定'}")
            
            # 从数据库查询用户画像
            user_profile_summary = await self._get_user_profile_summary(db_session, user_id)
            
            # 构建提示词
            system_prompt = prompt_loader.report_check
            user_input = f"# 报告内容\n\n{report_content}\n"
            if job_title:
                user_input = f"# 目标岗位\n{job_title}\n\n{user_input}"
            if user_profile_summary:
                user_input = f"{user_input}\n# 用户画像摘要\n{user_profile_summary}\n"
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            
            response = await self.llm.ainvoke(messages)
            response_text = response.content.strip()
            response_text = self._clean_json_response(response_text)
            result = json.loads(response_text)
            
            logger.info(
                f"报告完整性检查完成 | 完整性: {result.get('is_complete')} | "
                f"评分: {result.get('overall_score')}"
            )
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e} | 原始响应: {response_text[:200]}")
            return {
                "is_complete": False,
                "check_results": [],
                "missing_items": ["系统解析错误，请重试"],
                "overall_score": 0,
                "summary": f"解析失败：大模型返回了非标准JSON格式。错误信息：{str(e)}"
            }
        except Exception as e:
            logger.error(f"报告完整性检查失败: {e}", exc_info=True)
            return {
                "is_complete": False,
                "check_results": [],
                "missing_items": ["检查过程异常"],
                "overall_score": 0,
                "summary": f"检查失败：{str(e)}"
            }

    async def polish_paragraph(
            self,
            original_content: str,
            report_type: str,
            context: dict[str, Any] | None = None
    ) -> str:
        """
        智能润色报告段落
        
        Args:
            original_content: 原始文本内容
            report_type: 报告类型（match_analysis, action_plan, other）
            context: 上下文信息（可选）
            
        Returns:
            润色后的文本内容
        """
        try:
            logger.info(f"开始润色报告段落 | 类型: {report_type}")
            system_prompt = self._get_polish_prompt(report_type)
            user_input = f"# 原始内容\n\n{original_content}\n"
            if context:
                context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
                user_input = f"# 上下文信息\n{context_str}\n\n{user_input}"
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            response = await self.llm.ainvoke(messages)
            polished_content = response.content.strip()
            logger.info(f"报告润色完成 | 原始长度: {len(original_content)} | 润色后长度: {len(polished_content)}")
            return polished_content
        except Exception as e:
            logger.error(f"报告润色失败: {e}", exc_info=True)
            return f"润色失败，返回原始内容：\n\n{original_content}"

    async def _get_user_profile_summary(
            self,
            db_session: AsyncSession,
            user_id: int
    ) -> Optional[str]:
        """
        从数据库查询用户画像并生成摘要文本
        
        Args:
            db_session: 数据库会话
            user_id: 用户ID
            
        Returns:
            用户画像摘要文本（如果查询失败返回None）
        """
        try:
            repo = StuProfileRepository(session=db_session)
            profile = await repo.get_by_stu_id(user_id)
            
            if not profile:
                logger.warning(f"未找到用户画像 | 用户ID: {user_id}")
                return None
            
            # 构建摘要文本
            parts = []
            
            # 基础信息
            if profile.people_form:
                form = profile.people_form
                if form.get("education"):
                    parts.append(f"学历：{form['education']}")
                if form.get("major"):
                    parts.append(f"专业：{form['major']}")
            
            # 技术技能
            if profile.tech_skills and len(profile.tech_skills) > 0:
                skills = "、".join(profile.tech_skills[:5])  # 最多显示5个
                parts.append(f"掌握技能：{skills}")
            
            # 能力评分
            ability_scores = profile.get_ability_scores()
            if any(v > 0 for v in ability_scores.values()):
                scores_str = "、".join([
                    f"{k}：{v}分" 
                    for k, v in ability_scores.items() 
                    if v > 0
                ])
                parts.append(f"能力评分：{scores_str}")
            
            # 实习经历
            if profile.intern_exp:
                # 截取前100字
                exp_summary = profile.intern_exp[:100] + "..." if len(profile.intern_exp) > 100 else profile.intern_exp
                parts.append(f"实习/项目经历：{exp_summary}")
            
            if not parts:
                return None
            
            summary = "\n".join(parts)
            logger.info(f"成功查询用户画像 | 用户ID: {user_id}")
            return summary
            
        except Exception as e:
            logger.error(f"查询用户画像失败: {e}", exc_info=True)
            return None
    
    @staticmethod
    def _get_polish_prompt(report_type: str) -> str:
        """
        根据报告类型获取对应的润色提示词
        
        Args:
            report_type: 报告类型
            
        Returns:
            系统提示词
        """
        prompt_map = {
            "match_analysis": "report_polish_match",
            "action_plan": "report_polish_action",
            "other": "report_polish_general"
        }
        prompt_key = prompt_map.get(report_type, "report_polish_general")
        try:
            return getattr(prompt_loader, prompt_key)
        except AttributeError:
            logger.warning(f"未找到提示词 {prompt_key}，使用通用润色提示词")
            return prompt_loader.report_polish_general

    @staticmethod
    def _clean_json_response(text: str) -> str:
        """
        清理JSON响应文本
        
        移除markdown代码块标记、多余空白等
        
        Args:
            text: 原始响应文本
            
        Returns:
            清理后的JSON字符串
        """
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
        text = text.strip()
        return text


report_assistant_agent = ReportAssistantAgent()
