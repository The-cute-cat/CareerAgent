import os
# 配置 Hugging Face 镜像源
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import re
import asyncio
from collections import Counter
from typing import List, Dict
import pathlib

import hdbscan
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from huggingface_hub import snapshot_download  # 使用这个库来下载模型
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from ai_service.repository.connection_session import get_db_url
from ai_service.models.job_info import JobInfo
from ai_service.repository.job_info_repository import JobRepository
from ai_service.utils.logger_handler import log



try:
    from sklearn.metrics import silhouette_score
except Exception:
    silhouette_score = None


def get_model_local_path(model_name: str) -> str:
    """
    获取模型的本地路径，如果不存在则下载

    Args:
        model_name: 模型名称，如 "BAAI/bge-base-zh-v1.5"

    Returns:
        str: 模型的本地路径
    """
    # 检查是否是本地路径
    if pathlib.Path(model_name).exists():
        log.info(f"使用本地模型: {model_name}")
        return model_name

    # 使用 huggingface_hub 下载模型
    cache_dir = pathlib.Path.home() / ".cache" / "huggingface" / "hub"
    log.info(f"开始下载模型: {model_name}")
    log.info(f"镜像源: {os.environ.get('HF_ENDPOINT', '官方源')}")

    try:
        model_path = snapshot_download(
            repo_id=model_name,
            cache_dir=str(cache_dir),
            local_dir_use_symlinks=False,
            resume_download=True
        )
        log.info(f"✅ 模型下载成功: {model_path}")
        return model_path
    except Exception as e:
        log.error(f"❌ 模型下载失败: {e}")
        raise


def clean_text(text: str) -> str:
    """
    轻量文本清洗：
    - 转小写
    - 去掉多余空白
    - 统一常见分隔符
    - 去掉部分括号符号
    """
    if not text:
        return ""

    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[|｜/\\]+", " ", text)
    text = re.sub(r"[（）()\[\]【】]+", " ", text)
    text = re.sub(r"[,:：;；]+", " ", text)
    return text.strip()


def clean_title(title: str) -> str:
    """
    岗位标题轻量清洗：
    这里只做最基础的去噪，避免过度规则化影响召回。
    后续你可以接入更完整的规则清洗版本。
    """
    if not title:
        return ""

    title = clean_text(title)

    # 去掉常见招聘噪声词
    noise_words = [
        "急招", "高薪", "诚聘", "招聘", "热招", "急聘", "直招",
        "可实习", "接受实习", "双休", "五险一金", "五险", "一金",
        "2025届", "2026届", "校招", "社招", "应届", "实习"
    ]
    for word in noise_words:
        title = title.replace(word, " ")

    # 去掉薪资信息
    title = re.sub(r"\d+\s*[-~—到]\s*\d+\s*[kKwW万千]?(\s*/\s*(月|年))?", " ", title)
    title = re.sub(r"\d+[kK]\s*[-~—到]\s*\d+[kK]", " ", title)
    title = re.sub(r"\d+\s*-\s*\d+\s*万", " ", title)

    # 去掉多余空白
    title = re.sub(r"\s+", " ", title).strip()
    return title


def build_text_feature(job: JobInfo, desc_max_len: int = 150) -> str:
    """
    构建用于聚类的文本特征：
    - 标题为主
    - 描述为辅
    - 不使用薪资，减少干扰
    - 标题重复一次，给标题更高权重
    """
    title = clean_title(job.job_title or "")
    desc = clean_text(job.job_desc or "")

    # 描述只取前面一小段，减少公司介绍/福利/套话噪声
    short_desc = desc[:desc_max_len]

    parts = []

    if title:
        parts.append(f"岗位标题 {title}")
        parts.append(f"岗位核心 {title}")  # 重复一次，相当于轻量加权

    if short_desc:
        parts.append(f"岗位描述 {short_desc}")

    return "\n".join(parts).strip()

