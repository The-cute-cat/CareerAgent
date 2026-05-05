#!/usr/bin/env python3
"""
ChromaDB 种子数据自动导入脚本
================================
由 Docker 编排时 ai-service 的 entrypoint 调用，
在检测到 Chroma Collection 为空时自动导入种子数据。

环境变量:
    CHROMA_SAVE_PATH — Chroma 持久化目录 (默认: /app/data/chroma)
    SEED_DATA_DIR   — 种子数据目录 (默认: /app/data/init)
"""

import os
import sys
import json
import logging

import chromadb
from langchain_community.embeddings import DashScopeEmbeddings

from config import settings

os.environ["CHROMA_ONNX_MODEL"] = ""
os.environ["CHROMA_TELEMETRY"] = "false"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

CHROMA_SAVE_PATH = settings.chroma_config.save_path
SEED_DATA_DIR = os.getenv("SEED_DATA_DIR", settings.path_config.data + "/init") + "/chroma"

# 各 Collection 名称与种子文件映射
_SEED_MAP = [
    ("books", "books_seed.json"),
    ("open_source_projects", "open_source_projects_seed.json"),
    ("videos", "videos_seed.json"),
    ("internships", "internships_seed.json"),
]


def get_seed_files():
    """返回可用的种子数据文件列表"""
    seeds = []
    for col_name, filename in _SEED_MAP:
        seed_file = os.path.join(SEED_DATA_DIR, filename)
        if os.path.exists(seed_file):
            seeds.append((col_name, seed_file))
        else:
            log.warning(f"种⼦文件不存在，跳过: {filename}")
    return seeds


def import_seed_data(client, collection_name, seed_file, embedding_function):
    """向指定 Collection 导入种子数据"""
    try:
        with open(seed_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as e:
        log.warning(
            f"  [SKIP] 种子文件无效或为空: {os.path.basename(seed_file)} ({e})"
        )
        return 0

    if not isinstance(payload, dict):
        log.warning(f"  [SKIP] 种子文件格式不正确: {os.path.basename(seed_file)}")
        return 0

    data = payload.get("data", [])

    if not data:
        log.info(f"  [SKIP] 种子数据为空: {os.path.basename(seed_file)}")
        return 0

    # 获取或创建 Collection（指定嵌入函数）
    try:
        collection = client.get_collection(collection_name)
        log.debug(f"  ✓ Collection '{collection_name}' 已存在")
    except Exception as e:
        log.info(f" ERROR:{e};📝 创建 Collection '{collection_name}'...")
        try:
            # noinspection SpellCheckingInspection
            collection = client.create_collection(
                name=collection_name,
                embedding_function=embedding_function,
                metadata={"hnsw:space": "cosine"}  # 明确指定距离度量方式
            )
            log.info(f"  ✓ Collection '{collection_name}' 创建成功")
        except Exception as create_error:
            log.error(f"  ✗ Collection '{collection_name}' 创建失败: {create_error}")
            raise

    # 提取文档内容、元数据和 ID
    documents = [item.get("page_content", "") for item in data]
    # noinspection SpellCheckingInspection
    metadatas = [item.get("metadata", {}) for item in data]
    ids = [item.get("id", str(i)) for i, item in enumerate(data)]

    log.info(f"  📊 准备导入 {len(documents)} 条记录到 '{collection_name}'...")
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )
    log.info(f"  ✅ 导入 {len(data)} 条 → {collection_name}")
    return len(data)


def import_all_seeds_with_embedding(client, embedding_function):
    """导入所有可用的种子数据（使用嵌入函数）"""
    seeds = get_seed_files()
    total = 0
    seed_count = len(seeds)
    for index, (col_name, seed_file) in enumerate(seeds, start=1):
        log.info(f"⏳ 正在导入种子数据 ({index}/{seed_count}) → {col_name}")
        count = import_seed_data(client, col_name, seed_file, embedding_function)
        total += count
    log.info(f"📊 当前导入进度: 共 {seed_count} 个 Collection，已导入 {total} 条记录")
    return total


class DashScopeEmbeddingFunction:
    """ChromaDB 兼容的 DashScope 嵌入函数"""

    def __init__(self, model: str, api_key: str):
        self.embedding_function = DashScopeEmbeddings(
            model=model,
            dashscope_api_key=api_key,
        )
        self._call_count = 0
        log.info(f"🚀 DashScope Embedding 初始化完成 | 模型: {model}")

    def __call__(self, _input):
        """ChromaDB 嵌入函数接口"""
        if isinstance(_input, dict) and "documents" in _input:
            _input = _input["documents"]
        if isinstance(_input, str):
            _input = [_input]

        self._call_count += 1
        if self._call_count % 10 == 0:
            log.info(f"  📡 DashScope API 调用次数: {self._call_count}")

        return self.embedding_function.embed_documents(_input)


def do_import():
    """检测并执行种子数据导入（幂等）"""

    os.makedirs(CHROMA_SAVE_PATH, exist_ok=True)

    # 创建 DashScope 嵌入函数
    dashscope_ef = DashScopeEmbeddingFunction(
        model=settings.chroma_config.model_name,
        api_key=settings.chroma_config.api_key.get_secret_value(),
    )

    client = chromadb.PersistentClient(path=CHROMA_SAVE_PATH)
    log.info(f"📂 ChromaDB 持久化路径: {CHROMA_SAVE_PATH}")

    # 检查是否找到种子文件
    seeds = get_seed_files()
    if not seeds:
        log.info("📭 未找到种子数据文件，跳过导入")
        return

    # 幂等检查：每个 Collection 已有数据则跳过
    all_empty = True
    for col_name, _ in seeds:
        try:
            collection = client.get_collection(col_name)
            count = collection.count()
            if count > 0:
                log.info(f"💾 Collection '{col_name}' 已有 {count} 条数据，跳过")
                all_empty = False
            else:
                log.info(f"📂 Collection '{col_name}' 为空，准备导入")
        except Exception as e:
            log.info(f"📂 Collection '{col_name}' 不存在，将创建并导入,{e}")

    if not all_empty:
        log.info("⏭️ 所有目标 Collection 均已有数据，无需导入种子")
        return

    # 执行导入（使用嵌入函数）
    total = import_all_seeds_with_embedding(client, dashscope_ef)
    log.info(
        f"🎉 种子数据导入完成！共导入 {total} 条记录 → {len(seeds)} 个 Collections"
    )


def main():
    log.info("=" * 50)
    log.info("  ChromaDB 种子数据导⼊器")
    log.info("=" * 50)

    try:
        do_import()
    except Exception as e:
        log.error(f"❌ 导入失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
