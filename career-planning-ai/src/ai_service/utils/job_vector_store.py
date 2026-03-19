import asyncio
import json


from pymilvus import (
    connections, FieldSchema, CollectionSchema, DataType, Collection, utility,
    AnnSearchRequest, WeightedRanker
)
from sympy import false

from ai_service.models.struct_job_txt import JDAnalysisResult
from ai_service.models.struct_txt import StudentProfile
from ai_service.utils.aliyun_embedding import AliyunEmbedding
from config import settings


class JobVectorStore:
    def __init__(self, host="192.168.3.128", port="19530", dim=1024,collection_name="job_matching_profiles" ,api_key=settings.llm.api_key.get_secret_value()):
        self.host = host
        self.port = port
        self.dim = dim
        self.collection_name = collection_name
        self.embedder = AliyunEmbedding(api_key=api_key)
        
        # 1. 连接 Milvus
        connections.connect("default", host=self.host, port=self.port)
        print(f"✅ 已连接到 Milvus: {self.host}:{self.port}")
        
        # 2. 初始化或加载 Collection
        self.collection = self._init_collection()

    def _init_collection(self):
        """定义 Milvus 集合的 Schema，包含标量字段和 4 个向量字段"""
        if utility.has_collection(self.collection_name):
            collection = Collection(self.collection_name)
            collection.load()
            return collection

        fields = [
            # 主键
            FieldSchema(name="job_id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
            # 标量：用于 >= 过滤的数值等级
            FieldSchema(name="degree_level", dtype=DataType.INT64, description="学历等级"),
            FieldSchema(name="exp_level", dtype=DataType.INT64, description="经验等级"),
            # 原始数据
            FieldSchema(name="raw_data", dtype=DataType.JSON, description="岗位完整原始数据"),
            # 四个维度的向量
            FieldSchema(name="vec_basic", dtype=DataType.FLOAT_VECTOR, dim=self.dim, description="基础要求向量"),
            FieldSchema(name="vec_skills", dtype=DataType.FLOAT_VECTOR, dim=self.dim, description="职业技能向量"),
            FieldSchema(name="vec_literacy", dtype=DataType.FLOAT_VECTOR, dim=self.dim, description="职业素养向量"),
            FieldSchema(name="vec_potential", dtype=DataType.FLOAT_VECTOR, dim=self.dim, description="发展潜力向量")
        ]
        
        schema = CollectionSchema(fields, description="多维岗位画像库")
        collection = Collection(self.collection_name, schema)

        # 为四个向量字段分别创建索引
        index_params = {"metric_type": "COSINE", "index_type": "HNSW", "params": {"M": 8, "efConstruction": 64}}
        collection.create_index(field_name="vec_basic", index_params=index_params)
        collection.create_index(field_name="vec_skills", index_params=index_params)
        collection.create_index(field_name="vec_literacy", index_params=index_params)
        collection.create_index(field_name="vec_potential", index_params=index_params)
        
        collection.load()
        print(f"✅ Collection '{self.collection_name}' 初始化并加载完成")
        return collection

    # ================= 工具方法：等级映射 =================
    @staticmethod
    def map_degree_to_level(degree_str: str) -> int:
        """学历映射为数值，数值越大要求越高。用户等级 >= 岗位等级 即可匹配"""
        if not degree_str: return 0
        degree_str = degree_str.lower()
        if "博士" in degree_str: return 4
        if "硕士" in degree_str or "研究生" in degree_str: return 3
        if "本科" in degree_str: return 2
        if "专科" in degree_str or "大专" in degree_str: return 1
        return 0  # 不限

    @staticmethod
    def map_exp_to_level(exp_str: str) -> int:
        """经验映射为数值"""
        if not exp_str: return 0
        if "5" in exp_str: return 3        # 5年以上 / 5-10年
        if "3" in exp_str: return 2        # 3-5年
        if "1" in exp_str or "2" in exp_str: return 1  # 1-3年
        return 0                           # 应届/不限

    @staticmethod
    def obj_to_text(obj) -> str:
        """将 Pydantic 模型的子模块转化为拼接文本，用于生成 Embedding"""
        if isinstance(obj, dict):
            return " ".join([f"{k}:{v}" for k, v in obj.items() if v])
        return obj.model_dump_json(by_alias=True)

    # ================= 入库方法 =================
    async def insert_job_async(self, jd_result: JDAnalysisResult):
        """
        异步版本的入库方法
        使用 asyncio.to_thread 将同步阻塞操作放入线程池
        """
        # 将整个同步入库逻辑放入线程池
        # 这样不会阻塞 FastAPI 的主事件循环
        await asyncio.to_thread(self.insert_job, jd_result)

    def insert_job(self, jd_result: JDAnalysisResult):
        """将岗位画像存入 Milvus"""
        profiles = jd_result.profiles
        
        # 1. 标量字段解析
        degree_level = self.map_degree_to_level(profiles.basic_requirements.degree)
        exp_level = self.map_exp_to_level(profiles.basic_requirements.experience_years)
        
        # 2. 获取四个维度的文本并向量化
        # 使用 embedder 获取向量，如果网络不稳定内部自带重试机制
        vec_basic = self.embedder.get_embedding_with_retry(self.obj_to_text(profiles.basic_requirements))
        vec_skills = self.embedder.get_embedding_with_retry(self.obj_to_text(profiles.professional_skills))
        vec_literacy = self.embedder.get_embedding_with_retry(self.obj_to_text(profiles.professional_literacy))
        vec_potential = self.embedder.get_embedding_with_retry(self.obj_to_text(profiles.development_potential))
        
        if not all([vec_basic, vec_skills, vec_literacy, vec_potential]):
            print(f"❌ 职位 {jd_result.job_id} 向量化失败，跳过入库。")
            return

        raw_data = jd_result.model_dump(by_alias=False)
        # 3. 组装数据并插入
        data = [
            [jd_result.job_id],      # job_id
            [degree_level],          # degree_level
            [exp_level],             # exp_level
            [raw_data],              # raw_data  原json格式数据
            [vec_basic],             # vec_basic
            [vec_skills],            # vec_skills
            [vec_literacy],          # vec_literacy
            [vec_potential]          # vec_potential
        ]
        
        res = self.collection.upsert(data)
        self.collection.flush()
        print(f"✅ 职位 {jd_result.job_name} ({jd_result.job_id}) 成功入库！")

    # ================= 重置方法 =================
    def reset_collection(self):
        self.collection.drop()
        self.collection = self._init_collection()

    # 方式 3：仅删除集合
    def drop_collection(self):
        self.collection.drop()

    # 方式 4：查看集合信息
    def get_collection_info(self):
        self.collection.describe()

    def delete_job(self, job_id: str):
        """删除指定岗位"""
        self.collection.delete(expr=f"job_id = '{job_id}'")
        self.collection.flush()
        print(f"✅ 职位 {job_id} 成功删除！")

    # ================= 匹配方法 =================
    def match_jobs_for_student(self, student: StudentProfile, top_k: int = 20,nums:[float,float,float,float]=[0.2,0.5,0.2,0.1]):
        """
        根据用户画像匹配最合适的 Top K 岗位
        学历和工作年限要求：用户等级 >= 岗位等级
        """
        # 1. 计算用户的标量等级
        user_degree_level = self.map_degree_to_level(student.basic_info.degree)
        user_exp_level = self.map_exp_to_level(str(student.basic_info.internship_months))  # 简化处理，可按月数转换为年限规则

        # 2. 构造标量过滤表达式 (Expr)
        # 逻辑：岗位要求的学历 <= 用户的学历，且岗位要求的经验 <= 用户的经验
        filter_expr = f"degree_level <= {user_degree_level} && exp_level <= {user_exp_level}"

        # 3. 将用户的四个维度向量化 (与岗位侧对齐)
        user_vec_basic = self.embedder.get_embedding_with_retry(self.obj_to_text(student.basic_info))
        user_vec_skills = self.embedder.get_embedding_with_retry(self.obj_to_text(student.skills))
        user_vec_literacy = self.embedder.get_embedding_with_retry(self.obj_to_text(student.literacy))
        user_vec_potential = self.embedder.get_embedding_with_retry(self.obj_to_text(student.potential))

        if not all([user_vec_basic, user_vec_skills, user_vec_literacy, user_vec_potential]):
            print("❌ 用户画像向量化失败，无法进行匹配。")
            return []

        # 4. 构建多路召回请求 (Multi-vector Search)
        search_params = {"metric_type": "COSINE", "params": {"ef": 64}}

        req_basic = AnnSearchRequest([user_vec_basic], "vec_basic", search_params, limit=top_k, expr=filter_expr)
        req_skills = AnnSearchRequest([user_vec_skills], "vec_skills", search_params, limit=top_k, expr=filter_expr)
        req_literacy = AnnSearchRequest([user_vec_literacy], "vec_literacy", search_params, limit=top_k,
                                        expr=filter_expr)
        req_potential = AnnSearchRequest([user_vec_potential], "vec_potential", search_params, limit=top_k,
                                         expr=filter_expr)

        # 5. 执行混合检索 (Hybrid Search)
        # 可以通过 WeightedRanker 为不同维度分配权重。例如：技能占 40%，素养占 20%，潜力占 20%，基础占 20%
        ranker = WeightedRanker(*nums)

        results = self.collection.hybrid_search(
            reqs=[req_basic, req_skills, req_literacy, req_potential],
            rerank=ranker,
            limit=top_k,
            output_fields=["job_id", "raw_data"]  # 返回所需字段
        )

        # 6. 解析并返回结果
        matched_jobs = []
        for hits in results:
            for hit in hits:
                raw_data = hit.entity.get("raw_data")

                # 如果 raw_data 是字符串，解析为字典
                if isinstance(raw_data, str):
                    raw_data = json.loads(raw_data)

                matched_jobs.append({
                    "job_id": hit.entity.get("job_id"),
                    "score": hit.score,
                    "raw_data": raw_data
                })

        return matched_jobs


if __name__ == "__main__":
    from ai_service.models.struct_job_txt import JDAnalysisResult, Profiles, BasicRequirements, ProfessionalSkills, ProfessionalLiteracy, \
        DevelopmentPotential, JobAttributes

    # 岗位 1：高级 AI 算法工程师
    jd_ai_researcher = JDAnalysisResult(
        job_id="job_001",
        job_name="高级AI算法工程师",
        profiles=Profiles(
            基础要求=BasicRequirements(学历要求="本科", 专业背景="计算机类", 证书要求="无", 实习经历要求="优先",
                                       工作年限="", 特殊要求="无"),
            职业技能=ProfessionalSkills(核心专业技能="PyTorch, Transformer, LLM, RAG",
                                        工具与平台能力="Linux, Docker, NVIDIA Triton", 行业_Domain_知识="人工智能",
                                        语言能力="CET6", 项目经验="具备大型语言模型微调经验"),
            职业素养=ProfessionalLiteracy(沟通能力="中", 团队协作="高", 抗压能力="高", 逻辑思维="极高",
                                          责任心与职业道德="高"),
            发展潜力=DevelopmentPotential(学习能力="极高", 创新能力="极高", 领导力潜质="中", 职业倾向性="研究",
                                          适应性="高"),
            岗位属性=JobAttributes(薪资竞争力="高", 所属行业="互联网", 垂直晋升路径="算法专家->科学家",
                                   前置岗位要求="深度学习基础", 横向转岗方向="后端架构,数据科学", 社会需求度="高",
                                   行业发展趋势="朝阳")
        )
    )

    # 岗位 2：初级前端开发工程师
    jd_web_dev = JDAnalysisResult(
        job_id="job_002",
        job_name="前端开发工程师",
        profiles=Profiles(
            基础要求=BasicRequirements(学历要求="本科", 专业背景="不限", 证书要求="无", 实习经历要求="无",
                                       工作年限="应届", 特殊要求="无"),
            职业技能=ProfessionalSkills(核心专业技能="Vue3, TypeScript, CSS3", 工具与平台能力="Webpack, Vite, Git",
                                        行业_Domain_知识="互联网", 语言能力="CET4", 项目经验="有完整的项目上线经验"),
            职业素养=ProfessionalLiteracy(沟通能力="高", 团队协作="高", 抗压能力="中", 逻辑思维="中",
                                          责任心与职业道德="高"),
            发展潜力=DevelopmentPotential(学习能力="高", 创新能力="中", 领导力潜质="低", 职业倾向性="技术",
                                          适应性="高"),
            岗位属性=JobAttributes(薪资竞争力="中", 所属行业="互联网", 垂直晋升路径="中级前端->资深前端",
                                   前置岗位要求="HTML/JS基础", 横向转岗方向="UI设计,产品经理,Node后端", 社会需求度="高",
                                   行业发展趋势="平稳")
        )
    )

    job_list = [jd_ai_researcher, jd_web_dev]

    from ai_service.models.struct_txt import StudentProfile, BasicRequirements, ProfessionalSkills, ProfessionalLiteracy, DevelopmentPotential, SpecialConstraints, PracticalExperience

    # 学生：一位精通 Vue3 和 Python AI 组件的软件工程大四学生
    student_test_data = StudentProfile(
        基础信息=BasicRequirements(学历="本科",专业背景="软件工程", 证书=["CET-6", "计算机二级"],实习时长=6,求职状态="应届生"),
        专业技能=ProfessionalSkills(
            核心专业技能=["Vue3", "Java", "Python", "RAG", "LLM"," TypeScript"," CSS3"],
            工具与平台能力=["Milvus", "MySQL", "SQLAlchemy", "Git","Webpack"," Vite"],
            行业领域知识评分=4,
            语言能力=["CET-6 流利"],
            项目经验丰富度=4
        ),
        职业素养=ProfessionalLiteracy(
            沟通能力=4,
            团队协作=5,
            抗压能力=4,
            逻辑思维=5,
            责任心与职业道德=5
        ),
        发展潜力=DevelopmentPotential(
            学习能力=5,
            创新能力=4,
            领导力潜质=3,
            职业倾向性="技术型",
            环境适应性=4
        ),
        个人限制=SpecialConstraints(
            生理限制="无",
            价值观限制="不接受博彩行业",
            环境限制="无",
            时间习惯限制="无",
            其他特殊要求="希望在西安或北京工作"
        ),
        实践详情=PracticalExperience(
            项目经历详情="开发了一个基于 AI 的大学生职业规划 Agent 项目，负责全栈开发。",
            实习经历详情="在某科技公司实习 6 个月，负责后端数据库优化。",
            campus_activities="校学生会技术部部长",
            竞赛获奖详情="中国高校计算机大赛一等奖"
        )
    )

    # 1. 初始化
    store = JobVectorStore()
    # # store.reset_collection()
    # # 2. 模拟岗位入库
    # for jd in job_list:
    #     store.insert_job(jd)

    # 3. 执行匹配
    print("\n--- 正在为该学生匹配最合适的岗位 ---")
    matches = store.match_jobs_for_student(student_test_data, top_k=20)
    for match in matches:
        print(f"匹配结果：{match['job_id']} (得分: {match['score']:.2f})")
        print(f"岗位详情：{match['raw_data']}")
        print("-" * 50)