# 模型：BAAI/bge-base-zh-v1.5 或 BAAI/bge-small-zh-v1.5 或 BAAI/bge-tiny-zh-v1.5
async def cluster_standard_jobs_with_hdbscan(
    session: AsyncSession,
    min_cluster_size: int = 8,
    batch_size: int = 64,
    embedding_model: str = "BAAI/bge-base-zh-v1.5",
    hdbscan_min_samples: int = 3,
    desc_max_len: int = 150,
) -> Dict[int, List[JobInfo]]:
    """
    基于岗位标题 + 精简描述的 HDBSCAN 聚类版本

    优化点：
    1. 去掉薪资特征，减少非岗位语义干扰
    2. 缩短岗位描述，减少招聘话术噪声
    3. HDBSCAN 参数调松，降低过高噪声比例
    4. 去掉 DBCV 计算，减少不必要耗时和 overflow warning
    5. 只保留必要日志和轻量评估

    Args:
        session: 数据库异步会话
        min_cluster_size: 最小簇规模
        batch_size: Embedding 批大小
        embedding_model: 语义向量模型
        hdbscan_min_samples: HDBSCAN min_samples
        desc_max_len: 描述最大截断长度

    Returns:
        Dict[int, List[JobInfo]]: 聚类结果，key 为簇标签，-1 为噪声点
    """
    repo = JobRepository(session)

    # 1. 加载 Embedding 模型
    log.info(f"准备加载 Embedding 模型：{embedding_model}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        log.info("✅ 检测到 GPU，使用 CUDA 加速")
    else:
        log.warning("未检测到 GPU，使用 CPU 推理（较慢）")

    # 获取模型本地路径（如果不存在会自动下载）
    model_path = get_model_local_path(embedding_model)

    # 加载模型（使用本地路径）
    log.info(f"加载模型: {model_path}")
    embedder = SentenceTransformer(model_path, device=device)

    # 2. 获取数据库岗位数据
    log.info("开始从数据库获取全量岗位数据...")
    all_jobs: List[JobInfo] = await repo.get_list_all()

    if not all_jobs:
        log.warning("数据库中没有岗位数据可供聚类。")
        return {}

    # 3. 构建文本特征
    texts_to_embed: List[str] = []
    valid_jobs: List[JobInfo] = []

    for job in all_jobs:
        text_feature = build_text_feature(job, desc_max_len=desc_max_len)
        if not text_feature:
            continue

        texts_to_embed.append(text_feature)
        valid_jobs.append(job)

    total = len(valid_jobs)
    log.info(f"成功构建 {total} 条文本特征")

    if total == 0:
        log.warning("清洗后没有可用于聚类的岗位文本。")
        return {}

    # 4. 向量化
    log.info("开始本地向量化...")
    embeddings = embedder.encode(
        texts_to_embed,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype(np.float32)

    log.info(f"向量形状：{embeddings.shape}")

    # 5. HDBSCAN 聚类
    log.info("开始 HDBSCAN 聚类...")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=hdbscan_min_samples,
        metric="euclidean",  # 归一化向量后使用 euclidean 更稳
        cluster_selection_method="eom",
        cluster_selection_epsilon=0.0,
        approx_min_span_tree=True,
        prediction_data=False
    )

    cluster_labels = clusterer.fit_predict(embeddings)

    # 6. 整理结果
    clustered_result: Dict[int, List[JobInfo]] = {}
    for job, label in zip(valid_jobs, cluster_labels):
        label = int(label)
        if label not in clustered_result:
            clustered_result[label] = []
        clustered_result[label].append(job)

    # 7. 聚类结果摘要
    num_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
    noise_count = len(clustered_result.get(-1, []))
    noise_ratio = noise_count / total if total else 0.0

    log.info("=" * 50)
    log.info("📊 聚类完成！")
    log.info(f"总样本数：{total}")
    log.info(f"标准岗位类别数：{num_clusters}")
    log.info(f"噪声点数量：{noise_count} ({noise_ratio:.2%})")

    cluster_sizes = Counter([int(lbl) for lbl in cluster_labels if lbl != -1])
    if cluster_sizes:
        top_sizes = sorted(cluster_sizes.items(), key=lambda x: x[1], reverse=True)[:10]
        log.info(f"Top 簇规模（前10）：{top_sizes}")

    # 8. 轻量评估：仅保留 silhouette
    if silhouette_score and num_clusters > 1:
        try:
            mask = cluster_labels != -1
            masked_embeddings = embeddings[mask]
            masked_labels = cluster_labels[mask]

            if len(masked_labels) >= 10 and len(set(masked_labels)) > 1:
                sil = silhouette_score(masked_embeddings, masked_labels, metric="euclidean")
                log.info(f"Silhouette（去噪后）：{sil:.4f}")
            else:
                log.info("Silhouette：去噪后样本/簇数不足，跳过计算")
        except Exception as e:
            log.warning(f"计算 Silhouette 失败：{e}")
    elif not silhouette_score:
        log.info("Silhouette：未安装 scikit-learn，跳过计算")

    log.info("=" * 50)

    return clustered_result


async def main():

    engine = create_async_engine(get_db_url(), echo=False)
    AsyncSessionLocal = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession
    )

    try:
        async with AsyncSessionLocal() as session:
            clustered_result = await cluster_standard_jobs_with_hdbscan(
                session=session,
                min_cluster_size=8,
                hdbscan_min_samples=3,
                batch_size=64,
                embedding_model="BAAI/bge-base-zh-v1.5",
                desc_max_len=150
            )
        return clustered_result
    finally:
        await engine.dispose()


if __name__ == "__main__":
    clustered_result = asyncio.run(main())

    # 只打印摘要，避免大量刷屏
    for cluster_id, jobs in sorted(clustered_result.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"cluster={cluster_id}, size={len(jobs)}")

    # 如果你想看每个簇前几个岗位标题，可以打开下面这段：
    for cluster_id, jobs in sorted(clustered_result.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\ncluster={cluster_id}, size={len(jobs)}")
        for job in jobs[:10]:
            print(job.id, job.job_title)