import asyncio
import json
from typing import List, Dict, Any, Optional

import dashscope
from pydantic import BaseModel, Field

from ai_service.models.struct_txt import StudentProfile
from ai_service.services import log
from config import settings


# ==========================================
# 1. 定义 Agent 输出的结构化数据模型
# ==========================================
class GapItem(BaseModel):
    dimension: str = Field(description="维度名称，如 '核心专业技能', '工具与平台能力' 等")
    required: str = Field(description="岗位原始要求")
    current: str = Field(description="学生当前掌握情况")
    gap_analysis: str = Field(description="差距分析，需具体到技术点，如 '缺乏 Milvus 标量过滤经验'")


class DeepAnalysisResult(BaseModel):
    can_apply: bool = Field(description="是否满足核心硬性要求及关键技能。若缺失核心项直接为 false")
    score: int = Field(description="综合匹配度打分 0-100")
    missing_key_skills: List[str] = Field(description="缺失的关键技能或硬性条件列表，若满足则为空列表")
    gap_matrix: List[GapItem] = Field(description="详细的能力差距矩阵，仅列出有差距或需要提升的项")
    actionable_advice: str = Field(description="给学生的一句话下一步行动建议")


# ==========================================
# 2. 核心分析 Agent 类
# ==========================================
class CareerAnalystAgent:
    def __init__(self, api_key: str = settings.llm.api_key.get_secret_value(), model: str = settings.llm.model_name):
        """
        初始化职业分析 Agent
        推荐使用 qwen-max 以保证复杂的 JSON 结构化输出和逻辑判断能力
        """
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("未找到 API Key，请设置环境变量 LLM__API_KEY")

        dashscope.api_key = self.api_key
        self.model = model
        log.info(f"✅ Career Analyst Agent 初始化完成，使用模型：{self.model}")

    def _clean_json_response(self, text: str) -> str:
        """清理 LLM 返回的 Markdown 格式，提取纯 JSON 字符串"""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def _call_llm_sync(self, prompt: str) -> Dict[str, Any]:
        """同步调用 LLM 的底层方法"""
        try:
            # 强制要求模型输出 JSON 格式
            response = dashscope.Generation.call(
                model=self.model,
                prompt=prompt,
                result_format='message'
            )

            if response.status_code == 200:
                content = response.output.choices[0].message.content
                clean_json = self._clean_json_response(content)
                return json.loads(clean_json)
            else:
                log.error(f"⚠️ API 请求失败：{response.code} - {response.message}")
                return self._fallback_result()

        except json.JSONDecodeError:
            log.error("❌ LLM 返回的 JSON 格式解析失败")
            return self._fallback_result()
        except Exception as e:
            log.error(f"❌ LLM 请求异常：{e}")
            return self._fallback_result()

    async def _analyze_single_job_async(self, student_info: str, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        异步分析单个岗位
        """
        job_info = json.dumps(job.get("raw_data", {}), ensure_ascii=False)
        job_id = job.get("job_id", "Unknown")

        prompt = f"""
        你是一位资深的 IT 行业职业分析师。请对以下【求职者画像】和【岗位要求】进行深度 Gap 分析。

        【评审规则】
        1. 核心拦截 (can_apply)：仔细对比岗位核心要求（如学历、工作经验、必备技术栈）。如果求职者存在无法弥补的硬伤（如要求3年经验但他是应届生，或要求精通Java但他只会Python），必须将 `can_apply` 设为 false。
        2. 差距矩阵 (gap_matrix)：对比基础要求、职业技能、职业素养、发展潜力。列出求职者距离该岗位的具体差距。
        3. 透明度：描述要具体。例如不要只说“技术不足”，要说“掌握Vue3，但缺乏该岗位要求的React经验”。

        【求职者画像】
        {student_info}

        【岗位要求】
        {job_info}

        请严格按照以下 JSON 格式输出结果，不要包含任何其他文字或 Markdown 标记：
        {{
            "can_apply": true或false,
            "score": 0到100的整数,
            "missing_key_skills": ["缺失项1", "缺失项2"],
            "gap_matrix": [
                {{
                    "dimension": "技能维度",
                    "required": "岗位要求什么",
                    "current": "求职者目前如何",
                    "gap_analysis": "具体差距分析"
                    “adaptability”：“对技能的评价（只有低/中/高）”
                }}
            ],
            "actionable_advice": "一句话建议"
            “all_analysis”:"总的差距分析"
        }}
        """

        # 使用 asyncio.to_thread 将同步的 API 调用放入线程池，实现非阻塞并发
        analysis_dict = await asyncio.to_thread(self._call_llm_sync, prompt)

        # 将分析结果回填到岗位字典中
        job['deep_analysis'] = analysis_dict
        return job

    def _fallback_result(self) -> Dict[str, Any]:
        """当 API 失败时的保底返回结果"""
        return {
            "can_apply": False,
            "score": 0,
            "missing_key_skills": ["分析接口请求失败"],
            "gap_matrix": [],
            "actionable_advice": "系统繁忙，请稍后重试"
        }

    async def batch_analyze_async(
            self,
            student_profile: StudentProfile,
            retrieved_jobs: List[Dict[str, Any]],
            top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        并发执行批量分析并进行最终排序 (主入口)
        """
        if not retrieved_jobs:
            return []

        student_info = student_profile.model_dump_json(by_alias=True)

        # 1. 创建并发任务列表
        tasks = [
            self._analyze_single_job_async(student_info, job)
            for job in retrieved_jobs
        ]

        # 2. 等待所有任务并发完成 (这里将 10 个请求的时间压缩到 1 个请求的时间)
        log.info(f"🚀 启动并发分析，共 {len(tasks)} 个岗位，请稍候...")
        analyzed_jobs = await asyncio.gather(*tasks)

        # 3. 拦截与重排逻辑 (Rerank)
        # 排序规则：can_apply 为 True 的排在前面，同状态下按 score 降序，最后按原向量召回 score 降序
        analyzed_jobs.sort(
            key=lambda x: (
                x.get('deep_analysis', {}).get('can_apply', False),
                x.get('deep_analysis', {}).get('score', 0),
                x.get('score', 0)
            ),
            reverse=True
        )

        # 4. 截取最终需要展示的数量
        return analyzed_jobs[:top_k]

# ==========================================
# 1. 定义 Agent 输出的结构化数据模型
# ==========================================
class GapItem(BaseModel):
    dimension: str = Field(description="维度名称，如 '核心专业技能', '工具与平台能力' 等")
    required: str = Field(description="岗位原始要求")
    current: str = Field(description="学生当前掌握情况")
    gap_analysis: str = Field(description="差距分析，需具体到技术点，如 '缺乏 Milvus 标量过滤经验'")


class DeepAnalysisResult(BaseModel):
    can_apply: bool = Field(description="是否满足核心硬性要求及关键技能。若缺失核心项直接为 false")
    score: int = Field(description="综合匹配度打分 0-100")
    missing_key_skills: List[str] = Field(description="缺失的关键技能或硬性条件列表，若满足则为空列表")
    gap_matrix: List[GapItem] = Field(description="详细的能力差距矩阵，仅列出有差距或需要提升的项")
    actionable_advice: str = Field(description="给学生的一句话下一步行动建议")











# 如果发现运行是model限流的话，就改career_analyst_agent.py这个文件
#
# # ==========================================
# # 2. 核心分析 Agent 类
# # ==========================================
# class CareerAnalystAgent:
#     def __init__(
#         self,
#         api_key: str = settings.llm.api_key.get_secret_value(),
#         model: str = settings.llm.model_name,
#         default_max_concurrency: int = 5,
#     ):
#         """
#         初始化职业分析 Agent
#         推荐使用 qwen-max 以保证复杂的 JSON 结构化输出和逻辑判断能力
#
#         Args:
#             api_key: DashScope API Key
#             model: 使用的大模型名称
#             default_max_concurrency: 默认并发上限，避免一次性放开过多请求导致限流
#         """
#         self.api_key = api_key
#         if not self.api_key:
#             raise ValueError("未找到 API Key，请设置环境变量 LLM__API_KEY")
#
#         dashscope.api_key = self.api_key
#         self.model = model
#         self.default_max_concurrency = max(1, int(default_max_concurrency))
#         log.info(
#             f"✅ Career Analyst Agent 初始化完成，使用模型：{self.model}，默认并发上限：{self.default_max_concurrency}"
#         )
#
#     def _clean_json_response(self, text: str) -> str:
#         """清理 LLM 返回的 Markdown 格式，提取纯 JSON 字符串"""
#         text = text.strip()
#         if text.startswith("```json"):
#             text = text[7:]
#         elif text.startswith("```"):
#             text = text[3:]
#         if text.endswith("```"):
#             text = text[:-3]
#         return text.strip()
#
#     def _call_llm_sync(self, prompt: str) -> Dict[str, Any]:
#         """同步调用 LLM 的底层方法"""
#         try:
#             response = dashscope.Generation.call(
#                 model=self.model,
#                 prompt=prompt,
#                 result_format='message'
#             )
#
#             if response.status_code == 200:
#                 content = response.output.choices[0].message.content
#                 clean_json = self._clean_json_response(content)
#                 return json.loads(clean_json)
#             else:
#                 log.error(f"⚠️ API 请求失败：{response.code} - {response.message}")
#                 return self._fallback_result()
#
#         except json.JSONDecodeError:
#             log.error("❌ LLM 返回的 JSON 格式解析失败")
#             return self._fallback_result()
#         except Exception as e:
#             log.error(f"❌ LLM 请求异常：{e}")
#             return self._fallback_result()
#
#     async def _analyze_single_job_async(self, student_info: str, job: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         异步分析单个岗位。
#         内部仍复用同步 SDK，通过 asyncio.to_thread 包装为非阻塞调用。
#         """
#         job_info = json.dumps(job.get("raw_data", {}), ensure_ascii=False)
#         job_id = job.get("job_id", "Unknown")
#
#         prompt = f"""
#         你是一位资深的 IT 行业职业分析师。请对以下【求职者画像】和【岗位要求】进行深度 Gap 分析。
#
#         【评审规则】
#         1. 核心拦截 (can_apply)：仔细对比岗位核心要求（如学历、工作经验、必备技术栈）。如果求职者存在无法弥补的硬伤（如要求3年经验但他是应届生，或要求精通Java但他只会Python），必须将 `can_apply` 设为 false。
#         2. 差距矩阵 (gap_matrix)：对比基础要求、职业技能、职业素养、发展潜力。列出求职者距离该岗位的具体差距。
#         3. 透明度：描述要具体。例如不要只说“技术不足”，要说“掌握Vue3，但缺乏该岗位要求的React经验”。
#
#         【求职者画像】
#         {student_info}
#
#         【岗位要求】
#         {job_info}
#
#         请严格按照以下 JSON 格式输出结果，不要包含任何其他文字或 Markdown 标记：
#         {{
#             "can_apply": true或false,
#             "score": 0到100的整数,
#             "missing_key_skills": ["缺失项1", "缺失项2"],
#             "gap_matrix": [
#                 {{
#                     "dimension": "技能维度",
#                     "required": "岗位要求什么",
#                     "current": "求职者目前如何",
#                     "gap_analysis": "具体差距分析",
#                     "adaptability": "对技能的评价（只有低/中/高）"
#                 }}
#             ],
#             "actionable_advice": "一句话建议",
#             "all_analysis": "总的差距分析"
#         }}
#         """
#
#         log.info(f"🔍 开始分析岗位：job_id={job_id}")
#         analysis_dict = await asyncio.to_thread(self._call_llm_sync, prompt)
#         job['deep_analysis'] = analysis_dict
#         return job
#
#     async def _bounded_analyze_single_job_async(
#         self,
#         student_info: str,
#         job: Dict[str, Any],
#         semaphore: asyncio.Semaphore,
#     ) -> Dict[str, Any]:
#         """
#         带并发限制的单岗位分析。
#         """
#         job_id = job.get("job_id", "Unknown")
#         async with semaphore:
#             log.info(f"🚦 获取并发槽位，开始分析 job_id={job_id}")
#             try:
#                 return await self._analyze_single_job_async(student_info, job)
#             finally:
#                 log.info(f"✅ 完成分析并释放槽位 job_id={job_id}")
#
#     def _fallback_result(self) -> Dict[str, Any]:
#         """当 API 失败时的保底返回结果"""
#         return {
#             "can_apply": False,
#             "score": 0,
#             "missing_key_skills": ["分析接口请求失败"],
#             "gap_matrix": [],
#             "actionable_advice": "系统繁忙，请稍后重试"
#         }
#
#     async def batch_analyze_async(
#         self,
#         student_profile: StudentProfile,
#         retrieved_jobs: List[Dict[str, Any]],
#         top_k: int = 5,
#         max_concurrency: Optional[int] = None,
#     ) -> List[Dict[str, Any]]:
#         """
#         受控并发执行批量分析并进行最终排序。
#
#         Args:
#             student_profile: 学生画像
#             retrieved_jobs: 向量召回得到的岗位列表
#             top_k: 最终返回前 top_k 个岗位
#             max_concurrency: 最大并发数；不传则使用实例默认值
#         """
#         if not retrieved_jobs:
#             return []
#
#         student_info = student_profile.model_dump_json(by_alias=True)
#         max_concurrency = max(1, int(max_concurrency or self.default_max_concurrency))
#         semaphore = asyncio.Semaphore(max_concurrency)
#
#         tasks = [
#             self._bounded_analyze_single_job_async(student_info, job, semaphore)
#             for job in retrieved_jobs
#         ]
#
#         log.info(
#             f"🚀 启动受控并发分析，共 {len(tasks)} 个岗位，最大并发数={max_concurrency}"
#         )
#         analyzed_jobs = await asyncio.gather(*tasks)
#
#         analyzed_jobs.sort(
#             key=lambda x: (
#                 x.get('deep_analysis', {}).get('can_apply', False),
#                 x.get('deep_analysis', {}).get('score', 0),
#                 x.get('score', 0)
#             ),
#             reverse=True
#         )
#
#         return analyzed_jobs[:top_k]