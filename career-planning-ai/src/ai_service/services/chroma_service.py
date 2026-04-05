"""
Chroma 向量数据库通用服务模块

提供向量存储的增删改查功能，支持单例模式管理连接。
"""
from typing import Any

from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStoreRetriever

from ai_service.services import log as logger
from config import settings

_instances: dict[str, "ChromaService"] = {}


def get_default_embedding() -> Embeddings:
    """获取默认的 Embedding 模型"""
    return DashScopeEmbeddings(
        model=settings.chroma_config.model_name,
        dashscope_api_key=settings.chroma_config.api_key.get_secret_value(),
    )


class ChromaService:
    """
    Chroma 向量数据库服务类

    功能:
        - 向量文档存储与检索
        - 支持批量操作
        - 支持相似度搜索
        - 单例模式管理多个 collection

    Example:
        >>> # 获取单例实例
        >>> service = ChromaService.get_instance("my_collection")
        >>> # 批量添加文档
        >>> service.add_documents([
        ...     Document(page_content="内容1", metadata={"source": "test"}),
        ...     Document(page_content="内容2", metadata={"source": "test"}),
        ... ])
        >>> # 相似度搜索
        >>> results = service.similarity_search("查询内容", k=3)
        >>> # 带分数的搜索
        >>> results_with_scores = service.similarity_search_with_score("查询内容")
    """

    def __init__(
            self,
            collection_name: str = "default",
            embedding_function: Embeddings | None = None,
            persist_directory: str | None = None,
    ):
        """
        初始化 Chroma 服务

        Args:
            collection_name: 集合名称
            embedding_function: 自定义 Embedding 模型，默认使用 DashScope
            persist_directory: 持久化目录，默认使用配置中的路径
        """
        self._collection_name = collection_name
        self._embedding_function = embedding_function or get_default_embedding()
        self._persist_directory = persist_directory or settings.chroma_config.save_path

        try:
            self._vector_store = Chroma(
                collection_name=self._collection_name,
                embedding_function=self._embedding_function,
                persist_directory=self._persist_directory,
            )
            logger.info(
                f"Chroma 服务初始化成功: collection={collection_name}, path={self._persist_directory}"
            )
        except Exception as e:
            logger.error(f"Chroma 服务初始化失败: {e}", exc_info=True)
            raise

    @classmethod
    def get_instance(
            cls,
            collection_name: str = "default_collection",
            embedding_function: Embeddings | None = None,
            persist_directory: str | None = None,
    ) -> "ChromaService":
        """
        获取单例实例

        Args:
            collection_name: 集合名称
            embedding_function: 自定义 Embedding 模型
            persist_directory: 持久化目录

        Returns:
            ChromaService 实例
        """
        cache_key = f"{collection_name}:{persist_directory or settings.chroma_config.save_path}"
        if cache_key not in _instances:
            _instances[cache_key] = cls(
                collection_name=collection_name,
                embedding_function=embedding_function,
                persist_directory=persist_directory,
            )
        return _instances[cache_key]

    @classmethod
    def clear_instance(cls, collection_name: str = "default") -> None:
        """清除缓存的实例"""
        persist_directory = settings.chroma_config.save_path
        cache_key = f"{collection_name}:{persist_directory}"
        if cache_key in _instances:
            del _instances[cache_key]
            logger.info(f"已清除 Chroma 实例缓存: {collection_name}")

    @property
    def vector_store(self) -> Chroma:
        """获取底层 VectorStore 实例"""
        return self._vector_store

    @property
    def collection_name(self) -> str:
        """获取集合名称"""
        return self._collection_name

    def get_retriever(
            self,
            search_type: str = "similarity",
            search_kwargs: dict[str, Any] | None = None,
    ) -> VectorStoreRetriever:
        """
        获取检索器

        Args:
            search_type: 搜索类型 (similarity, mmr, similarity_score_threshold)
            search_kwargs: 搜索参数，默认使用配置中的 k 值

        Returns:
            VectorStoreRetriever 实例
        """
        if search_kwargs is None:
            search_kwargs = {"k": settings.chroma_config.k}
        return self._vector_store.as_retriever(
            search_type=search_type, search_kwargs=search_kwargs
        )

    def add_content(self, content: str, metadata: dict[str, Any] | None = None) -> list[str]:
        """
        添加单个文档

        Args:
            content: 文档内容
            metadata: 元数据

        Returns:
            添加的文档 ID 列表
        """
        return self.add_documents([Document(page_content=content, metadata=metadata or {})])

    def add_documents(
            self,
            documents: list[Document],
            ids: list[str] | None = None,
    ) -> list[str]:
        """
        批量添加文档

        Args:
            documents: 文档列表
            ids: 可选的文档 ID 列表

        Returns:
            添加的文档 ID 列表
        """
        if not documents:
            logger.warning("尝试添加空文档列表")
            return []

        try:
            result = self._vector_store.add_documents(documents, ids=ids)
            logger.info(f"成功添加 {len(documents)} 个文档到集合 {self._collection_name}")
            return result
        except KeyError as e:
            logger.error(f"DashScope API 调用失败，可能是限流或网络问题。KeyError: {e}")
            raise RuntimeError(
                "DashScope embedding API 调用失败。常见原因：\n"
                "1. API 限流 - 请稍后重试或减少并发请求\n"
                "2. API 密钥无效 - 请检查配置\n"
                "3. 网络问题 - 请检查网络连接"
            ) from e
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            raise

    def add_texts(
            self,
            texts: list[str],
            metadata: list[dict[str, Any]] | None = None,
            ids: list[str] | None = None,
    ) -> list[str]:
        """
        批量添加文本

        Args:
            texts: 文本列表
            metadata: 元数据列表
            ids: 可选的文档 ID 列表

        Returns:
            添加的文档 ID 列表
        """
        if not texts:
            logger.warning("尝试添加空文本列表")
            return []

        try:
            result = self._vector_store.add_texts(texts, metadatas=metadata, ids=ids)
            logger.info(f"成功添加 {len(texts)} 条文本到集合 {self._collection_name}")
            return result
        except Exception as e:
            logger.error(f"添加文本失败: {e}")
            raise

    def find_content(self, query: str) -> list[Document]:
        """
        使用检索器查找内容

        Args:
            query: 查询文本

        Returns:
            相关文档列表
        """
        return self.get_retriever().invoke(query)

    def similarity_search(
            self,
            query: str,
            k: int | None = None,
            filter_dict: dict[str, Any] | None = None,
    ) -> list[Document]:
        """
        相似度搜索

        Args:
            query: 查询文本
            k: 返回文档数量，默认使用配置中的值
            filter_dict: 元数据过滤条件

        Returns:
            相似文档列表
        """
        k = k or settings.chroma_config.k
        try:
            return self._vector_store.similarity_search(query, k=k, filter=filter_dict)
        except Exception as e:
            logger.error(f"相似度搜索失败: {e}")
            raise

    def similarity_search_with_score(
            self,
            query: str,
            k: int | None = None,
            filter_dict: dict[str, Any] | None = None,
    ) -> list[tuple[Document, float]]:
        """
        带分数的相似度搜索

        Args:
            query: 查询文本
            k: 返回文档数量，默认使用配置中的值
            filter_dict: 元数据过滤条件

        Returns:
            (文档, 相似度分数) 元组列表，分数越小越相似
        """
        k = k or settings.chroma_config.k
        try:
            return self._vector_store.similarity_search_with_score(query, k=k, filter=filter_dict)
        except Exception as e:
            logger.error(f"带分数的相似度搜索失败: {e}")
            raise

    def max_marginal_relevance_search(
            self,
            query: str,
            k: int = 4,
            fetch_k: int = 20,
            lambda_mult: float = 0.5,
            filter_dict: dict[str, Any] | None = None,
    ) -> list[Document]:
        """
        最大边际相关性搜索（MMR），平衡相关性和多样性

        Args:
            query: 查询文本
            k: 返回文档数量
            fetch_k: 候选文档数量
            lambda_mult: 0-1 之间，1 表示最大相关性，0 表示最大多样性
            filter_dict: 元数据过滤条件

        Returns:
            文档列表
        """
        try:
            return self._vector_store.max_marginal_relevance_search(
                query, k=k, fetch_k=fetch_k, lambda_mult=lambda_mult, filter=filter_dict
            )
        except Exception as e:
            logger.error(f"MMR 搜索失败: {e}")
            raise

    def delete_by_ids(self, ids: list[str]) -> None:
        """
        根据 ID 删除文档

        Args:
            ids: 要删除的文档 ID 列表
        """
        if not ids:
            return

        try:
            self._vector_store.delete(ids=ids)
            logger.info(f"已删除 {len(ids)} 个文档: {ids}")
        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            raise

    def delete_by_filter(self, filter_dict: dict[str, Any]) -> None:
        """
        根据元数据过滤条件删除文档

        Args:
            filter_dict: 元数据过滤条件
        """
        try:
            self._vector_store.delete(filter=filter_dict)
            logger.info(f"已删除符合过滤条件的文档: {filter_dict}")
        except Exception as e:
            logger.error(f"按条件删除文档失败: {e}")
            raise

    def delete_all(self) -> None:
        """删除集合中的所有文档"""
        try:
            self._vector_store.delete_collection()
            # 重新创建空集合
            self._vector_store = Chroma(
                collection_name=self._collection_name,
                embedding_function=self._embedding_function,
                persist_directory=self._persist_directory,
            )
            logger.info(f"已清空集合 {self._collection_name} 中的所有文档")
        except Exception as e:
            logger.error(f"清空集合失败: {e}")
            raise

    def count(self) -> int:
        """获取文档数量"""
        try:
            # noinspection PyProtectedMember
            collection = self._vector_store._collection
            return collection.count()
        except Exception as e:
            logger.error(f"获取文档数量失败: {e}")
            raise

    def get(self, ids: list[str] | None = None, where: dict[str, Any] | None = None) -> Any:
        """
        获取文档（底层 Chroma 接口）

        Args:
            ids: 文档 ID 列表
            where: 过滤条件

        Returns:
            GetResult: 包含 ids, documents, metadata 等字段的对象
        """
        try:
            # noinspection PyProtectedMember
            collection = self._vector_store._collection
            return collection.get(ids=ids, where=where)
        except Exception as e:
            logger.error(f"获取文档失败: {e}")
            raise

    def __len__(self) -> int:
        """支持 len() 函数"""
        return self.count()

    def __repr__(self) -> str:
        return f"ChromaService(collection={self._collection_name}, docs_count={self.count()})"


chroma_service = ChromaService.get_instance(collection_name=settings.chroma_config.collection_name.default)
