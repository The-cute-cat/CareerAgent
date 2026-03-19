import json
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from ai_service.models.struct_txt import StudentProfile
import os
import dashscope
from typing import List, Dict, Any
load_dotenv()

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
    def __init__(self, api_key: str = os.getenv("LLM__API_KEY"), model: str = "qwen-max"):
        """
        初始化职业分析 Agent
        推荐使用 qwen-max 以保证复杂的 JSON 结构化输出和逻辑判断能力
        """
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("未找到 API Key，请设置环境变量 LLM__API_KEY")

        dashscope.api_key = self.api_key
        self.model = model
        print(f"✅ Career Analyst Agent 初始化完成，使用模型：{self.model}")

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
                print(f"⚠️ API 请求失败：{response.code} - {response.message}")
                return self._fallback_result()

        except json.JSONDecodeError:
            print("❌ LLM 返回的 JSON 格式解析失败")
            return self._fallback_result()
        except Exception as e:
            print(f"❌ LLM 请求异常：{e}")
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
                }}
            ],
            "actionable_advice": "一句话建议"
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
        print(f"🚀 启动并发分析，共 {len(tasks)} 个岗位，请稍候...")
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








    # 同步RAGc重排在异步里面被包含了，不需要了。
    # def rerank_jobs(
    #         self,
    #         student_profile: Any,  # 假设是 StudentProfile 对象
    #         retrieved_jobs: List[Dict[str, Any]],
    #         top_k: int = 10,
    #         model: str = "qwen-turbo"
    # ) -> List[Dict[str, Any]]:
    #     """
    #     对 Milvus 召回的岗位列表进行 LLM 深度重排序
    #     """
    #     if not retrieved_jobs:
    #         return []
    #
    #     # 1. 预处理学生信息 (如果是 Pydantic 模型则转为 dict)
    #     student_info = student_profile.dict() if hasattr(student_profile, 'dict') else str(student_profile)
    #
    #     for job in retrieved_jobs:
    #         # 提取岗位核心文本用于打分，若无 raw_data 则取整个 job 字典
    #         job_context = job.get("raw_data", job)
    #
    #         prompt = f"""
    #         你是一位资深的 HR 算法评审员。请评估【求职者】与【岗位】的匹配度。
    #
    #         【求职者画像】:
    #         {student_info}
    #
    #         【岗位要求】:
    #         {job_context}
    #
    #         请直接给出一个 0 到 100 之间的整数分数代表最终匹配度。
    #         注意：不要输出任何分析过程，只输出一个数字。
    #         """
    #
    #         try:
    #             response = dashscope.Generation.call(
    #                 model=model,
    #                 prompt=prompt
    #             )
    #
    #             if response.status_code == 200:
    #                 result_text = response.output.text.strip()
    #                 # 鲁棒性提取数字
    #                 match = re.search(r'\d+', result_text)
    #                 score = float(match.group()) if match else 0.0
    #             else:
    #                 score = 0.0
    #         except Exception as e:
    #             print(f"❌ Rerank 异常: {e}")
    #             score = 0.0
    #
    #         # 直接在原始字典上注入分数，不破坏原始结构
    #         job['rerank_score'] = score
    #
    #     # 2. 根据分数降序排序，同时保留原始数据
    #     # 使用 key=lambda 排序不会改变字典内部结构
    #     sorted_jobs = sorted(
    #         retrieved_jobs,
    #         key=lambda x: x.get('rerank_score', 0),
    #         reverse=True
    #     )
    #
    #     # 3. 返回前 top_k 个原始字典列表
    #     return sorted_jobs[:top_k]