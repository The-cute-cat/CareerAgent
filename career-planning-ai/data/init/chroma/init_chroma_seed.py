#!/usr/bin/env python3
"""
ChromaDB 种子数据自动导入脚本
================================
由 Docker 编排时 ai-service 的 entrypoint 调用，
在检测到 Chroma Collection 为空时自动导入种子数据。

环境变量:
    CHROMA_SAVE_PATH — Chroma 持久化目录 (默认: /app/data/chroma)
    SEED_DATA_DIR   — 种子数据目录 (默认: /app/data/init/chroma)
"""

import os
import sys
import json
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

CHROMA_SAVE_PATH = os.getenv("PATH_CONFIG__DATA", "/app/data") + "/chroma"
SEED_DATA_DIR = os.getenv("SEED_DATA_DIR", "/app/data/init") + "/chroma"

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


def import_seed_data(client, collection_name, seed_file):
    """向指定 Collection 导入种子数据"""
    with open(seed_file, "r", encoding="utf-8") as f:
        payload = json.load(f)

    data = payload.get("data", [])

    if not data:
        log.info(f"  [SKIP] 种子数据为空: {os.path.basename(seed_file)}")
        return 0

    # 获取或创建 Collection
    try:
        collection = client.get_collection(collection_name)
    except Exception:
        collection = client.create_collection(collection_name)

    # 提取文档内容、元数据和 ID
    documents = [item.get("page_content", "") for item in data]
    metadatas = [item.get("metadata", {}) for item in data]
    ids = [item.get("id", str(i)) for i, item in enumerate(data)]

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )
    log.info(f"  [OK] 导入 {len(data)} 条 → {collection_name}")
    return len(data)


def import_all_seeds(client):
    """导入所有可用的种子数据"""
    total = 0
    for col_name, seed_file in get_seed_files():
        count = import_seed_data(client, col_name, seed_file)
        total += count
    return total


def do_import():
    """检测并执行种子数据导入（幂等）"""
    import chromadb

    os.makedirs(CHROMA_SAVE_PATH, exist_ok=True)
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
        except Exception:
            log.info(f"📂 Collection '{col_name}' 不存在，将创建并导入")

    if not all_empty:
        log.info("⏭️ 所有目标 Collection 均已有数据，无需导入种子")
        return

    # 执行导入
    total = import_all_seeds(client)
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
