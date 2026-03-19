# 人岗匹配的接口文档
import asyncio

from ai_service.services.Career_AnalystAgent import CareerAnalystAgent
from ai_service.utils.job_vector_store import JobVectorStore

if __name__ == "__main__":
    if __name__ == "__main__":
        from ai_service.models.struct_job_txt import JDAnalysisResult, Profiles, BasicRequirements, ProfessionalSkills, \
            ProfessionalLiteracy, \
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
                                            行业_Domain_知识="互联网", 语言能力="CET4",
                                            项目经验="有完整的项目上线经验"),
                职业素养=ProfessionalLiteracy(沟通能力="高", 团队协作="高", 抗压能力="中", 逻辑思维="中",
                                              责任心与职业道德="高"),
                发展潜力=DevelopmentPotential(学习能力="高", 创新能力="中", 领导力潜质="低", 职业倾向性="技术",
                                              适应性="高"),
                岗位属性=JobAttributes(薪资竞争力="中", 所属行业="互联网", 垂直晋升路径="中级前端->资深前端",
                                       前置岗位要求="HTML/JS基础", 横向转岗方向="UI设计,产品经理,Node后端",
                                       社会需求度="高",
                                       行业发展趋势="平稳")
            )
        )

        job_list = [jd_ai_researcher, jd_web_dev]

        from ai_service.models.struct_txt import StudentProfile, BasicRequirements, ProfessionalSkills, \
            ProfessionalLiteracy, DevelopmentPotential, SpecialConstraints, PracticalExperience

        # 学生：一位精通 Vue3 和 Python AI 组件的软件工程大四学生
        student_test_data = StudentProfile(
            基础信息=BasicRequirements(学历="本科", 专业背景="软件工程", 证书=["CET-6", "计算机二级"], 实习时长=6,
                                       求职状态="应届生"),
            专业技能=ProfessionalSkills(
                核心专业技能=["Vue3", "Java", "Python", "RAG", "LLM", " TypeScript", " CSS3"],
                工具与平台能力=["Milvus", "MySQL", "SQLAlchemy", "Git", "Webpack", " Vite"],
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
        agent = CareerAnalystAgent()
        # # store.reset_collection()
        # # 2. 模拟岗位入库
        # for jd in job_list:
        #     store.insert_job(jd)

        # 3. 执行匹配
        print("\n--- 正在为该学生匹配最合适的岗位 ---")
        matches = store.match_jobs_for_student(student_test_data, top_k=20)
        final_results = asyncio.run(agent.batch_analyze_async(student_test_data, matches, top_k=5))
        print("\n" + "=" * 50)
        for i, res in enumerate(final_results):
            # analysis = res['deep_analysis']
            # print(f"🏆 综合排名 Top {i + 1} | 岗位 ID: {res['job_id']}")
            # print(f"   - 门槛判定 (can_apply): {'✅ 通过' if analysis['can_apply'] else '❌ 拦截 (硬性条件不符)'}")
            # print(f"   - Agent 深度评分: {analysis['score']} 分")
            #
            # if not analysis['can_apply']:
            #     print(f"   - 🚫 核心缺失项: {', '.join(analysis['missing_key_skills'])}")
            #
            # print("   - 📊 核心差距矩阵 (Gap Matrix):")
            # for gap in analysis['gap_matrix']:
            #     print(f"     * [{gap['dimension']}] {gap['gap_analysis']}")
            #
            # print(f"   - 💡 专家建议: {analysis['actionable_advice']}")
            # print("-" * 50)

            print(str(res))
