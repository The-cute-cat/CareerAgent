"""
岗位向量存储模块

该模块实现了基于 Milvus 向量数据库的多维度岗位信息存储与检索系统。
支持从四个维度（基础要求、职业技能、职业素养、发展潜力）对岗位进行向量化，
并支持混合检索和过滤搜索。

主要功能：
- 批量存入岗位数据并进行多维度向量化
- 基于多向量的混合搜索（使用 RRF 算法排序）
- 支持学历、地点等条件过滤
- 数据的增删改查操作
"""

import os
import json
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Milvus 标准客户端（兼容 Docker 版）
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection, AnnSearchRequest, \
    RRFRanker

# Pydantic
from pydantic import BaseModel, Field, ConfigDict

# 阿里云 Embedding
from aliyun_embedding import AliyunEmbedding

# 加载环境变量
load_dotenv()


class JobVectorStore:
    """
    岗位向量存储类
    
    封装了与 Milvus 向量数据库的所有交互操作，支持多维度向量存储和检索。
    
    Attributes:
        embedder: 阿里云 Embedding 向量化工具
        collection_name: Milvus 集合名称
        dim: 向量维度
        host: Milvus 服务器地址
        port: Milvus 服务器端口
        collection: Milvus 集合对象
    """
    
    def __init__(self,
                 host: str = "192.168.3.128",  # Docker Milvus 服务器 IP
                 port: str = "19530",  # Docker Milvus 端口
                 collection_name: str = "jobs_multi_vector",
                 api_key: str = None,
                 dim: int = 1024):
        """
        初始化基于 Docker Milvus 的多维度向量存储系统
        
        Args:
            host: Milvus 服务器地址
            port: Milvus 服务器端口
            collection_name: 集合名称
            api_key: 阿里云 API 密钥
            dim: 向量维度（默认 1024，根据阿里云模型实际维度调整）
        """
        # 初始化阿里云 Embedding 工具
        self.embedder = AliyunEmbedding(api_key)
        self.collection_name = collection_name
        self.dim = dim
        self.host = host
        self.port = port
        self.collection = None

        # 1. 连接 Docker Milvus 服务器
        self._connect()

        # 2. 如果集合不存在，则创建
        if not utility.has_collection(collection_name):
            self._create_collection()
        else:
            # 集合已存在，直接加载
            self.collection = Collection(collection_name)

        print(f"✅ Milvus 向量库初始化完成：{host}:{port}")

    def _connect(self):
        """连接 Milvus 服务器"""
        try:
            connections.connect(
                alias="default",  # 连接别名，默认使用 "default"
                host=self.host,
                port=self.port,
                timeout=30  # 连接超时时间（秒）
            )
            print(f"✓ 已连接 Milvus 服务器 {self.host}:{self.port}")
        except Exception as e:
            print(f"✗ 连接失败：{e}")
            raise

    def _create_collection(self):
        """
        创建支持多向量和动态字段的集合
        
        集合结构：
        - id: 岗位唯一标识（主键）
        - education_level: 学历等级（0=不限, 1=专科, 2=本科, 3=硕士, 4=博士）
        - vec_basic: 基础要求维度向量
        - vec_skills: 职业技能维度向量
        - vec_literacy: 职业素养维度向量
        - vec_potential: 发展潜力维度向量
        - title: 岗位名称
        - company: 公司名称
        - location: 工作地点
        - salary: 薪资范围
        - raw_profiles: 原始岗位信息（JSON 格式）
        """
        # 定义字段
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),  # 主键
            FieldSchema(name="education_level", dtype=DataType.INT64),  # 学历等级（用于过滤）
            # 四个维度的向量字段
            FieldSchema(name="vec_basic", dtype=DataType.FLOAT_VECTOR, dim=self.dim),  # 基础要求
            FieldSchema(name="vec_skills", dtype=DataType.FLOAT_VECTOR, dim=self.dim),  # 职业技能
            FieldSchema(name="vec_literacy", dtype=DataType.FLOAT_VECTOR, dim=self.dim),  # 职业素养
            FieldSchema(name="vec_potential", dtype=DataType.FLOAT_VECTOR, dim=self.dim),  # 发展潜力
            # 岗位基本信息字段
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),  # 岗位名称
            FieldSchema(name="company", dtype=DataType.VARCHAR, max_length=500),  # 公司名称
            FieldSchema(name="location", dtype=DataType.VARCHAR, max_length=200),  # 工作地点
            FieldSchema(name="salary", dtype=DataType.VARCHAR, max_length=200),  # 薪资
            FieldSchema(name="raw_profiles", dtype=DataType.VARCHAR, max_length=65535)  # 完整的岗位信息
        ]

        # 创建 Schema（集合结构定义）
        schema = CollectionSchema(
            fields=fields,
            description="多维度岗位向量存储",
            enable_dynamic_field=True  # 启用动态字段，允许后续添加新字段
        )

        # 创建集合
        self.collection = Collection(self.collection_name, schema)
        print(f"✓ 集合创建成功：{self.collection_name}")

        # 创建索引（每个向量字段都需要索引才能进行高效搜索）
        vector_fields = ["vec_basic", "vec_skills", "vec_literacy", "vec_potential"]
        for field in vector_fields:
            index_params = {
                "index_type": "IVF_FLAT",  # 索引类型：IVF_FLAT（适合中等规模数据）
                "metric_type": "COSINE",  # 相似度度量：余弦距离
                "params": {"nlist": 128}  # IVF 参数：聚类中心数量
            }
            self.collection.create_index(field_name=field, index_params=index_params)
            print(f"✓ 索引创建成功：{field}")

        # 加载集合到内存（必须加载后才能搜索）
        self.collection.load()
        print(f"✅ 集合已加载到内存")

    def _map_education(self, edu_str: str) -> int:
        """
        将学历字符串映射为数值等级
        
        Args:
            edu_str: 学历字符串，如 "本科"、"硕士"、"博士" 等
        
        Returns:
            int: 学历等级（0=不限, 1=专科, 2=本科, 3=硕士, 4=博士）
        """
        if not edu_str:
            return 0
        if "博士" in str(edu_str):
            return 4
        if "硕士" in str(edu_str) or "研究生" in str(edu_str):
            return 3
        if "本科" in str(edu_str):
            return 2
        if "专科" in str(edu_str) or "大专" in str(edu_str):
            return 1
        return 0

    def add_jobs(self, jobs: List[Dict], batch_size: int = 10, delay: float = 0.3):
        """
        批量存入多维度岗位数据
        
        对每个岗位的四个维度（基础要求、职业技能、职业素养、发展潜力）分别进行向量化，
        然后存入 Milvus 数据库。
        
        Args:
            jobs: 岗位数据列表，每个岗位包含 id、title、company、location、salary、profiles 等字段
            batch_size: 批处理大小，控制每次向量化处理的数据量
            delay: 批次间延迟（秒），避免 API 限流
        """
        if not jobs:
            print("❌ 没有数据需要存入")
            return

        total_inserted = 0

        # 分批处理数据
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i:i + batch_size]

            # 提取四个维度的文本
            texts_basic = [str(job.get('profiles', {}).get('基础要求', '')) for job in batch]
            texts_skills = [str(job.get('profiles', {}).get('职业技能', '')) for job in batch]
            texts_literacy = [str(job.get('profiles', {}).get('职业素养', '')) for job in batch]
            texts_potential = [str(job.get('profiles', {}).get('发展潜力', '')) for job in batch]

            # 生成向量（使用阿里云 Embedding API）
            try:
                # 对四个维度分别进行向量化
                emb_basic = self.embedder.get_embeddings_batch(texts_basic, batch_size=batch_size, delay=delay)
                emb_skills = self.embedder.get_embeddings_batch(texts_skills, batch_size=batch_size, delay=delay)
                emb_literacy = self.embedder.get_embeddings_batch(texts_literacy, batch_size=batch_size, delay=delay)
                emb_potential = self.embedder.get_embeddings_batch(texts_potential, batch_size=batch_size, delay=delay)
            except Exception as e:
                print(f"✗ 向量化失败：{e}")
                continue

            # 组装插入数据
            insert_data = []
            for idx, job in enumerate(batch):
                # 提取学历要求并映射为等级
                edu_text = job.get('profiles', {}).get('基础要求', {}).get('学历要求', '')
                edu_level = self._map_education(edu_text)

                # 构建实体对象
                entity = {
                    "id": int(job['id']),
                    "education_level": edu_level,
                    # 四个维度的向量（如果向量化失败则使用零向量）
                    "vec_basic": emb_basic[idx] if idx < len(emb_basic) else [0.0] * self.dim,
                    "vec_skills": emb_skills[idx] if idx < len(emb_skills) else [0.0] * self.dim,
                    "vec_literacy": emb_literacy[idx] if idx < len(emb_literacy) else [0.0] * self.dim,
                    "vec_potential": emb_potential[idx] if idx < len(emb_potential) else [0.0] * self.dim,
                    # 岗位基本信息（截断至最大长度）
                    "title": str(job.get('title', ''))[:500],
                    "company": str(job.get('company', ''))[:500],
                    "location": str(job.get('location', ''))[:200],
                    "salary": str(job.get('salary', ''))[:200],
                    # 完整的岗位信息（JSON 格式）
                    "raw_profiles": json.dumps(job.get('profiles', {}), ensure_ascii=False)[:65535]
                }
                insert_data.append(entity)

            # 插入数据到 Milvus
            if insert_data:
                try:
                    self.collection.insert(insert_data)
                    self.collection.flush()  # 刷新数据到磁盘
                    total_inserted += len(insert_data)
                    print(f"✓ 批次 {i // batch_size + 1} 完成，已插入 {total_inserted} 条")
                except Exception as e:
                    print(f"✗ 插入失败：{e}")

            # 避免 API 限流（批次间延迟）
            if delay > 0:
                time.sleep(delay)

        print(f"✅ 总共存入 {total_inserted} 条数据")

    def search_jobs(self, query: str, top_k: int = 5, min_education: int = 0, location: str = None) -> List[Dict]:
        """
        多向量混合搜索
        
        使用四个维度的向量同时进行搜索，通过 RRF（Reciprocal Rank Fusion）算法融合结果，
        支持学历和地点过滤。
        
        Args:
            query: 搜索查询文本
            top_k: 返回结果数量
            min_education: 最低学历等级（0=不限, 1=专科, 2=本科, 3=硕士, 4=博士）
            location: 工作地点过滤条件（可选）
        
        Returns:
            List[Dict]: 搜索结果列表，每个结果包含岗位信息和相关性得分
        """
        # 生成查询向量
        try:
            query_vector = self.embedder.get_embedding_with_retry(query, max_retries=3)
            if not query_vector:
                print("✗ 向量化失败")
                return []
        except Exception as e:
            print(f"✗ 向量化异常：{e}")
            return []

        # 构建过滤表达式
        expr_parts = [f"education_level >= {min_education}"]  # 学历过滤
        if location:
            expr_parts.append(f"location == '{location}'")  # 地点过滤
        filter_expr = " and ".join(expr_parts)

        # 构建四路搜索请求（每个维度一路）
        search_requests = []
        for vec_field in ["vec_basic", "vec_skills", "vec_literacy", "vec_potential"]:
            req = AnnSearchRequest(
                data=[query_vector],  # 查询向量
                anns_field=vec_field,  # 搜索的向量字段
                param={"metric_type": "COSINE", "params": {"nprobe": 10}},  # 搜索参数
                limit=top_k * 2,  # 每路多取一些，RRF 后再筛选
                expr=filter_expr  # 过滤表达式
            )
            search_requests.append(req)

        # 执行混合搜索
        try:
            results = self.collection.hybrid_search(
                reqs=search_requests,  # 四路搜索请求
                rerank=RRFRanker(),  # 使用 RRF 算法对结果进行重排序
                limit=top_k,  # 最终返回数量
                output_fields=["id", "title", "company", "location", "salary", "education_level", "raw_profiles"]
            )
        except Exception as e:
            print(f"✗ 搜索失败：{e}")
            return []

        # 格式化结果
        job_list = []
        for hits in results:
            for hit in hits:
                job_list.append({
                    'id': hit.entity.get('id'),
                    'title': hit.entity.get('title'),
                    'company': hit.entity.get('company'),
                    'location': hit.entity.get('location'),
                    'salary': hit.entity.get('salary'),
                    'education_level': hit.entity.get('education_level'),
                    'score': hit.score,  # RRF 综合得分
                    'profiles': json.loads(hit.entity.get('raw_profiles', '{}'))  # 解析完整的岗位信息
                })

        return job_list

    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            Dict: 包含总数据量、集合名称和状态信息的字典
        """
        try:
            self.collection.flush()
            return {
                "total_count": self.collection.num_entities,  # 总数据量
                "collection_name": self.collection_name,
                "status": "healthy"
            }
        except Exception as e:
            return {
                "total_count": 0,
                "collection_name": self.collection_name,
                "status": f"error: {e}"
            }

    def clear_all(self):
        """
        清空数据库
        
        删除现有集合并重新创建（用于测试或重置）
        """
        try:
            if utility.has_collection(self.collection_name):
                utility.drop_collection(self.collection_name)
                print(f"✓ 已删除集合：{self.collection_name}")

            # 重新创建集合
            self._create_collection()
            print("✅ 数据库已清空并重建")
        except Exception as e:
            print(f"✗ 清空失败：{e}")
            raise

    def delete_job(self, job_id: int):
        """
        删除单个岗位
        
        Args:
            job_id: 岗位 ID
        """
        try:
            expr = f"id == {job_id}"
            self.collection.delete(expr)
            self.collection.flush()
            print(f"✅ 已删除岗位 ID: {job_id}")
        except Exception as e:
            print(f"✗ 删除失败：{e}")

    def update_job(self, job: Dict):
        """
        更新岗位数据（删除后重新插入）
        
        Args:
            job: 更新后的岗位数据
        """
        job_id = int(job['id'])
        self.delete_job(job_id)
        self.add_jobs([job])
        print(f"✅ 已更新岗位 ID: {job_id}")

    def close(self):
        """关闭与 Milvus 的连接"""
        try:
            connections.disconnect("default")
            print("✓ 已断开 Milvus 连接")
        except:
            pass


# ============ 测试代码 ============
if __name__ == "__main__":
    """
    测试代码
    
    演示了 JobVectorStore 的主要功能：
    1. 初始化连接
    2. 清空并重建数据库
    3. 批量插入测试数据
    4. 查询统计信息
    5. 执行混合搜索
    6. 关闭连接
    """
    # 初始化
    store = JobVectorStore(
        host="192.168.3.128",  # 你的 Milvus 服务器 IP
        port="19530",
        dim=1024  # 根据阿里云模型实际维度调整
    )

    # 清空重建（测试用）
    store.clear_all()

    # 测试数据
    test_jobs = [
        {
            "id": 1,
            "title": "Java 后端工程师",
            "company": "阿里巴巴",
            "location": "北京",
            "salary": "20-40K",
            "profiles": {
                "基础要求": {"学历要求": "本科", "工作年限": "3-5 年"},
                "职业技能": {"核心专业技能": "Java, Spring Boot, MySQL, Redis", "语言能力": "CET4"},
                "职业素养": {"沟通能力": "良好", "团队协作": "优秀"},
                "发展潜力": {"学习能力": "极强", "适应性": "强"}
            }
        },
        {
            "id": 2,
            "title": "算法研究员",
            "company": "百度",
            "location": "北京",
            "salary": "40-80K",
            "profiles": {
                "基础要求": {"学历要求": "博士", "工作年限": "不限"},
                "职业技能": {"核心专业技能": "PyTorch, NLP, RAG, Transformer", "语言能力": "CET6"},
                "职业素养": {"沟通能力": "正常", "逻辑思维": "极强"},
                "发展潜力": {"创新能力": "前沿学术研究级别", "适应性": "一般"}
            }
        },
        {
            "id": 3,
            "title": "前端开发工程师",
            "company": "腾讯",
            "location": "深圳",
            "salary": "15-30K",
            "profiles": {
                "基础要求": {"学历要求": "本科", "工作年限": "2-4 年"},
                "职业技能": {"核心专业技能": "Vue, React, TypeScript, Webpack", "语言能力": "CET4"},
                "职业素养": {"沟通能力": "优秀", "团队协作": "良好"},
                "发展潜力": {"学习能力": "强", "适应性": "极强"}
            }
        }
    ]

    # 插入数据
    print("\n=== 插入测试数据 ===")
    store.add_jobs(test_jobs, batch_size=2, delay=0.5)

    # 查看统计
    print("\n=== 数据库统计 ===")
    stats = store.get_stats()
    print(json.dumps(stats, ensure_ascii=False, indent=2))

    # 搜索测试
    print("\n=== 多向量+学历过滤搜索测试 ===")
    results = store.search_jobs(
        query="精通大型后端架构和数据库优化",
        top_k=3,
        min_education=2,  # 本科及以上
        location="北京"
    )

    for job in results:
        print(f"\nID:{job['id']} | {job['title']} ({job['company']})")
        print(f"  薪资:{job['salary']} | 地点:{job['location']} | 学历等级:{job['education_level']}")
        print(f"  RRF得分:{job['score']:.4f}")

    # 清理
    store.close()
    print("\n✅ 测试完成！")
