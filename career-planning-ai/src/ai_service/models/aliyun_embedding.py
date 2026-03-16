import os
import time
import dashscope
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()

class AliyunEmbedding:
    def __init__(self, api_key: str = None):
        """
        初始化阿里云 Embedding 客户端
        :param api_key: 阿里云 DashScope API Key
        """
        # 优先使用传入的 key，否则从环境变量读取
        self.api_key = api_key or os.getenv("LLM__API_KEY")

        if not self.api_key:
            raise ValueError("未找到 API Key，请传入或在环境变量中设置 LLM__API_KEY")

        dashscope.api_key = self.api_key
        self.model = "text-embedding-v4"  # 阿里云主力模型
        print(f"阿里云 Embedding 初始化完成，使用模型：{self.model}")

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        获取单条文本的向量
        :param text: 输入文本
        :return: 浮点数列表，如 [0.01, -0.23, ...]
        """
        try:
            response = dashscope.TextEmbedding.call(
                model=self.model,
                input=text
            )

            # 检查请求是否成功
            if response.status_code == 200:
                # 提取向量数据
                return response.output['embeddings'][0]['embedding']
            else:
                print(f"API 请求失败：{response.code} - {response.message}")
                return None

        except Exception as e:
            print(f"Embedding 请求异常：{e}")
            return None

    def get_embeddings_batch(self, texts: List[str], batch_size: int = 10,
                             delay: float = 0.2) -> List[Optional[List[float]]]:
        """
        批量获取向量
        :param texts: 文本列表
        :param batch_size: 每批请求的文本数量（阿里云限制单次最多 25 条）
        :param delay: 批次间延时（秒），避免触发限流
        :return: 向量列表
        """
        all_embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1

            try:
                response = dashscope.TextEmbedding.call(
                    model=self.model,
                    input=batch
                )

                if response.status_code == 200:
                    # 按顺序提取向量
                    batch_embeddings = [
                        item['embedding'] for item in response.output['embeddings']
                    ]
                    all_embeddings.extend(batch_embeddings)
                    print(f"批次 {batch_num}/{total_batches} 完成，已处理 {i + len(batch)}/{len(texts)} 条")
                else:
                    print(f"批次 {batch_num} 失败：{response.code} - {response.message}")
                    # 失败时填充 None
                    all_embeddings.extend([None] * len(batch))

            except Exception as e:
                print(f"批次 {batch_num} 异常：{e}")
                all_embeddings.extend([None] * len(batch))

            # 延时避免限流
            if i + batch_size < len(texts):
                time.sleep(delay)

        return all_embeddings

    def get_embedding_with_retry(self, text: str, max_retries: int = 3) -> Optional[List[float]]:
        """
        带重试机制的单条向量获取
        :param text: 输入文本
        :param max_retries: 最大重试次数
        :return: 向量
        """
        for attempt in range(max_retries):
            result = self.get_embedding(text)
            if result is not None:
                return result
            print(f"重试 {attempt + 1}/{max_retries}")
            time.sleep(1 * (attempt + 1))  # 指数退避
        return None


# ==========================================
# 使用示例
# ==========================================
if __name__ == "__main__":
    # ⚠️ 建议将 Key 放入环境变量，不要硬编码
    # 方式 1: 直接传入
    # API_KEY = "sk-xxxxxxxxxxxxxxxx"

    API_KEY = os.getenv("LLM__API_KEY")

    if not API_KEY:
        print("❌ 未找到 API Key，请设置环境变量 LLM__API_KEY")
        exit(1)

    embedder = AliyunEmbedding(API_KEY)

    # 1. 单条测试
    print("\n=== 单条测试 ===")
    text = "Java 后端开发工程师，熟悉 Spring Boot 和 MySQL"
    vector = embedder.get_embedding(text)

    if vector:
        print(f"✅ 向量维度：{len(vector)}")  # 应为 1024
        print(f"✅ 向量前 5 位：{vector[:1024]}")
    else:
        print("❌ 向量获取失败")

    # 2. 批量测试
    print("\n=== 批量测试 ===")
    texts = [
        "Python 数据分析工程师",
        "前端 Vue 开发工程师",
        "算法工程师/机器学习",
        "Java 后端开发",
        "产品经理",
        "UI/UX 设计师",
        "DevOps 工程师",
        "测试工程师",
        "数据分析师",
        "运维工程师"
    ]
    vectors = embedder.get_embeddings_batch(texts, batch_size=5, delay=0.3)

    success_count = len([v for v in vectors if v])
    print(f"\n✅ 成功获取 {success_count}/{len(texts)} 条向量")

    # 3. 带重试测试
    print("\n=== 重试机制测试 ===")
    vector_retry = embedder.get_embedding_with_retry("测试重试功能")
    if vector_retry:
        print(f"✅ 重试成功，维度：{len(vector_retry)}")