import time

from langchain_core.prompt_values import PromptValue
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from ai_service.agents import log
from config import settings

__all__ = ["common_agent", "CommonAgent"]


class CommonAgent:
    def __init__(self, llm: ChatOpenAI | None = None):
        self.llm: ChatOpenAI = llm if llm else self.get_llm()

    @staticmethod
    def get_llm(
            api_key: SecretStr = settings.llm.api_key.get_secret_value(),
            model: str = settings.llm.model_name,
            base_url: str = settings.llm.base_url,
            timeout: float = settings.llm.timeout,
            max_retries: int = settings.llm.max_retries,
            temperature: float = settings.llm.extra["temperature"]
    ):
        return ChatOpenAI(api_key=api_key, model=model, base_url=base_url, timeout=timeout, max_retries=max_retries,
                          temperature=temperature)

    async def get_answer(self, prompt: str | PromptValue) -> str | list[str | dict]:
        start_time = time.time()
        log.debug(f"prompt:{prompt.replace("\n", "\\n") if type(prompt) is str else prompt.to_string().replace("\n", "\\n")}")
        response = await self.llm.ainvoke(prompt)
        end_time = time.time()
        log.info(f"耗时: {end_time - start_time}秒；response_metadata: {response.response_metadata}")
        result = response.content
        log.debug(f"result:{result.replace("\n", "\\n") if type(result) is str else result}")
        return result


common_agent = CommonAgent()
