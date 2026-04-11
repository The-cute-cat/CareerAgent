import os

from sklearn.decomposition import PCA

from ai_service.services.database_manage import get_db_url

# 配置 Hugging Face 镜像源
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import asyncio
from typing import List, Dict

import hdbscan
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from ai_service.models.job_info import JobInfo
from ai_service.utils.logger_handler import log
from ai_service.utils.vector_store.job_original_vector_store import JobOriginalVectorStore

try:
    from sklearn.metrics import silhouette_score
except Exception:
    silhouette_score = None


# 模型：BAAI/bge-base-zh-v1.5 或 BAAI/bge-small-zh-v1.5 或 BAAI/bge-tiny-zh-v1.5
async def cluster_standard_jobs_with_hdbscan(
    session: AsyncSession,
    min_cluster_size: int = 8,# 1. 形成簇的最小样本数
    batch_size: int = 64,
    embedding_model: str = "BAAI/bge-base-zh-v1.5",
    hdbscan_min_samples: int = 3,    # 2. 核心点的最小邻居数 (密度敏感度)
    desc_max_len: int = 10000,
    collection_name: str = "job_original_embeddings",
) -> Dict[int, List[JobInfo]]:
    """
    基于岗位标题 + 精简描述的 HDBSCAN 聚类版本。

    现在的流程改为：
    1. 由 JobOriginalVectorStore 统一负责文本构建、向量化、Milvus 同步
    2. HDBSCAN 只负责读取向量并聚类

    新增数量判断规则：
    - 当向量库数量 == 数据库岗位数量：不进行向量化
    - 当数据库岗位数量 > 向量库数量：按 id 从后往前取多出来的岗位补做向量化
    - 当数据库岗位数量 < 向量库数量：直接报错

    Args:
        session: 数据库异步会话
        min_cluster_size: 最小簇规模
        batch_size: Embedding 批大小
        embedding_model: 语义向量模型
        hdbscan_min_samples: HDBSCAN min_samples
        desc_max_len: 描述最大截断长度
        collection_name: 原始岗位向量集合名称

    Returns:
        Dict[int, List[JobInfo]]: 聚类结果，key 为簇标签，-1 为噪声点
    """
    store = JobOriginalVectorStore(
        collection_name=collection_name,
        embedding_model=embedding_model,
    )

    log.info("开始从 JobOriginalVectorStore 获取聚类所需向量...")
    valid_jobs, embeddings, sync_stats = await store.get_jobs_and_embeddings_for_hdbscan(
        session=session,
        filters=None,
        batch_size=batch_size,
        desc_max_len=desc_max_len,
    )

    # log.info(f"向量同步结果：{sync_stats}")

    total = len(valid_jobs)
    if total == 0:
        log.warning("没有可用于聚类的岗位数据。")
        return {}

    if embeddings.shape[0] != total:
        raise ValueError(
            f"岗位数量({total}) 与向量数量({embeddings.shape[0]}) 不一致，无法执行 HDBSCAN 聚类。"
        )

    if total < 2:
        log.warning("可聚类岗位数量不足 2 条，跳过 HDBSCAN。")
        return {-1: valid_jobs}

    log.info(f"开始 HDBSCAN 聚类，样本数：{total}，向量形状：{embeddings.shape}")
    # PCA 降维
    if embeddings.shape[1] > 128:
        embeddings = PCA(n_components=128).fit_transform(embeddings)
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,  # 1. 形成簇的最小样本数
        min_samples=hdbscan_min_samples,  # 2. 核心点的最小邻居数 (密度敏感度)
        metric="euclidean",  # 3. 距离度量方式 # 归一化向量后使用 euclidean 更稳
        cluster_selection_method="eom",  # 4. 簇选择方法
        cluster_selection_epsilon=0.0,  # 5. 簇选择的最大距离阈值
        approx_min_span_tree=True,  # 6. 最小生成树近似优化
        prediction_data=False,  # 7. 预测数据生成
    )

    cluster_labels = clusterer.fit_predict(embeddings)

    clustered_result: Dict[int, List[JobInfo]] = {}
    for job, label in zip(valid_jobs, cluster_labels):
        label = int(label)
        clustered_result.setdefault(label, []).append(job)

    num_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
    noise_count = len(clustered_result.get(-1, []))
    noise_ratio = noise_count / total if total else 0.0

    log.info("=" * 50)
    log.info("📊 聚类完成！")
    log.info(f"总样本数：{total}")
    log.info(f"标准岗位类别数：{num_clusters}")
    log.info(f"噪声点数量：{noise_count} ({noise_ratio:.2%})")

    if silhouette_score and num_clusters > 1:
        try:
            mask = cluster_labels != -1
            masked_embeddings = embeddings[mask]
            masked_labels = cluster_labels[mask]

        except Exception as e:
            log.warning(f"计算 Silhouette 失败：{e}")
    elif not silhouette_score:
        log.info("Silhouette：未安装 scikit-learn，跳过计算")

    log.info("=" * 50)
    return clustered_result


async def main():
    engine = create_async_engine(get_db_url(), echo=False)
    async_session_local = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    try:
        async with async_session_local() as session:
            clustered_result = await cluster_standard_jobs_with_hdbscan(
                session=session
            )
        return clustered_result
    finally:
        await engine.dispose()


if __name__ == "__main__":
    clustered_result = asyncio.run(main())
    for cluster_id, jobs in sorted(clustered_result.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"cluster={cluster_id}, size={len(jobs)}")

    for cluster_id, jobs in sorted(clustered_result.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\ncluster={cluster_id}, size={len(jobs)}")
        for job in jobs[:10]:
            print(job.id, job.job_title)
