import asyncio

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ai_service.agents.common_agent import CommonAgent
from ai_service.services.prompt_loader import prompt_loader
from config import settings


class TestQuestionAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.llm.api_key.get_secret_value(),
            model=settings.test_question.model_name,
            base_url=settings.llm.base_url,
            timeout=settings.test_question.timeout,
            max_retries=settings.llm.max_retries,
            temperature=settings.test_question.extra["temperature"]
        )
        self.common_agent = CommonAgent(self.llm)

    async def generate_test_questions(
            self,
            skill: str | None = None,
            tool: str | None = None
    ) -> str | list[str | dict]:
        if not skill and not tool:
            raise ValueError("skill and tool cannot be empty at the same time")
        if skill and tool:
            raise ValueError("skill and tool cannot be used at the same time")
        if tool is None:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "{system_prompt}"),
                ("human", "请根据以下技能生成测试题:\n\n技能: {skill}")
            ])
            prompt_text = prompt.invoke(
                {
                    "system_prompt": prompt_loader.test_question_generation_skill,
                    "skill": skill
                }
            )
            return await self.common_agent.get_answer(prompt_text)
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "{system_prompt}"),
                ("human", "请根据以下工具生成测试题:\n\n工具: {tool}")
            ])
            prompt_text = prompt.invoke(
                {
                    "system_prompt": prompt_loader.test_question_generation_tool,
                    "tool": tool
                }
            )
            return await self.common_agent.get_answer(prompt_text)

    async def check_student_answer(self, questions: str, evaluation_criteria: str, student_answer: str) -> str | list[
        str | dict]:
        if not questions or not evaluation_criteria or not student_answer:
            raise ValueError("questions, evaluation_criteria and student_answer cannot be empty")
        prompt_text = prompt_loader.answer_evaluation.format(questions=questions,
                                                             evaluation_criteria=evaluation_criteria,
                                                             student_answer=student_answer)
        return await self.common_agent.get_answer(prompt_text)

    async def check_test_questions(self, questions: str, skill_or_tool: str):
        if not questions or not skill_or_tool:
            raise ValueError("questions and skill_or_tool cannot be empty")
        prompt_text = prompt_loader.test_question_censorship.format(questions=questions,
                                                                    skill_or_tool=skill_or_tool)
        return await self.common_agent.get_answer(prompt_text)

    async def modify_test_questions(self, questions: str, skill_or_tool: str, review_report: str):
        if not questions or not skill_or_tool or not review_report:
            raise ValueError("questions, skill_or_tool and review_report cannot be empty")
        prompt_text = prompt_loader.test_question_modification.format(questions=questions,
                                                                      skill_or_tool=skill_or_tool,
                                                                      review_report=review_report)
        return await self.common_agent.get_answer(prompt_text)


test_question_agent = TestQuestionAgent()


async def main():
    # result = await test_question_agent.check_test_questions(
    #     "在一个 Web 服务中，发现某个 API 接口响应缓慢。请从 Python 技术角度分析可能的原因，并给出优化建议。",
    #     """评分标准：
    #             1. 提到同步阻塞 I/O 问题（数据库查询、HTTP 请求等）（2分）
    #             2. 提到异步方案（async/await、gevent 等）（2分）
    #             3. 提到缓存策略（Redis 等）（2分）
    #             4. 提到连接池优化（数据库连接复用）（2分）
    #             5. 提到监控与分析工具（日志、性能分析）（2分）""",
    #     "我觉得可能是数据库查询太慢了，可以用 Redis 做缓存。另外代码里有很多地方在循环里查数据库，可以优化一下。还可以用 Python 的 async 功能来处理并发请求。"
    # )
    tools = "Docker"
    skills = "Python"
    result1 = await test_question_agent.generate_test_questions(tool="Docker")
    result = await test_question_agent.check_test_questions(result1, tools)
    result = await test_question_agent.modify_test_questions(result1, tools, result)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
