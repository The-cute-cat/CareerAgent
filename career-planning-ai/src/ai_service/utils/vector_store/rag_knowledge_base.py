import os
import json
import csv
import uuid
from typing import List, Dict, Any, Optional

from docx import Document
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient, DataType

from ai_service.utils.logger_handler import log
from config import settings

# =========================
# 1. 数据结构与常量
# =========================

ALLOWED_CATEGORIES = {
    "job_jd",  # 原始岗位JD
    "job_profile",  # 标准岗位画像
    "learning_path",  # 学习路径
    "resume",  # 简历/学生画像
    "general",  # 其他通用知识
}

DEFAULT_EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


# =========================
# 2. 工具函数：文件读取
# =========================

def read_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def read_json(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return json.dumps(data, ensure_ascii=False, indent=2)


def read_csv(file_path: str, max_rows: Optional[int] = None) -> str:
    rows = []
    with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            rows.append(json.dumps(row, ensure_ascii=False))
            if max_rows and i + 1 >= max_rows:
                break
    return "\n".join(rows)


def read_docx(file_path: str) -> str:
    doc = Document(file_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def read_pdf_by_pages(file_path: str) -> List[Dict[str, Any]]:
    """
    按页读取 PDF 文本，返回:
    [
        {"page_no": 1, "text": "..."},
        {"page_no": 2, "text": "..."},
    ]
    """
    reader = PdfReader(file_path)
    pages = []

    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            pages.append({
                "page_no": i,
                "text": text
            })

    return pages


def read_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".txt", ".md"]:
        return read_txt(file_path)
    if ext == ".json":
        return read_json(file_path)
    if ext == ".csv":
        return read_csv(file_path)
    if ext == ".docx":
        return read_docx(file_path)
    if ext == ".pdf":
        # 非 PDF 按页逻辑时，兜底拼接
        pages = read_pdf_by_pages(file_path)
        return "\n".join([p["text"] for p in pages])

    raise ValueError(f"暂不支持的文件类型: {ext}")


# =========================
# 3. 文本分块
# =========================

def split_text(
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 100
) -> List[str]:
    """
    简单字符分块
    - chunk_size: 每块最大字符数
    - chunk_overlap: 相邻块重叠字符数
    """
    text = (text or "").strip()
    if not text:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap 必须小于 chunk_size")

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == text_len:
            break
        start = end - chunk_overlap

    return chunks


# =========================
# 4. Milvus 向量知识库
# =========================

class RAGKnowledgeBase:
    """
    单 collection 存储，使用 category 区分资料类型
    适合:
    - job_jd
    - job_profile
    - learning_path
    - resume
    - general
    """

    def __init__(
            self,
            local_host: str = None,
            local_port: int = 19530,
            cloud_url: str = None,
            cloud_token: str = None,
            db_name: str = "default",
            collection_name: str = "career_rag_kb",
            embedding_model_name: str = DEFAULT_EMBED_MODEL,
    ):
        # 从配置文件读取默认值
        self.local_host = local_host or settings.milvus.local.host
        self.local_port = local_port or settings.milvus.local.port
        self.cloud_url = cloud_url or settings.milvus.cloud.url
        self.cloud_token = cloud_token or (
            settings.milvus.cloud.token.get_secret_value() if settings.milvus.cloud.token else None)
        self.db_name = db_name
        self.collection_name = collection_name
        self.is_available = True
        self._connect_error_msg = ""
        self._connected_uri = None

        try:
            # 智能连接（支持自动故障转移）
            self._connect_with_failover()

            self.embedding_model = SentenceTransformer(embedding_model_name)
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

            self._ensure_collection()
            log.info(f"✅ RAGKnowledgeBase 初始化完成，Milvus 可用")
        except Exception as e:
            self.is_available = False
            self._connect_error_msg = str(e)
            self.client = None
            self.embedding_model = None
            self.embedding_dim = 0
            log.warning(f"⚠️警告：RAGKnowledgeBase 初始化失败，RAG知识库服务不可用: {e}")

    def _connect_with_failover(self):
        """
        智能连接 Milvus（支持自动故障转移）
        - force_local=true: 强制使用本地配置，不进行故障转移
        - force_local=false: 自动选择（优先本地，失败后尝试云端）
        """
        use_cloud = settings.milvus.cloud.is_can_use
        force_local = getattr(settings.milvus, 'force_local', False)

        if force_local:
            # 强制使用本地，不尝试云端
            connected, uri = self._try_connect("local", self.local_host, self.local_port)
            if not connected:
                raise ConnectionError(
                    f"❌ 无法连接到本地 Milvus 服务器（强制本地模式）！\n"
                    f"  - 地址: {self.local_host}:{self.local_port}"
                )
            self._connected_uri = uri
        else:
            # 自动选择：优先本地，失败后尝试云端
            connections_to_try = [("local", self.local_host, self.local_port)]
            if use_cloud:
                connections_to_try.append(("cloud", self.cloud_url, self.cloud_token))
            connected = False
            for i, (conn_type, param1, param2) in enumerate(connections_to_try):
                if i > 0:
                    log.warning(f"⚠️ 上一个服务器连接失败，尝试切换到 {conn_type} 服务器...")
                connected, uri = self._try_connect(conn_type, param1, param2)
                if connected:
                    self._connected_uri = uri
                    break
            if not connected:
                raise ConnectionError(
                    f"❌ 无法连接到任何 Milvus 服务器！\n"
                    f"  - 本地: {self.local_host}:{self.local_port}\n"
                    f"  - 云端: {self.cloud_url if use_cloud else '未配置'}"
                )

    def _try_connect(self, conn_type: str, param1, param2) -> tuple:
        """尝试连接 Milvus，返回 (是否成功, uri)"""
        try:
            if conn_type == "local":
                uri = f"http://{param1}:{param2}"
                self.client = MilvusClient(uri=uri, db_name=self.db_name)
                log.info(f"✅ 已连接到本地 Milvus: {param1}:{param2}")
            else:
                uri = param1
                self.client = MilvusClient(uri=uri, token=param2, db_name=self.db_name)
                log.info(f"✅ 已连接到 Zilliz 云服务!")
            return True, uri
        except Exception as e:
            log.warning(f"⚠️ 连接 {conn_type} 失败: {e}")
            return False, None

    # ---------- 基础 ----------
    def _check_category(self, category: str):
        if category not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"非法 category: {category}，允许值为: {sorted(ALLOWED_CATEGORIES)}"
            )

    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.embedding_model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embeddings.tolist()

    def _ensure_collection(self):
        if self.client.has_collection(self.collection_name):
            return

        schema = MilvusClient.create_schema(
            auto_id=False,
            enable_dynamic_field=False,
        )

        schema.add_field(
            field_name="id",
            datatype=DataType.VARCHAR,
            is_primary=True,
            max_length=128,
        )
        schema.add_field(
            field_name="doc_id",
            datatype=DataType.VARCHAR,
            max_length=128,
        )
        schema.add_field(
            field_name="category",
            datatype=DataType.VARCHAR,
            max_length=64,
        )
        schema.add_field(
            field_name="title",
            datatype=DataType.VARCHAR,
            max_length=512,
        )
        schema.add_field(
            field_name="source",
            datatype=DataType.VARCHAR,
            max_length=2048,
        )
        schema.add_field(
            field_name="page_no",
            datatype=DataType.INT64,
        )
        schema.add_field(
            field_name="chunk_index",
            datatype=DataType.INT64,
        )
        schema.add_field(
            field_name="content",
            datatype=DataType.VARCHAR,
            max_length=65535,
        )
        schema.add_field(
            field_name="metadata",
            datatype=DataType.JSON,
        )
        schema.add_field(
            field_name="embedding",
            datatype=DataType.FLOAT_VECTOR,
            dim=self.embedding_dim,
        )

        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="embedding",
            index_type="AUTOINDEX",
            metric_type="COSINE",
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params,
        )
        self.client.load_collection(self.collection_name)

    # ---------- 通用单条文本入库 ----------
    def add_text(
            self,
            category: str,
            text: str,
            title: str,
            source: str = "",
            metadata: Optional[Dict[str, Any]] = None,
            doc_id: Optional[str] = None,
            chunk_size: int = 500,
            chunk_overlap: int = 100,
    ) -> Dict[str, Any]:
        if not self.is_available:
            return {"success": False, "message": "知识库服务暂不可用，请稍后重试", "doc_id": doc_id}
        self._check_category(category)
        metadata = metadata or {}
        doc_id = doc_id or str(uuid.uuid4())

        chunks = split_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        if not chunks:
            return {"success": False, "message": "文本为空，未入库", "doc_id": doc_id}

        rows = []
        for idx, chunk in enumerate(chunks):
            rows.append({
                "id": f"{doc_id}__{idx}",
                "doc_id": doc_id,
                "category": category,
                "title": title,
                "source": source,
                "page_no": 0,  # 普通文本无页码
                "chunk_index": idx,
                "content": chunk,
                "metadata": metadata,
            })

        embeddings = self._embed_texts([row["content"] for row in rows])
        for row, emb in zip(rows, embeddings):
            row["embedding"] = emb

        self.client.insert(
            collection_name=self.collection_name,
            data=rows,
        )

        return {
            "success": True,
            "doc_id": doc_id,
            "category": category,
            "title": title,
            "source": source,
            "chunk_count": len(rows),
        }

    # ---------- PDF 入库：按页 + 分块 ----------
    def add_pdf(
            self,
            category: str,
            file_path: str,
            title: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None,
            doc_id: Optional[str] = None,
            chunk_size: int = 500,
            chunk_overlap: int = 100,
    ) -> Dict[str, Any]:
        if not self.is_available:
            return {"success": False, "message": "知识库服务暂不可用，请稍后重试", "doc_id": doc_id}
        self._check_category(category)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        metadata = metadata or {}
        doc_id = doc_id or str(uuid.uuid4())
        title = title or os.path.basename(file_path)

        pages = read_pdf_by_pages(file_path)
        if not pages:
            return {
                "success": False,
                "doc_id": doc_id,
                "message": "PDF 未提取到有效文本"
            }

        rows = []
        global_chunk_index = 0

        for page in pages:
            page_no = page["page_no"]
            page_text = page["text"]
            chunks = split_text(
                page_text,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )

            for chunk in chunks:
                row_metadata = {
                    **metadata,
                    "file_type": "pdf",
                    "origin_name": os.path.basename(file_path),
                }
                rows.append({
                    "id": f"{doc_id}__{global_chunk_index}",
                    "doc_id": doc_id,
                    "category": category,
                    "title": title,
                    "source": file_path,
                    "page_no": page_no,
                    "chunk_index": global_chunk_index,
                    "content": chunk,
                    "metadata": row_metadata,
                })
                global_chunk_index += 1

        embeddings = self._embed_texts([row["content"] for row in rows])
        for row, emb in zip(rows, embeddings):
            row["embedding"] = emb

        self.client.insert(
            collection_name=self.collection_name,
            data=rows,
        )

        return {
            "success": True,
            "doc_id": doc_id,
            "category": category,
            "title": title,
            "source": file_path,
            "page_count": len(pages),
            "chunk_count": len(rows),
        }

    # ---------- 通用文件入库 ----------
    def add_file(
            self,
            category: str,
            file_path: str,
            title: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None,
            doc_id: Optional[str] = None,
            chunk_size: int = 500,
            chunk_overlap: int = 100,
    ) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        title = title or os.path.basename(file_path)

        if ext == ".pdf":
            return self.add_pdf(
                category=category,
                file_path=file_path,
                title=title,
                metadata=metadata,
                doc_id=doc_id,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )

        text = read_file(file_path)
        file_metadata = {
            **(metadata or {}),
            "file_type": ext.lstrip("."),
            "origin_name": os.path.basename(file_path),
        }

        return self.add_text(
            category=category,
            text=text,
            title=title,
            source=file_path,
            metadata=file_metadata,
            doc_id=doc_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    # ---------- 批量文件入库 ----------
    def add_files(
            self,
            category: str,
            file_paths: List[str],
            common_metadata: Optional[Dict[str, Any]] = None,
            chunk_size: int = 500,
            chunk_overlap: int = 100,
    ) -> List[Dict[str, Any]]:
        results = []
        for fp in file_paths:
            try:
                res = self.add_file(
                    category=category,
                    file_path=fp,
                    metadata=common_metadata,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                )
                results.append(res)
            except Exception as e:
                results.append({
                    "success": False,
                    "file_path": fp,
                    "error": str(e),
                })
        return results

    # ---------- 结构化 JSON 入库 ----------
    def add_structured_records(
            self,
            category: str,
            records: List[Dict[str, Any]],
            title_field: str = "title",
            content_fields: Optional[List[str]] = None,
            metadata_fields: Optional[List[str]] = None,
            id_field: Optional[str] = None,
            chunk_size: int = 500,
            chunk_overlap: int = 100,
    ) -> List[Dict[str, Any]]:
        self._check_category(category)
        results = []

        for idx, record in enumerate(records):
            try:
                title = str(record.get(title_field, f"{category}_{idx}"))

                if content_fields:
                    parts = []
                    for field in content_fields:
                        value = record.get(field, "")
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value, ensure_ascii=False)
                        parts.append(f"{field}: {value}")
                    text = "\n".join(parts)
                else:
                    text = json.dumps(record, ensure_ascii=False, indent=2)

                metadata = {}
                if metadata_fields:
                    for field in metadata_fields:
                        metadata[field] = record.get(field)

                doc_id = str(record.get(id_field)) if id_field and record.get(id_field) else None

                res = self.add_text(
                    category=category,
                    text=text,
                    title=title,
                    source="structured_records",
                    metadata=metadata,
                    doc_id=doc_id,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                )
                results.append(res)
            except Exception as e:
                results.append({
                    "success": False,
                    "record_index": idx,
                    "error": str(e),
                })

        return results

    # ---------- 检索 ----------
    def search(
            self,
            query: str,
            category: Optional[str] = None,
            top_k: int = 5,
            filters: Optional[Dict[str, Any]] = None,
            output_fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        if not self.is_available:
            return [{"error": "知识库服务暂不可用，请稍后重试"}]
        if category:
            self._check_category(category)

        output_fields = output_fields or [
            "id",
            "doc_id",
            "category",
            "title",
            "source",
            "page_no",
            "chunk_index",
            "content",
            "metadata",
        ]

        expr_parts = []

        if category:
            expr_parts.append(f'category == "{category}"')

        if filters:
            for k, v in filters.items():
                if isinstance(v, str):
                    expr_parts.append(f'{k} == "{v}"')
                elif isinstance(v, bool):
                    expr_parts.append(f"{k} == {str(v).lower()}")
                else:
                    expr_parts.append(f"{k} == {v}")

        filter_expr = " and ".join(expr_parts) if expr_parts else ""

        query_embedding = self._embed_texts([query])[0]

        result = self.client.search(
            collection_name=self.collection_name,
            data=[query_embedding],
            anns_field="embedding",
            limit=top_k,
            filter=filter_expr,
            output_fields=output_fields,
        )

        return self._format_search_result(result)

    # ---------- 全局检索 ----------
    def search_global(
            self,
            query: str,
            top_k: int = 8,
            filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        return self.search(
            query=query,
            category=None,
            top_k=top_k,
            filters=filters,
        )

    # ---------- 删除 ----------
    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        self.client.delete(
            collection_name=self.collection_name,
            filter=f'doc_id == "{doc_id}"'
        )
        return {
            "success": True,
            "doc_id": doc_id,
            "message": "删除完成",
        }

    # ---------- 查看分类统计 ----------
    def count_by_category(self) -> Dict[str, int]:
        result = {}
        for category in sorted(ALLOWED_CATEGORIES):
            items = self.client.query(
                collection_name=self.collection_name,
                filter=f'category == "{category}"',
                output_fields=["id"],
                limit=16384,
            )
            result[category] = len(items)
        return result

    # ---------- 查询某文档 ----------
    def query_by_doc_id(
            self,
            doc_id: str,
            limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        result = self.client.query(
            collection_name=self.collection_name,
            filter=f'doc_id == "{doc_id}"',
            output_fields=[
                "id",
                "doc_id",
                "category",
                "title",
                "source",
                "page_no",
                "chunk_index",
                "content",
                "metadata",
            ],
            limit=limit,
        )
        result.sort(key=lambda x: (x["page_no"], x["chunk_index"]))
        return result

    # ---------- 重置整个知识库 ----------
    def reset_all(self) -> Dict[str, Any]:
        if self.client.has_collection(self.collection_name):
            self.client.drop_collection(self.collection_name)
        self._ensure_collection()
        return {"success": True, "message": "整个知识库已重置"}

    # ---------- 结果格式化 ----------
    @staticmethod
    def _format_search_result(result: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        hits = []
        if not result:
            return hits

        for item in result[0]:
            entity = item.get("entity", {})
            hit = {
                "score": item.get("distance"),
                **entity,
            }
            hits.append(hit)
        return hits


# =========================
# 5. 业务层封装：按资料情况存入
# =========================

class CareerKnowledgeService:
    """
    适合你的项目场景：
    - 岗位原始JD
    - 岗位画像
    - 学习路径
    - 学生简历 / 学生画像
    - 通用资料(PDF/Docx/Txt等)
    """

    def __init__(self, kb: RAGKnowledgeBase):
        self.kb = kb

    # ---- 1) 存岗位原始JD ----
    def add_job_jds(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return self.kb.add_structured_records(
            category="job_jd",
            records=jobs,
            title_field="job_title",
            content_fields=[
                "job_title",
                "industry",
                "salary_range",
                "company_name",
                "job_desc",
            ],
            metadata_fields=[
                "industry",
                "salary_range",
                "company_name",
            ],
            id_field="id",
        )

    # ---- 2) 存岗位画像 ----
    def add_job_profiles(self, profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return self.kb.add_structured_records(
            category="job_profile",
            records=profiles,
            title_field="title",
            content_fields=[
                "title",
                "core_responsibilities",
                "skills",
                "qualities",
                "career_path",
            ],
            metadata_fields=[
                "title",
            ],
            id_field="id",
        )

    # ---- 3) 存学习路径 ----
    def add_learning_paths(self, paths: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return self.kb.add_structured_records(
            category="learning_path",
            records=paths,
            title_field="title",
            content_fields=[
                "title",
                "skill_name",
                "difficulty",
                "steps",
                "resources",
            ],
            metadata_fields=[
                "skill_name",
                "difficulty",
            ],
            id_field="id",
        )

    # ---- 4) 存学生简历/画像 ----
    def add_resumes(self, resumes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return self.kb.add_structured_records(
            category="resume",
            records=resumes,
            title_field="student_name",
            content_fields=[
                "student_name",
                "education",
                "major",
                "skills",
                "certificates",
                "internships",
                "projects",
                "career_intention",
            ],
            metadata_fields=[
                "education",
                "major",
                "career_intention",
            ],
            id_field="id",
        )

    # ---- 5) 存通用资料文件 ----
    def add_general_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        return self.kb.add_files(
            category="general",
            file_paths=file_paths,
        )

    # ---- 6) 存某类资料文件 ----
    def add_category_files(
            self,
            category: str,
            file_paths: List[str],
            common_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        return self.kb.add_files(
            category=category,
            file_paths=file_paths,
            common_metadata=common_metadata,
        )

    # ---- 7) 按场景检索 ----
    def retrieve(self, query: str, scene: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if scene == "job_match":
            return self.kb.search(query, category="job_jd", top_k=top_k)

        if scene == "job_profile":
            return self.kb.search(query, category="job_profile", top_k=top_k)

        if scene == "learning_path":
            return self.kb.search(query, category="learning_path", top_k=top_k)

        if scene == "resume":
            return self.kb.search(query, category="resume", top_k=top_k)

        if scene == "global":
            return self.kb.search_global(query, top_k=top_k)

        raise ValueError(f"未知 scene: {scene}")


# =========================
# 6. 示例：怎么用
# =========================

def demo():
    kb = RAGKnowledgeBase(
        uri="http://localhost:19530",
        token=None,  # 若有用户名密码可填: "root:Milvus"
        db_name="default",
        collection_name="career_rag_kb",
    )
    service = CareerKnowledgeService(kb)

    # ---------- 1. 存岗位JD ----------
    jobs = [
        {
            "id": "job_001",
            "job_title": "Java后端开发工程师",
            "industry": "互联网",
            "salary_range": "10k-15k",
            "company_name": "星云科技",
            "job_desc": "负责后端接口开发、数据库设计、Spring Boot 微服务开发、Redis 缓存优化。"
        },
        {
            "id": "job_002",
            "job_title": "Python数据分析工程师",
            "industry": "互联网",
            "salary_range": "8k-12k",
            "company_name": "数智未来",
            "job_desc": "负责数据清洗、报表分析、可视化展示，熟悉 Python、Pandas、SQL。"
        },
    ]
    print("\n=== 存岗位JD ===")
    print(service.add_job_jds(jobs))

    # ---------- 2. 存 PDF 通用资料 ----------
    # 假设你有 PDF:
    # ./docs/职业规划指南.pdf
    # ./docs/SpringBoot学习路线.pdf
    pdf_paths = [
        "./docs/职业规划指南.pdf",
        "./docs/SpringBoot学习路线.pdf",
    ]
    print("\n=== 存通用PDF资料 ===")
    print(service.add_general_files(pdf_paths))

    # ---------- 3. 单独存岗位类PDF ----------
    job_pdf_paths = [
        "./docs/后端开发岗位说明.pdf",
    ]
    print("\n=== 存岗位类PDF资料 ===")
    print(service.add_category_files(
        category="job_jd",
        file_paths=job_pdf_paths,
        common_metadata={"domain": "job_pdf"}
    ))

    # ---------- 4. 检索：岗位 ----------
    print("\n=== 检索：岗位匹配 ===")
    hits = service.retrieve(
        "我想找后端开发相关岗位，需要 Spring Boot 和 MySQL",
        scene="job_match",
        top_k=3
    )
    for h in hits:
        print(json.dumps(h, ensure_ascii=False, indent=2))

    # ---------- 5. 检索：学习路径 ----------
    print("\n=== 检索：全局 ===")
    hits = service.retrieve(
        "如何学习 Spring Boot 成为后端工程师",
        scene="global",
        top_k=5
    )
    for h in hits:
        print(json.dumps(h, ensure_ascii=False, indent=2))

    # ---------- 6. 分类统计 ----------
    print("\n=== 分类统计 ===")
    print(kb.count_by_category())


if __name__ == "__main__":
    demo()
