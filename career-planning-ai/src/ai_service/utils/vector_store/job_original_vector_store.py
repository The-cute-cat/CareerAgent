import os
import re
import asyncio
import pathlib
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import torch
from pymilvus import (
    connections,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    utility,
)

from ai_service.services.database_manage import get_db_url

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from sentence_transformers import SentenceTransformer
from huggingface_hub import snapshot_download
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from ai_service.models.job_info import JobInfo

from ai_service.repository.job_info_repository import JobRepository
from ai_service.utils.logger_handler import log
from config import settings


def get_model_local_path(model_name: str) -> str:
    """获取模型的本地路径，如果不存在则自动下载"""

    cache_dir = pathlib.Path.home() / ".cache" / "huggingface" / "hub"
    log.info(f"加载模型: {model_name}")
    log.info(f"缓存目录: {cache_dir}")
    log.info(f"镜像源: {os.environ.get('HF_ENDPOINT', '官方源')}")

    try:
        # snapshot_download 会自动检查缓存，已存在则秒返回，无需重复下载
        model_path = snapshot_download(
            repo_id=model_name,
            cache_dir=str(cache_dir),
            local_dir_use_symlinks=False,  # Windows 建议设为 False，避免权限问题
            resume_download=True,
        )
        log.info(f"✅ 模型就绪: {model_path}")
        return model_path
    except Exception as e:
        log.error(f"❌ 模型加载失败: {e}")
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
    岗位标题轻量清洗。
    逻辑与 HDBSCAN.py 保持一致。
    """
    if not title:
        return ""

    title = clean_text(title)

    noise_words = [
        "急招", "高薪", "诚聘", "招聘", "热招", "急聘", "直招",
        "可实习", "接受实习", "双休", "五险一金", "五险", "一金",
        "2025届", "2026届", "校招", "社招", "应届", "实习",
    ]
    for word in noise_words:
        title = title.replace(word, " ")

    title = re.sub(r"\d+\s*[-~—到]\s*\d+\s*[kKwW万千]?(\s*/\s*(月|年))?", " ", title)
    title = re.sub(r"\d+[kK]\s*[-~—到]\s*\d+[kK]", " ", title)
    title = re.sub(r"\d+\s*-\s*\d+\s*万", " ", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def build_text_feature(job: JobInfo, desc_max_len: int = 10000) -> str:
    """
    构建用于向量化/聚类的文本特征：
    - 标题为主
    - 描述为辅
    - 标题重复一次做轻量加权
    - 不带薪资，减少噪声
    """
    title = clean_title(job.job_title or "")
    desc = clean_text(job.job_desc or "")
    short_desc = desc[:desc_max_len]

    parts: List[str] = []
    if title:
        parts.append(f"岗位标题 {title}")
        parts.append(f"岗位核心 {title}")

    if short_desc:
        parts.append(f"岗位描述 {short_desc}")

    return "\n".join(parts).strip()


class JobOriginalVectorStore:
    """
    原始岗位向量库：
    - 数据源：job_original 表（通过 JobRepository.get_list_all 获取）
    - 向量化：复用 HDBSCAN 的文本构建与 SentenceTransformer 向量化方式
    - Milvus 字段：只保存 job_id + embedding
    - 支持按“数据库数量 vs 向量库数量”进行增量同步
    """

    def __init__(
        self,
        host: str = settings.milvus.local.host,
        port: str = settings.milvus.local.port,
        url: str = settings.milvus.cloud.url,
        token: str = settings.milvus.cloud.token.get_secret_value(),
        collection_name: str = "job_original_embeddings",
        embedding_model: str = "BAAI/bge-base-zh-v1.5",
        index_type: str = "HNSW",
        metric_type: str = "COSINE",
    ):
        self.host = host
        self.port = port
        self.url = url
        self.token = token
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.index_type = index_type
        self.metric_type = metric_type

        self.embedder = self._load_embedder()
        self.dim = self.embedder.get_sentence_embedding_dimension()

        self._connect_milvus()
        self.collection = self._init_collection()

    def _connect_milvus(self) -> None:
        """连接 Milvus / Zilliz。"""
        # 增加 gRPC 接收消息大小限制 (例如 64MB)，防止查询返回数据量过大时报错
        # RESOURCE_EXHAUSTED: grpc: received message larger than max
        conn_args = {
            "grpc_args": [
                ("grpc.max_receive_message_length", 64 * 1024 * 1024),
                ("grpc.max_send_message_length", 64 * 1024 * 1024),
            ]
        }

        if self.url != "<url>" and self.token != "<token>":
            connections.connect("default", uri=self.url, token=self.token, **conn_args)
            log.info("✅ 已连接到 Zilliz 云服务")
        else:
            connections.connect("default", host=self.host, port=self.port, **conn_args)
            log.info(f"✅ 已连接到本地 Milvus: {self.host}:{self.port}")

    def _load_embedder(self) -> SentenceTransformer:
        """加载本地语义模型，向量化方式与 HDBSCAN 保持一致。"""
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cuda":
            log.info("✅ 检测到 GPU，使用 CUDA 加速")
        else:
            log.warning("未检测到 GPU，使用 CPU 推理（较慢）")

        model_path = get_model_local_path(self.embedding_model)
        log.info(f"加载模型: {model_path}")
        return SentenceTransformer(model_path, device=device)

    def _init_collection(self) -> Collection:
        """初始化集合。仅保存 job_id 和 embedding。"""
        if utility.has_collection(self.collection_name):
            collection = Collection(self.collection_name)
            collection.load()
            log.info(f"✅ Collection '{self.collection_name}' 已存在，直接加载")
            return collection

        fields = [
            FieldSchema(name="job_id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim),
        ]

        schema = CollectionSchema(fields, description="原始岗位单向量库")
        collection = Collection(self.collection_name, schema=schema)

        index_params = {
            "metric_type": self.metric_type,
            "index_type": self.index_type,
            "params": {"M": 8, "efConstruction": 64},
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        collection.load()
        log.info(f"✅ Collection '{self.collection_name}' 初始化并加载完成")
        return collection

    @staticmethod
    def _sort_jobs_by_id(jobs: List[JobInfo]) -> List[JobInfo]:
        return sorted(jobs, key=lambda x: int(getattr(x, "id", 0) or 0))

    @classmethod
    def build_valid_jobs_and_texts(
        cls,
        jobs: List[JobInfo],
        desc_max_len: int = 10000,
    ) -> Tuple[List[JobInfo], List[int], List[str], List[int]]:
        """
        构建可向量化输入。

        Returns:
            valid_jobs: 可用于聚类/读取向量的岗位对象列表
            job_ids: 与 texts 对应的 job_id 列表
            texts: 与 job_ids 一一对应的文本特征
            skipped_ids: 被跳过的 job_id 列表
        """
        valid_jobs: List[JobInfo] = []
        job_ids: List[int] = []
        texts: List[str] = []
        skipped_ids: List[int] = []

        for job in cls._sort_jobs_by_id(jobs):
            job_id = getattr(job, "id", None)
            text_feature = build_text_feature(job, desc_max_len=desc_max_len)

            if job_id is None or not text_feature:
                if job_id is not None:
                    skipped_ids.append(int(job_id))
                continue

            valid_jobs.append(job)
            job_ids.append(int(job_id))
            texts.append(text_feature)

        return valid_jobs, job_ids, texts, skipped_ids

    def get_vector_count(self) -> int:
        """获取当前向量集合中的实体数量。"""
        self.collection.flush()
        return int(self.collection.num_entities or 0)

    def upsert_embeddings(
        self,
        job_ids: List[int],
        embeddings: np.ndarray,
    ) -> Dict[str, Any]:
        """将向量批量写入 Milvus。"""
        if not job_ids:
            return {"success": 0, "failed": 0, "total": 0, "errors": []}

        if len(job_ids) != len(embeddings):
            raise ValueError("job_ids 与 embeddings 数量不一致")

        data = [job_ids, embeddings.tolist()]

        try:
            self.collection.upsert(data)
            self.collection.flush()
            log.info(f"✅ 向量入库完成，写入 {len(job_ids)} 条")
            return {
                "success": len(job_ids),
                "failed": 0,
                "total": len(job_ids),
                "errors": [],
            }
        except Exception as e:
            log.error(f"❌ Milvus 批量插入失败: {e}")
            return {
                "success": 0,
                "failed": len(job_ids),
                "total": len(job_ids),
                "errors": [{"job_ids": job_ids[:20], "error": str(e)}],
            }

    async def sync_embeddings_with_database(
        self,
        session: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        batch_size: int = 64,
        desc_max_len: int = 10000,
    ) -> Dict[str, Any]:
        """
        根据“数据库岗位数量 vs 向量库数量”执行同步。

        规则：
        1. 数量相等：不进行向量化。
        2. 数据库数量更多：按 id 从后往前取多出来的那几条，进行向量化并入库。
        3. 数据库数量更少：直接报错。

        注意：这个规则默认岗位数据是按 id 递增追加写入的。
        """
        repo = JobRepository(session)
        log.info("开始检查数据库岗位数与向量库数量是否一致...")

        all_jobs = await repo.get_list_all(filters=filters)
        all_jobs = self._sort_jobs_by_id(all_jobs)
        db_count = len(all_jobs)
        vector_count = self.get_vector_count()

        if db_count == 0:
            log.warning("数据库中没有岗位数据，无需向量化。")
            return {
                "mode": "empty",
                "db_count": 0,
                "vector_count": vector_count,
                "success": 0,
                "failed": 0,
                "total": 0,
                "errors": [],
            }
        log.info(f"✅ 向量库数量({vector_count}) 与数据库数量({db_count})")

        if vector_count == db_count:
            log.info(f"✅ 向量库数量({vector_count}) 与数据库数量({db_count})一致，跳过向量化")
            return {
                "mode": "skip",
                "db_count": db_count,
                "vector_count": vector_count,
                "success": 0,
                "failed": 0,
                "total": 0,
                "errors": [],
            }

        if vector_count > db_count:
            raise ValueError(
                f"向量库中的数据量({vector_count}) 大于数据库岗位数量({db_count})，"
                f"不符合当前增量规则，请检查数据或重建向量库。"
            )

        missing_count = db_count - vector_count
        jobs_to_vectorize = all_jobs[-missing_count:]
        _, job_ids, texts_to_embed, skipped_ids = self.build_valid_jobs_and_texts(
            jobs_to_vectorize,
            desc_max_len=desc_max_len,
        )

        if len(job_ids) < missing_count:
            raise ValueError(
                f"数据库比向量库多 {missing_count} 条，但从后往前选出的新增岗位中，"
                f"只有 {len(job_ids)} 条可向量化，跳过的 job_id={skipped_ids}。"
            )

        log.info(
            f"检测到数据库新增 {missing_count} 条岗位，"
            f"将按 id 从后往前补齐向量：{job_ids[0]} ~ {job_ids[-1]}"
        )

        embeddings = self.embedder.encode(
            texts_to_embed,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype(np.float32)

        insert_stats = self.upsert_embeddings(job_ids, embeddings)
        return {
            **insert_stats,
            "mode": "incremental",
            "db_count": db_count,
            "vector_count_before": vector_count,
            "vector_count_after": self.get_vector_count(),
            "missing_count": missing_count,
            "inserted_job_ids": job_ids,
            "skipped_ids": skipped_ids,
        }



    # 一次性拉取整个集合的数据
    async def query_embeddings_by_job_ids(
            self,
            job_ids: List[int],
            batch_size: int = 1000,  # 这里的 batch_size 转变为迭代器单次拉取的数据量，可适当调大
            max_workers: int = 5,  # 保留参数签名，防止外部调用时传参报错
    ) -> Dict[int, np.ndarray]:
        """
        优化版（全量读取）：
        已知数据库的 id 和 job_ids 数量及内容完全一致。
        直接全量读取数据库中的所有向量，避免拼接超长的 IN 表达式。

        loop = asyncio.get_event_loop()

        def fetch_all_data() -> List[Dict[str, Any]]:
            # 因为 job_id 是主键且通常为正整数，使用 >= 0 即可匹配全量数据
            expr = "job_id >= 0"

            # 优先使用 query_iterator，避免全量数据过大直接撑爆 gRPC 的 64MB 限制
            if hasattr(self.collection, "query_iterator"):
                log.info(f"使用 query_iterator 游标安全拉取全量数据，单批次 {batch_size} 条")
                iterator = self.collection.query_iterator(
                    expr=expr,
                    output_fields=["job_id", "embedding"],
                    batch_size=batch_size
                )
                all_rows = []
                while True:
                    res = iterator.next()
                    if not res:
                        break
                    all_rows.extend(res)
                return all_rows
            else:
                # 兼容非常旧版本的 pymilvus（万一不支持游标）
                log.warning("当前 pymilvus 不支持 query_iterator，降级使用常规全量 query")
                return self.collection.query(
                    expr=expr,
                    output_fields=["job_id", "embedding"]
                )

        # 在异步 executor 中执行同步的 I/O 密集型拉取操作
        rows = await loop.run_in_executor(None, fetch_all_data)
        log.info(f"全量查询完成，共成功读取到 {len(rows)} 条岗位向量")

        # 将结果合并为映射字典
        embedding_map: Dict[int, np.ndarray] = {}
        for row in rows:
            jid = int(row["job_id"])
            embedding_map[jid] = np.array(row["embedding"], dtype=np.float32)

        return embedding_map
        
    # 正规的函数
    # async def query_embeddings_by_job_ids(
    #     self,
    #     job_ids: List[int],
    #     batch_size: int = 1000,
    #     max_workers: int = 10,
    # ) -> Dict[int, np.ndarray]:
    #     """
    #     优化版：按 job_id 批量读取向量，返回 {job_id: embedding}。
    #     使用内存索引 + 大批量获取 + 异步并行查询。
    #
    #     Args:
    #         job_ids: 待查询 job_id 列表
    #         batch_size: 每个批次查询大小
    #         max_workers: 最大并发协程数，限制并发压力
    #
    #     Returns:
    #         Dict[job_id, np.ndarray]: job_id 对应的向量
    #     """
    #     if not job_ids:
    #         return {}
    #
    #     self.collection.load()
    #
    #     # 使用信号量控制并发数，防止瞬间压力过大
    #     semaphore = asyncio.Semaphore(max_workers)
    #     log.info(f"开始查询 {len(job_ids)} 条向量，batch_size={batch_size}")
    #     async def fetch_batch(batch_ids: List[int]) -> Dict[int, np.ndarray]:
    #         log.info(f"查询任务已提交，共 {len(batch_ids)} 个批次")
    #         async with semaphore:
    #             result = {}
    #             ids_str = ",".join(map(str, batch_ids))
    #             expr = f"job_id in [{ids_str}]"
    #             log.info(f"查询任务已提交，expr={expr}")
    #
    #             # 在 IO 密集型操作中使用 loop.run_in_executor 或直接异步调用（pymilvus query 是同步阻塞的）
    #             loop = asyncio.get_event_loop()
    #             rows = await loop.run_in_executor(
    #                 None,
    #                 lambda: self.collection.query(
    #                     expr=expr,
    #                     output_fields=["embedding"]
    #                 )
    #             )
    #             log.info(f"查询任务已完成")
    #             for row in rows:
    #                 jid = int(row["job_id"])
    #                 result[jid] = np.array(row["embedding"], dtype=np.float32)
    #             return result
    #
    #     tasks = [
    #         fetch_batch(job_ids[i:i + batch_size])
    #         for i in range(0, len(job_ids), batch_size)
    #     ]
    #     log.info(f"查询任务已提交，共 {len(tasks)} 个批次")
    #
    #     results = await asyncio.gather(*tasks)
    #
    #     # 合并结果
    #     embedding_map: Dict[int, np.ndarray] = {}
    #     for r in results:
    #         embedding_map.update(r)
    #
    #     return embedding_map

    async def get_jobs_and_embeddings_for_hdbscan(
        self,
        session: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        batch_size: int = 64,
        desc_max_len: int = 10000,
    ) -> Tuple[List[JobInfo], np.ndarray, Dict[str, Any]]:
        """
        提供给 HDBSCAN 调用：
        1. 先按数量规则同步向量库
        2. 再读取所有可聚类岗位及其向量

        Returns:
            valid_jobs: 与 embeddings 一一对应的岗位对象列表
            embeddings: 聚类用向量矩阵
            sync_stats: 同步摘要
        """
        sync_stats = await self.sync_embeddings_with_database(
            session=session,
            filters=filters,
            batch_size=batch_size,
            desc_max_len=desc_max_len,
        )

        repo = JobRepository(session)
        all_jobs = await repo.get_list_all(filters=filters)
        valid_jobs, job_ids, _, skipped_ids = self.build_valid_jobs_and_texts(
            all_jobs,
            desc_max_len=desc_max_len,
        )
        if not valid_jobs:
            log.warning("清洗后没有可用于聚类的岗位文本。")
            return valid_jobs, np.empty((0, self.dim), dtype=np.float32), {
                **sync_stats,
                "valid": 0,
                "skipped": len(skipped_ids),
                "skipped_ids": skipped_ids,
            }
        embedding_map = await self.query_embeddings_by_job_ids(job_ids)
        log.info(f"成功读取 {len(embedding_map)} 条岗位向量。")
        missing_ids = [job_id for job_id in job_ids if job_id not in embedding_map]
        if missing_ids:
            raise ValueError(
                f"向量库中缺少 {len(missing_ids)} 条岗位向量，job_id={missing_ids[:20]}，"
                f"无法继续 HDBSCAN 聚类。"
            )

        embeddings = np.stack([embedding_map[job_id] for job_id in job_ids]).astype(np.float32)
        log.info(f"成功读取 {len(valid_jobs)} 条岗位向量，向量形状：{embeddings.shape}")

        return valid_jobs, embeddings, {
            **sync_stats,
            "valid": len(valid_jobs),
            "skipped": len(skipped_ids),
            "skipped_ids": skipped_ids,
            "collection_name": self.collection_name,
            "embedding_model": self.embedding_model,
            "vector_dim": self.dim,
        }

    async def vectorize_and_store_all(
        self,
        session: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        batch_size: int = 64,
        desc_max_len: int = 10000,
    ) -> Dict[str, Any]:
        """
        保留全量入口：直接把数据库全部岗位重新向量化并 upsert。
        """
        repo = JobRepository(session)

        log.info("开始从数据库获取原始岗位数据...")
        all_jobs = await repo.get_list_all(filters=filters)
        total_db_jobs = len(all_jobs)

        if not all_jobs:
            log.warning("数据库中没有原始岗位数据可供向量化。")
            return {
                "success": 0,
                "failed": 0,
                "total": 0,
                "skipped": 0,
                "skipped_ids": [],
                "errors": [],
            }

        _, job_ids, texts_to_embed, skipped_ids = self.build_valid_jobs_and_texts(
            all_jobs,
            desc_max_len=desc_max_len,
        )

        if not texts_to_embed:
            log.warning("清洗后没有可用于向量化的岗位文本。")
            return {
                "success": 0,
                "failed": 0,
                "total": total_db_jobs,
                "skipped": len(skipped_ids),
                "skipped_ids": skipped_ids,
                "errors": [],
            }

        log.info(f"成功构建 {len(texts_to_embed)} 条文本特征，开始全量向量化...")
        embeddings = self.embedder.encode(
            texts_to_embed,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype(np.float32)

        insert_stats = self.upsert_embeddings(job_ids, embeddings)
        return {
            **insert_stats,
            "total": total_db_jobs,
            "valid": len(job_ids),
            "skipped": len(skipped_ids),
            "skipped_ids": skipped_ids,
            "collection_name": self.collection_name,
            "embedding_model": self.embedding_model,
            "vector_dim": self.dim,
        }

    async def vectorize_and_store_all_async(
        self,
        session: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        batch_size: int = 64,
        desc_max_len: int = 10000,
    ) -> Dict[str, Any]:
        return await self.vectorize_and_store_all(
            session=session,
            filters=filters,
            batch_size=batch_size,
            desc_max_len=desc_max_len,
        )

    def search_similar(
        self,
        text: str,
        top_k: int = 20,
        search_params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        用同一套向量化逻辑做相似岗位召回。
        只返回 job_id 和 score。
        """
        if not text:
            return []

        query_vector = self.embedder.encode(
            [clean_text(text)],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype(np.float32)[0]

        search_params = search_params or {
            "metric_type": self.metric_type,
            "params": {"ef": 64},
        }

        results = self.collection.search(
            data=[query_vector.tolist()],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["job_id"],
        )

        matched_jobs: List[Dict[str, Any]] = []
        for hits in results:
            for hit in hits:
                matched_jobs.append(
                    {
                        "job_id": hit.entity.get("job_id"),
                        "score": hit.score,
                    }
                )
        return matched_jobs

    def delete_job(self, job_id: int) -> None:
        self.collection.delete(expr=f"job_id in [{int(job_id)}]")
        self.collection.flush()
        log.info(f"✅ 已删除岗位向量：job_id={job_id}")

    def reset_collection(self) -> None:
        """删除整个集合并重新创建。谨慎使用！"""
        self.collection.drop()
        self.collection = self._init_collection()

    def drop_collection(self) -> None:
        self.collection.drop()

    def get_collection_info(self):
        return self.collection.describe()


async def main():
    engine = create_async_engine(get_db_url(), echo=False)
    AsyncSessionLocal = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    store = JobOriginalVectorStore(
        collection_name="job_original_embeddings",
        embedding_model="BAAI/bge-base-zh-v1.5",
    )

    try:
        async with AsyncSessionLocal() as session:
            result = await store.sync_embeddings_with_database(
                session=session
            )
            print(result)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
    # store = JobOriginalVectorStore(
    #     collection_name="job_original_embeddings",
    #     embedding_model="BAAI/bge-base-zh-v1.5",
    # )
    # store.reset_collection()