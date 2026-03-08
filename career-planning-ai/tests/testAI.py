from typing import List, Optional
import dashscope
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_community.chat_models import ChatTongyi
from dashscope import MultiModalConversation
from ai_service.utils.logger_handler import log


# 抽离一个测试类，模拟调用大模型的接口，减少对大模型接口的依赖，方便测试和调试
class TestAI:
    def __init__(self, api_key, base_url, timeout, max_retries, model):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.model = model

    async def run(self, message: List[BaseMessage]) -> str:
        # 自定义默认返回值（替换None/异常场景）
        DEFAULT_RETURN = "未获取到有效回复(API调用失败)"
        try:
            response = ChatTongyi(
                api_key=self.api_key,
                model=self.model,
            )
            result = await response.ainvoke(message)
            content = result.content[0]["text"]
            if isinstance(content, list):
                return str(content)
            return content
        # 细分异常类型，精准定位问题
        except KeyError as e:
            log.error(f"解析content时缺少关键键值,{e}")
            return DEFAULT_RETURN
        except IndexError as e:
            log.error(f"content列表索引越界,{e}")
            return DEFAULT_RETURN
        except Exception as e:  # 兜底异常（不建议省略，但需记录详细日志）
            log.error(f"调用ChatTongyi时发生未知错误,{e}", exc_info=True)
            return DEFAULT_RETURN


class TestPrompt:
    def image_prompt(self, image_suffix, image_data_base64):
        # 构造文件头信息,以便API正确识别图片格式
        file_header = f"data:image/{image_suffix};base64,{image_data_base64}"
        # 构造信息提示语,以便API正确理解任务需求
        message = [
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "描述图片,要保留数据和格式.",
                    },
                    {"type": "image", "image": file_header},
                ]
            )
        ]
        return message
