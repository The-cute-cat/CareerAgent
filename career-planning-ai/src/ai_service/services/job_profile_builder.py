#通过岗位元信息构建岗位画像
import os
import json
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, ConfigDict
from langchain_community.chat_models import ChatTongyi

load_dotenv()

# ==========================================
# 1. 定义 Pydantic 数据模型 (对应 JSON Schema)
# ==========================================

class BasicRequirements(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    学历要求:str = Field(alias="学历要求", description="专科/本科/硕士/博士/不限")
    专业背景:str = Field(alias="专业背景", description="计算机类/数学类/不限等")
    证书要求:str = Field(alias="证书要求", description="必需/优先/无")
    实习经历要求:str = Field(alias="实习经历要求", description="必需/优先/无 + 月数等")
    工作年限:str = Field(alias="工作年限", description="应届/1-3 年/3-5 年/5 年+等")
    特殊要求:str = Field(alias="特殊要求", description="等")

class ProfessionalSkills(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    核心专业技能:str = Field(alias="核心专业技能", description="JD 关键词提取")
    工具与平台能力:str = Field(alias="工具与平台能力", description="JD 关键词提取")
    行业_Domain_知识:str = Field(alias="行业 Domain 知识", description="JD 文本分析")
    语言能力:str = Field(alias="语言能力", description="CET4/CET6/托福/雅思等")
    项目经验:str = Field(alias="项目经验", description="JD 文本分析")

class ProfessionalLiteracy(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    沟通能力:str = Field(alias="沟通能力", description="JD 软性要求提取")
    团队协作:str = Field(alias="团队协作", description="JD 软性要求提取")
    抗压能力:str = Field(alias="抗压能力", description="JD 软性要求提取")
    逻辑思维:str = Field(alias="逻辑思维", description="JD 软性要求提取")
    责任心与职业道德:str = Field(alias="责任心与职业道德", description="JD 软性要求提取")

class DevelopmentPotential(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    学习能力:str = Field(alias="学习能力", description="JD 文本分析")
    创新能力:str = Field(alias="创新能力", description="JD 文本分析")
    领导力潜质:str = Field(alias="领导力潜质", description="JD 文本分析")
    职业倾向性:str = Field(alias="职业倾向性", description="管理/技术/创业/研究等")
    适应性:str = Field(alias="适应性", description="JD 文本分析")

class JobAttributes(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    薪资竞争力:str = Field(alias="薪资竞争力", description="低/中/高")
    工作地点:str = Field(alias="工作地点", description="城市分级")
    企业性质:str = Field(alias="企业性质", description="国企/民企/外企/初创等")
    公司规模:str = Field(alias="公司规模", description="大型/中型/小型")
    所属行业:str = Field(alias="所属行业", description="互联网/金融/制造等")
    垂直晋升路径:str = Field(alias="垂直晋升路径", description="文本列表 (如:初级->资深->组长)")
    前置岗位要求:str = Field(alias="前置岗位要求", description="文本列表")
    横向转岗方向:str = Field(alias="横向转岗方向", description="文本列表（至少 5 个）")
    社会需求度:str = Field(alias="社会需求度", description="高/中/低")
    行业发展趋势:str = Field(alias="行业发展趋势", description="朝阳/平稳/萎缩等")
    工作强度与节奏:str = Field(alias="工作强度与节奏", description="大小周/双休/弹性/高频出差")
    核心产出_KPI: str = Field(alias="核心产出/KPI", description="文本")
    培训与带教机制:str = Field(alias="培训与带教机制", description="完善/一般/无等")

class Profiles(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    基础要求:BasicRequirements = Field(alias="基础要求")
    职业技能:ProfessionalSkills = Field(alias="职业技能")
    职业素养:ProfessionalLiteracy = Field(alias="职业素养")
    发展潜力:DevelopmentPotential = Field(alias="发展潜力")
    岗位属性:JobAttributes = Field(alias="岗位属性")

class JDAnalysisResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    job_id: str = Field(description="职位ID")
    job_name: str = Field(description="职位名称")
    profiles: Profiles = Field(alias="profiles", description="岗位详细画像")


# 2. 定义 Prompt 模板，可以修改条件

SYSTEM_PROMPT = """
你是一位资深的人力资源数据分析专家及职业图谱构建师。
你的任务是从给定的职位描述（JD）文本中，提取关键信息并推断岗位属性，最终输出符合 JSON Schema 的结构化数据。

# 约束与规则
1. **格式严格**:必须输出合法的 JSON 格式，不要包含 Markdown 代码块标记。
2. **提取原则**:
   - 基础信息优先从 JD 原文提取。
   - "职业技能",优先从 JD 原文提取,若 JD 中未明确提及，则基于行业通用知识进行合理推断或填充字符串 "未提及"。
   - "职业素养" 、"发展潜力"中的软性要求，若 JD 中未明确提及，则基于行业通用知识进行合理推断或填充字符串 "未提及"。
   - "岗位属性" 中的推断类字段（如晋升路径、行业趋势），若 JD 未明确，请基于行业通用知识进行合理推断。
3. **缺失处理**:若某字段在 JD 中完全未提及且无法合理推断，请填充字符串 "未提及"。
4. **语言**:所有字段值请使用简体中文。
5. **字段对应**:请严格对应输出 Schema 中的字段名称（包括中文键名）。
"""

USER_PROMPT = """
请分析以下职位描述（JD）文本:

{jd_text}
"""

# ==========================================
# 3. 封装调用函数
# ==========================================

def analyze_job_description(jd_text: str, api_key: Optional[str] = None, model_name: str = "qwq-plus-latest") -> dict:
    """
    使用 LangChain 调用大模型分析 JD 文本并返回结构化 JSON 数据

    Args:
        jd_text (str): 原始的职位描述文本
        api_key (str, optional): API Key，若不传则读取环境变量 LLM__API_KEY
        model_name (str, optional): 模型名称，默认 gpt-3.5-turbo

    Returns:
        dict: 解析后的字典数据
    """
    # 1. 初始化 LLM
    if not api_key:
        api_key = os.getenv("LLM__API_KEY")

    if not api_key:
        raise ValueError("请提供 API Key 或设置环境变量 LLM__API_KEY")

    llm = ChatTongyi(
        api_key=api_key,
        model=model_name,
        temperature=0.1,  # 低温度以保证输出稳定性
        streaming=True  # 启用流式模式（该模型必需）
    )

    # 2. 初始化输出解析器 (绑定 Pydantic Schema)
    parser = PydanticOutputParser(pydantic_object=JDAnalysisResult)

    # 3. 构建 Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT + "\n\n# 输出格式说明\n{format_instructions}"),
        ("user", USER_PROMPT)
    ])

    # 4. 注入格式指令
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())

    # 5. 构建链 (Chain)
    chain = prompt | llm | parser

    try:
        # 6. 执行调用
        result = chain.invoke({"jd_text": jd_text})

        # 7. 转换为普通字典 (方便后续处理)
        # model_dump() 是 Pydantic V2 的方法，如果是 V1 请用 .dict()
        return result.model_dump(by_alias=True)

    except Exception as e:
        print(f"解析错误:{e}")
        # 如果解析失败，可以尝试返回原始文本或重试逻辑
        return {"error": str(e), "raw_text": jd_text}

if __name__ == "__main__":
    # 模拟一段 JD 文本
    sample_jd = """
    职位:APP推广
   岗位职责:1.负责推广公司产品，吸引新用户下载并使用。2.分析市场趋势，找到合适的推广区域。3.与团队合作，完成推广任务。任职要求：1.具有良好的沟通能力和团队合作精神。2.能够快速适应工作环境，学习新知识。3.对推广工作有热情，能够承受工作压力。
    """

    # 调用函数
    # 请确保你的环境变量中有 LLM__API_KEY，或者在这里传入 api_key="sk-..."
    try:
        result_data = analyze_job_description(sample_jd)

        # 打印结果
        print(json.dumps(result_data, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"运行失败:{e}")