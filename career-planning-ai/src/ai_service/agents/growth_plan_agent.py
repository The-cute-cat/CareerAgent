from langchain.agents import create_agent
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from ai_service.agents.middleware import log_before_model, monitor_tool
from ai_service.agents.tools import query_books, query_videos, query_project, query_intern
from ai_service.services.prompt_loader import prompt_loader
from config import settings


class GrowthPlanAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.growth_plan_agent.api_key.get_secret_value(),
            model=settings.growth_plan_agent.model_name,
            base_url=settings.growth_plan_agent.base_url,
            timeout=settings.growth_plan_agent.timeout,
            max_retries=settings.growth_plan_agent.max_retries,
            temperature=settings.growth_plan_agent.extra["temperature"]
        )
        self.agent = create_agent(
            model=self.llm,
            system_prompt=prompt_loader.growth_plan_generation,
            tools=[query_books, query_videos, query_project, query_intern],
            middleware=[log_before_model, monitor_tool]
        )

    async def generate_growth_plan(self, target_position: str, student_profile: str, ability_gap: str | None = None):
        input_message = prompt_loader.small_prompts["growth_plan_user"].format(
            target_position=target_position, student_profile=student_profile,
            ability_gap=ability_gap if ability_gap else "暂无"
        )
        config: RunnableConfig = {
            "recursion_limit": settings.growth_plan_agent.extra["recursion_limit"]
        }
        output = await self.agent.ainvoke(
            {"messages": [HumanMessage(content=input_message)]},
            config=config
        )
        return output

