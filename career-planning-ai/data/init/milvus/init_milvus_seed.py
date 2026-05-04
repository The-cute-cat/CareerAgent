#!/usr/bin/env python3
"""
Milvus 种子数据自动导入脚本
===========================
由 Docker 编排时 ai-service 的 entrypoint 调用，
在检测到 Milvus Collection 为空时自动导入种子数据。

环境变量:
    MILVUS_HOST   — Milvus 主机地址 (默认: localhost)
    MILVUS_PORT   — Milvus 端口 (默认: 19530)
    SEED_DATA_DIR — 种子数据目录 (默认: /app/data/init/milvus)
"""

import os
import sys
import json
import time
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))
SEED_DATA_DIR = os.getenv("SEED_DATA_DIR", "/app/data/init") + "/milvus"

# 最大重试次数与间隔（等待 Milvus 就绪）
MAX_RETRIES = 30
RETRY_INTERVAL = 5


# ==================== 种子数据发现与导入 ====================


def get_seed_files():
    """返回可用的种子数据文件列表"""
    seeds = []
    seed_file = os.path.join(SEED_DATA_DIR, "job_original_embeddings_seed.json")
    if os.path.exists(seed_file):
        seeds.append(("job_original_embeddings", seed_file))

    seed_file = os.path.join(SEED_DATA_DIR, "job_matching_profiles_seed.json")
    if os.path.exists(seed_file):
        seeds.append(("job_matching_profiles", seed_file))

    return seeds


def import_seed_data(client, collection_name, seed_file):
    """向指定 Collection 导入种子数据"""
    with open(seed_file, "r", encoding="utf-8") as f:
        payload = json.load(f)

    data = payload.get("data", [])

    if not data:
        log.info(f"  [SKIP] 种子数据为空: {os.path.basename(seed_file)}")
        return 0

    client.insert(
        collection_name=collection_name,
        data=data,
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


# ==================== Milvus 连接与编排控制 ====================


def wait_for_milvus():
    """等待 Milvus 服务就绪"""
    from pymilvus import utility

    for i in range(1, MAX_RETRIES + 1):
        try:
            if utility.list_connections():
                log.info(f"✅ Milvus ({MILVUS_HOST}:{MILVUS_PORT}) 已就绪")
                return True
        except Exception:
            pass
        log.info(f"⏳ 等待 Milvus 就绪... ({i}/{MAX_RETRIES})")
        time.sleep(RETRY_INTERVAL)

    log.error("❌ Milvus 连接超时")
    return False


def do_import():
    """检测并执行种子数据导入"""
    from pymilvus import connections, utility, Collection

    # 建立连接
    connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
    log.info(f"🔗 已连接 Milvus: {MILVUS_HOST}:{MILVUS_PORT}")

    # 检查是否已有种子数据需要导入
    seeds = get_seed_files()
    if not seeds:
        log.info("📭 未找到种子数据文件，跳过导入")
        connections.disconnect("default")
        return

    # 检查每个 collection 是否已有数据（幂等：已有数据则跳过）
    all_empty = True
    for col_name, _ in seeds:
        if utility.has_collection(col_name):
            col = Collection(col_name)
            col.load()
            count = col.num_entities
            if count and count > 0:
                log.info(f"💾 Collection '{col_name}' 已有 {count} 条数据，跳过")
                all_empty = False
            else:
                log.info(f"📂 Collection '{col_name}' 为空，准备导入")
        else:
            log.info(
                f"📂 Collection '{col_name}' 不存在，"
                "将在代码层 _init_collection 时自动创建后手动重新导入"
            )

    if not all_empty:
        log.info("⏭️ 所有目标 Collection 均已有数据，无需导入种子")
        connections.disconnect("default")
        return

    # 执行导入
    total = import_all_seeds(connections)
    log.info(f"🎉 种子数据导入完成！共导入 {total} 条记录")

    connections.disconnect("default")


def main():
    log.info("=" * 50)
    log.info("  Milvus 种子数据导入器")
    log.info("=" * 50)

    try:
        if not wait_for_milvus():
            sys.exit(1)
        do_import()
    except Exception as e:
        log.error(f"❌ 导入失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
