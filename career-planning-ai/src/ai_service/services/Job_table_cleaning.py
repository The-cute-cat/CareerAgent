__all__ = ['filter_computer_jobs_excel','clean_job_excel','read_excel_to_jobinfo']
# 清洗招聘数据 Excel 文件（支持.xls 和.xlsx 格式）
#从文件中读取数据，并转换为JobInfo/字典实体对象列表
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import re


from ai_service.models.job_info import JobInfo  # 替换为您的实际导入路径
from pydantic import BaseModel, Field
import os
import pandas as pd
from typing import Optional, List, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.output_parsers import PydanticOutputParser

from config import LLM, settings


class JobClassificationItem(BaseModel):
    job_title: str = Field(description="岗位名称")
    is_computer_related: bool = Field(description="是否为计算机相关岗位，true 为是，false 为否")


class JobClassificationResult(BaseModel):
    """大模型返回的岗位分类结果列表"""
    classifications: List[JobClassificationItem] = Field(description="岗位分类列表")


# --- 删除与计算机不相干的岗位 ---
def filter_computer_jobs_excel(
        file_path: str,
        api_key: Optional[str] = None,
        model_name: str = settings.llm_model_name.model_name,
        batch_size: int = 50  # 每次发送给大模型的唯一岗位数量
) -> str:
    """
    读取 Excel -> 提取岗位 -> 去重 -> 大模型批量分类 -> 过滤原表 -> 覆盖保存

    Args:
        file_path (str): Excel 文件路径
        api_key (str, optional): API Key
        model_name (str, optional): 模型名称
        batch_size (int, optional): 大模型批量处理的岗位数量，防止 Token 超限

    Returns:
        str: 处理后的文件路径
    """
    # 1. 基础检查
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在：{file_path}")

    if not api_key:
        api_key = settings.llm.api_key.get_secret_value()
    if not api_key:
        raise ValueError("请提供 API Key 或设置环境变量 LLM__API_KEY")

    # 2. 读取 Excel 数据
    print(f"正在读取文件：{file_path} ...")
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        raise ValueError(f"读取 Excel 失败：{e}")

    if df.empty:
        print("表格为空，无需处理。")
        return file_path

    # 3. 识别岗位列
    target_col = None
    possible_names = ["岗位名称", "岗位", "职位名称", "职位", "Job Title", "Position"]
    # 标准化列名（去除空格）
    df.columns = df.columns.str.strip()

    for name in possible_names:
        if name in df.columns:
            target_col = name
            break

    if not target_col:
        raise ValueError(f"未找到岗位列，请确保包含以下列名之一：{possible_names}")

    # 4. 【核心步骤】提取岗位并去重
    print(f"正在提取唯一岗位名称（原数据行数：{len(df)}）...")
    # 转为字符串并去除首尾空格，去除空值
    unique_jobs = df[target_col].astype(str).str.strip().replace('', pd.NA).dropna().unique().tolist()
    print(f"去重后唯一岗位数量：{len(unique_jobs)}")

    if not unique_jobs:
        print("未发现有效岗位数据，直接返回。")
        return file_path

    # 5. 初始化 LLM 与解析器
    llm = ChatTongyi(
        api_key=api_key,
        model=model_name,
        temperature=0.1,
        streaming=True  # qwq-plus-latest 只支持流式模式
    )
    parser = PydanticOutputParser(pydantic_object=JobClassificationResult)

    # 6. 构建 Prompt 模板
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """你是一名资深人力资源数据清洗专家，专门负责从岗位名称中精准识别计算机/软件相关岗位。

## 🎯 核心任务
仅根据「岗位名称」文本，判断该岗位是否属于【计算机/软件】相关领域。

## 🔍 判断标准（满足任一即为"相关"）

### ✅ 明确相关的关键词（正向匹配）：
- 开发类：开发、工程师、程序、代码、架构、后端、前端、全栈、移动端、嵌入式、算法、AI、大模型
- 技术类：技术、技术支撑、研发、R&D、DevOps、SRE、运维、测试、测试开发、质量、效能
- 数据类：数据、大数据、数仓、ETL、数据挖掘、数据分析、BI、算法工程
- 基础设施：云、云计算、容器、K8s、Docker、网络、安全、信息安全、渗透、漏洞
- 产品/项目（技术向）：技术产品经理、研发项目经理、敏捷教练、Scrum Master
- 其他技术岗：爬虫、逆向、自动化、脚本、工具链、中间件、数据库、DBA

### ❌ 明确不相关的关键词（负向排除）：
- 纯业务/职能：销售、客服、行政、人事、财务、法务、采购、物流、仓管、司机、保安、保洁
- 纯运营/市场（无技术前缀）：运营、市场、推广、策划、文案、设计（除非带"UI/前端"等技术词）
- 传统行业岗位：教师、医生、护士、厨师、工人、技工、服务员、导购、顾问（除非明确带"技术"前缀）

### ⚠️ 模糊岗位处理策略（关键！）：
【高召回原则】当岗位名称存在歧义时，只要包含任何技术相关词汇，或无法100%确定无关，一律判定为 "related": true
示例：
- "技术顾问" → related: true（含"技术"）
- "IT支持" → related: true
- "系统专员" → related: true（"系统"在中文语境常指计算机系统）
- "项目助理" → related: false（无技术前缀）
- "技术支持工程师" → related: true

## 📦 输出格式（严格JSON，无额外内容）
{format_instructions}

## ⚡ 执行要求
1. 仅分析岗位名称，不推测职责、不依赖外部信息
2. 输出必须为合法JSON，字段：job_name(原名称), related(bool), reason(10字内简述)
3. 保持高召回：宁可误判为相关，绝不漏判真正技术岗
4. 不输出思考过程，只返回JSON结果"""),
        ("user",
         """请分析以下岗位列表，返回 JSON 格式结果。\n\n# 输出格式说明\n{format_instructions}\n\n# 待分析岗位列表\n{job_list}""")
    ])
    prompt = prompt_template.partial(format_instructions=parser.get_format_instructions())
    chain = prompt | llm | parser

    # 7. 【核心步骤】分批调用大模型进行分类
    # 避免一次性发送过多岗位导致 Token 超限或超时
    classification_map: Dict[str, bool] = {}
    total_batches = (len(unique_jobs) + batch_size - 1) // batch_size

    print(f"正在调用大模型进行分类（共分 {total_batches} 批）...")

    for i in range(0, len(unique_jobs), batch_size):
        batch_jobs = unique_jobs[i:i + batch_size]
        job_list_text = "\n".join([f"- {job}" for job in batch_jobs])

        max_retries = 3
        retry_count = 0
        success = False

        while retry_count < max_retries and not success:
            try:
                result = chain.invoke({"job_list": job_list_text})
                # 将结果存入映射表
                for item in result.classifications:
                    # 确保 key 也是.strip() 过的，方便后续匹配
                    classification_map[item.job_title.strip()] = item.is_computer_related
                print(f"  - 完成批次 {i // batch_size + 1}/{total_batches}")
                success = True
            except Exception as e:
                retry_count += 1
                import traceback
                error_type = type(e).__name__
                error_msg = str(e)
                error_detail = traceback.format_exc() if retry_count == max_retries else ""

                if retry_count < max_retries:
                    print(f"  - 批次 {i // batch_size + 1} 处理失败（重试 {retry_count}/{max_retries}）")
                    print(f"    错误类型: {error_type}")
                    print(f"    错误信息: {error_msg}")
                    import time
                    time.sleep(2)  # 等待2秒后重试
                else:
                    print(f"  - 批次 {i // batch_size + 1} 处理失败（已重试{max_retries}次）")
                    print(f"    错误类型: {error_type}")
                    print(f"    错误信息: {error_msg}")
                    if error_detail:
                        print(f"    详细堆栈:\n{error_detail}")
                    # 失败则该批次岗位默认视为非计算机岗（保守策略）
                    continue

    # 8. 【核心步骤】根据映射表过滤原 DataFrame
    print("正在应用过滤规则到原表格...")

    # 定义一个映射函数
    def map_job_status(job_title):
        if not isinstance(job_title, str):
            return False
        clean_title = job_title.strip()
        # 如果大模型判断过，返回判断结果；如果没判断过（漏网之鱼），默认返回 False
        return classification_map.get(clean_title, False)

    # 创建掩码
    mask = df[target_col].apply(map_job_status)
    filtered_df = df[mask]

    # 9. 覆盖保存原文件
    try:
        filtered_df.to_excel(file_path, index=False, engine='openpyxl')
        print(f"处理完成！原始行数：{len(df)}, 保留行数：{len(filtered_df)}, 删除行数：{len(df) - len(filtered_df)}")
        print(f"文件已覆盖保存：{file_path}")
        return file_path
    except Exception as e:
        raise RuntimeError(f"保存文件失败，请检查文件是否被占用：{e}")


# Excel表头到JobInfo字段的映射关系
EXCEL_TO_MODEL_MAPPING = {
    '岗位名称': 'job_title',
    '地址': 'location',
    '薪资范围': 'salary_range',
    '公司名称': 'company_name',
    '所属行业': 'industry',
    '公司规模': 'company_size',
    '公司类型': 'company_type',
    '岗位编码': 'job_code',
    '岗位详情': 'job_desc',
    '更新日期': 'updated_at',
    '公司详情': 'company_desc',
    '岗位来源地址': 'job_source_url',
}


def read_excel_to_jobinfo(
        file_path: str,
        sheet_name: Optional[str] = 0,
        skip_rows: int = 0
) -> List[JobInfo]:
    """
    读取Excel表格并生成JobInfo实体列表

    Args:
        file_path: Excel文件路径
        sheet_name: 工作表名称，默认为第一个工作表
        skip_rows: 跳过的行数（如果表头不在第一行）

    Returns:
        List[JobInfo]: JobInfo实体对象列表
    """
    # 验证文件路径
    if not Path(file_path).exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 读取Excel文件
    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        skiprows=skip_rows,
        dtype=str  # 默认全部读取为字符串，避免类型转换问题
    )

    # 检查必要的列是否存在
    available_columns = set(df.columns)
    missing_columns = set(EXCEL_TO_MODEL_MAPPING.keys()) - available_columns
    if missing_columns:
        print(f"警告: 以下列在Excel中未找到: {missing_columns}")

    job_info_list = []

    for idx, row in df.iterrows():
        try:
            job_info_data = {}

            # 遍历映射关系，将Excel数据转换为模型字段
            for excel_col, model_field in EXCEL_TO_MODEL_MAPPING.items():
                if excel_col in df.columns:
                    value = row.get(excel_col)

                    # 处理特殊字段类型
                    if model_field == 'updated_at' and pd.notna(value):
                        # 处理日期时间字段
                        try:
                            if isinstance(value, str):
                                for fmt in ['%Y年%m月%d日', '%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d']:
                                    try:
                                        value = datetime.strptime(value, fmt)
                                        break
                                    except ValueError:
                                        continue
                            elif isinstance(value, pd.Timestamp):
                                value = value.to_pydatetime()
                        except (ValueError, TypeError):
                            value = None
                    else:
                        # 其他字段转为字符串，处理NaN值
                        value = str(value).strip() if pd.notna(value) else None

                    job_info_data[model_field] = value

            # 创建JobInfo实例（不保存到数据库）
            job_info = JobInfo(**job_info_data)
            job_info_list.append(job_info)

        except Exception as e:
            print(f"第{idx + 2}行数据解析失败: {e}")
            continue

    return job_info_list


def read_excel_to_jobinfo_dict(
        file_path: str,
        sheet_name: Optional[str] = 0
) -> List[Dict[str, Any]]:
    """
    读取Excel表格并生成字典列表（不创建实体对象，更轻量）

    Args:
        file_path: Excel文件路径
        sheet_name: 工作表名称

    Returns:
        List[Dict]: 字典列表，可直接用于批量插入数据库
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)

    data_list = []
    for _, row in df.iterrows():
        record = {}

        for excel_col, model_field in EXCEL_TO_MODEL_MAPPING.items():
            if excel_col in df.columns:
                value = row.get(excel_col)

                if model_field == 'updated_at' and pd.notna(value):
                    try:
                        if isinstance(value, str):
                            for fmt in ['%Y年%m月%d日', '%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d']:
                                try:
                                    value = datetime.strptime(value, fmt)
                                    break
                                except ValueError:
                                    continue
                        else:
                            record[model_field] = None
                    except:
                        record[model_field] = None
                else:
                    record[model_field] = str(value).strip() if pd.notna(value) else None

        data_list.append(record)

    return data_list


def clean_job_excel(file_path, clean_salary=False, clean_date=True, remove_duplicates=False, output_format=None):
    """
    清洗招聘数据 Excel 文件（支持.xls 和.xlsx 格式）

    参数:
        file_path: Excel 文件路径（.xls 或.xlsx）
        clean_salary: 是否统一薪资格式（默认 False，保留原格式）
                clean_date: 是否统一日期格式为"YYYY年M月D日"（默认 True）
        remove_duplicates: 是否删除重复记录（默认 False）
        output_format: 输出格式（'xls' 或 'xlsx'，默认 None 则保持原格式）

    功能:
        1. 读取 Excel 表格内容（支持.xls 和.xlsx）
        2. 清洗岗位详情（删除换行、<br>等符号）
        3. 按岗位名称排序（相同岗位名称放在一起）
        4. 保持指定列格式一致
        5. 可选：统一薪资格式
        6. 可选：统一日期格式
        7. 可选：删除重复记录
        8. 覆盖保存原文件（保持原格式或指定格式）
    """

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在：{file_path}")

    # 检查文件扩展名
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in ['.xls', '.xlsx']:
        raise ValueError(f"不支持的文件格式：{file_ext}，请使用.xls 或.xlsx")

    # 读取 Excel 文件（pandas 自动识别格式）
    df = pd.read_excel(file_path)

    # 定义需要保持格式的列
    target_columns = [
        '岗位名称', '地址', '薪资范围', '公司名称', '所属行业',
        '公司规模', '公司类型', '岗位编码', '岗位详情'
    ]

    # 检查必要列是否存在
    missing_cols = [col for col in target_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"缺少必要列：{missing_cols}")

    print(f"📊 原始数据行数：{len(df)}")
    # print(f"📁 文件格式：{file_ext}")

    # ========== 1. 清洗岗位详情列 ==========
    def clean_job_details(text):
        """删除换行符、<br>等无用符号"""
        if pd.isna(text):
            return ''

        text = str(text)
        # 删除<br>标签（包括<br/>、<br />等变体）
        text = re.sub(r'<br\s*/?>', '', text, flags=re.IGNORECASE)
        # 删除换行符
        text = re.sub(r'\n|\r|\t', '', text)
        # 删除多余空格（保留单个空格）
        text = re.sub(r'\s+', ' ', text)
        # 删除首尾空格
        text = text.strip()

        return text

    # 应用清洗函数
    df['岗位详情'] = df['岗位详情'].apply(clean_job_details)

    # ========== 2. 统一其他列的数据类型 ==========
    for col in target_columns:
        if col != '岗位详情':  # 岗位详情已处理
            df[col] = df[col].apply(lambda x: '' if pd.isna(x) else str(x).strip())

    # ========== 3. 可选：统一薪资格式 ==========
    if clean_salary:
        print("🔧 正在统一薪资格式...")

        def standardize_salary(text):
            """统一薪资格式为：X-X 元/月 或 面议"""
            if pd.isna(text) or str(text).strip() == '':
                return '面议'

            text = str(text).strip()

            # 如果已经是"面议"
            if '面议' in text:
                return '面议'

            # 处理"元/天"格式
            if '元/天' in text:
                match = re.search(r'(\d+)-?(\d*)', text)
                if match:
                    min_val = match.group(1)
                    max_val = match.group(2) if match.group(2) else min_val
                    # 转换为月薪（按 22 天计算）
                    min_month = int(min_val) * 22
                    max_month = int(max_val) * 22
                    return f'{min_month}-{max_month}元/月'
                return text

            # 处理"元·X 薪"格式（如 7000-10000 元·13 薪）
            if '·' in text and '薪' in text:
                match = re.search(r'(\d+)-?(\d*)', text)
                salary_match = re.search(r'(\d+) 薪', text)
                if match and salary_match:
                    min_val = match.group(1)
                    max_val = match.group(2) if match.group(2) else min_val
                    months = int(salary_match.group(1))
                    # 转换为年薪
                    min_year = int(min_val) * months
                    max_year = int(max_val) * months
                    return f'{min_year}-{max_year}元/年'
                return text

            # 处理"万"单位
            if '万' in text:
                match = re.search(r'(\d+\.?\d*)-?(\d*\.?\d*)', text)
                if match:
                    min_val = float(match.group(1))
                    max_val = float(match.group(2)) if match.group(2) else min_val
                    # 转换为元
                    min_yuan = int(min_val * 10000)
                    max_yuan = int(max_val * 10000)
                    if min_yuan == max_yuan:
                        return f'{min_yuan}元/月'
                    return f'{min_yuan}-{max_yuan}元/月'
                return text

            # 处理"元"格式（默认为月薪）
            if '元' in text:
                match = re.search(r'(\d+)-?(\d*)', text)
                if match:
                    min_val = match.group(1)
                    max_val = match.group(2) if match.group(2) else min_val
                    if min_val == max_val:
                        return f'{min_val}元/月'
                    return f'{min_val}-{max_val}元/月'
                return text

            # 其他情况保留原样
            return text

        df['薪资范围'] = df['薪资范围'].apply(standardize_salary)

    # ========== 3.5. 可选：统一日期格式 ==========
    if clean_date:
        print("🔧 正在统一日期格式...")

        def standardize_date(text):
            """统一日期格式为：YYYY年M月D日"""
            if pd.isna(text) or str(text).strip() == '':
                return ''

            text = str(text).strip()

            # 处理 "2025-07-27 00:13:40" 格式
            match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', text)
            if match:
                year = match.group(1)
                month = match.group(2)
                day = match.group(3)
                # 去掉月份和日期的前导零
                month = str(int(month))
                day = str(int(day))
                return f'{year}年{month}月{day}日'

            # 处理 "7月22日" 格式（需要补充年份，默认使用当前年份）
            match = re.search(r'(\d{1,2})月(\d{1,2})日', text)
            if match:
                month = match.group(1)
                day = match.group(2)
                # 去掉月份和日期的前导零
                month = str(int(month))
                day = str(int(day))
                # 默认使用2025年
                return f'2025年{month}月{day}日'

            # 其他情况保留原样
            return text

        # 检查是否有日期相关的列
        date_columns = [col for col in df.columns if '日期' in col or 'date' in col.lower() or '更新' in col]
        if date_columns:
            for date_col in date_columns:
                print(f"  处理列: {date_col}")
                df[date_col] = df[date_col].apply(standardize_date)
        else:
            print("  未找到日期列，跳过日期格式统一")

    # ========== 4. 可选：删除重复记录 ==========
    if remove_duplicates:
        print("🔧 正在删除重复记录...")
        original_count = len(df)
        # 根据岗位编码去重（岗位编码通常唯一）
        if '岗位编码' in df.columns:
            df = df.drop_duplicates(subset=['岗位编码'], keep='first')
        else:
            # 如果没有岗位编码，根据岗位名称 + 公司名称 + 地址去重
            df = df.drop_duplicates(subset=['岗位名称', '公司名称', '地址'], keep='first')

        removed_count = original_count - len(df)
        print(f"✓ 删除重复记录：{removed_count}条")

    # ========== 5. 按岗位名称排序 ==========
    df = df.sort_values(by='岗位名称', ascending=True, kind='stable')

    # 重置索引
    df = df.reset_index(drop=True)

    # ========== 6. 保存覆盖原文件 ==========
    output_path = file_path

    # 确定输出格式
    if output_format is None:
        output_format = file_ext
    else:
        output_format = '.' + output_format.lower().replace('.', '')
        output_path = os.path.splitext(file_path)[0] + output_format

    # 根据文件扩展名选择合适的引擎
    print(f"💾 保存格式：{output_format}")

    if output_format == '.xls':
        # .xls 格式使用 openpyxl 引擎
        df.to_excel(output_path, index=False, engine='openpyxl')
        print("⚠️  注意：.xls 格式最大支持 65536 行，如数据量大建议使用.xlsx")
    else:
        # .xlsx 格式使用 openpyxl 引擎（推荐）
        df.to_excel(output_path, index=False, engine='openpyxl')

    print(f"\n✓ 数据清洗完成！")
    print(f"✓ 处理后行数：{len(df)}")
    print(f"✓ 文件已保存：{output_path}")

    return df


def process_excel_jobs(file_path: str, url_column_name: str='岗位来源地址'):
    """
    读取Excel，提取URL并抓取信息，最后写回原文件

    参数:
        file_path: Excel文件的路径
        url_column_name: Excel中存放职位URL的列名
    """
    # 1. 加载数据
    if not os.path.exists(file_path):
        print(f"❌ 错误：找不到文件 {file_path}")
        return

    # 根据后缀判断读取方式（pandas会自动处理）
    df = pd.read_excel(file_path)

    # 检查列名是否存在
    if url_column_name not in df.columns:
        print(f"❌ 错误：列名 '{url_column_name}' 不在表中，请检查！")
        return

    print(f"🚀 开始处理，共 {len(df)} 行数据...")

    # 2. 遍历并抓取
    for index, row in df.iterrows():
        url = row[url_column_name]

        # 简单判断URL是否有效
        if pd.isna(url) or str(url).strip() == "":
            continue

        print(f"🔍 正在抓取第 {index + 1} 行: {url}")

        try:
            # 调用你提供的抓取函数
            from ai_service.scripts.zhaopin_spider import fetch_job_info
            job_info = fetch_job_info(url=url)
            # print("11")

            # 3. 判断字典是否为空（以及是否抓到了有效内容）
            # 假设 fetch_job_info 返回 {} 或者 None 或者 字典值全为 None
            if job_info and any(job_info.values()):
                # 将获取到的信息填充到对应的列
                for key, value in job_info.items():
                    # 如果值为 None 或空字符串，则不修改也不添加
                    if value is None or value == "":
                        print(f"⚠️ 第 {index + 1} 行抓取结果为空，跳过修改。")
                        continue
                    # 如果列不存在，pandas会自动创建新列
                    df.at[index, key] = value
                print(f"✅ 抓取成功")
            else:
                print(f"⚠️ 第 {index + 1} 行抓取结果为空，跳过修改。")

        except Exception as e:
            print(f"❌ 处理第 {index + 1} 行时发生异常: {e}")

    # 4. 保存文件
    output_path = file_path
    _, ext = os.path.splitext(output_path)
    output_format = ext.lower()

    try:
        if output_format == '.xls':
            # .xls 格式使用 openpyxl 引擎（注意：openpyxl通常支持xlsx，老版xls可能需要xlwt，但依你要求写）
            df.to_excel(output_path, index=False, engine='openpyxl')
            print(f"💾 数据已保存至 {output_path}")
            print("⚠️ 注意：.xls 格式最大支持 65536 行，如数据量大建议使用 .xlsx")
        else:
            # .xlsx 格式使用 openpyxl 引擎
            df.to_excel(output_path, index=False, engine='openpyxl')
            print(f"💾 数据已成功保存至 {output_path}")

    except Exception as e:
        print(f"❌ 保存文件失败: {e}")

# ========== 使用示例 ==========
if __name__ == "__main__":
    file_path = r"E:\软件工程相关资料\项目比赛\服创2026\a13基于AI的大学生职业规划智能体-JD采样数据.xls"
    filter_computer_jobs_excel(file_path)
    clean_job_excel(file_path)
    # read_excel_to_jobinfo(file_path)
    # process_excel_jobs(file_path)




# # ========== 进阶版本：支持更多自定义选项 ==========
# def clean_job_excel_advanced(file_path,
#                              clean_salary=False,
#                              clean_date=True,
#                              remove_duplicates=False,
#                              salary_unit='月',  # 薪资格式单位：'月' 或 '年'
#                              duplicate_cols=None,  # 去重依据列
#                              output_path=None,  # 输出路径（None 则覆盖原文件）
#                              output_format=None):  # 输出格式（'xls' 或 'xlsx'）
#     """
#     进阶版清洗函数，支持更多自定义选项（支持.xls 和.xlsx）
#
#     参数:
#         file_path: 文件路径
#         clean_salary: 是否统一薪资格式（默认 False）
#         clean_date: 是否统一日期格式为"YYYY年M月D日"（默认 True）
#         remove_duplicates: 是否删除重复记录（默认 False）
#         salary_unit: 薪资格式单位（'月' 或 '年'）
#         duplicate_cols: 去重依据列列表（默认 ['岗位编码']）
#         output_path: 输出路径（None 则覆盖原文件）
#         output_format: 输出格式（'xls' 或 'xlsx'，默认 None 保持原格式）
#
#     返回:
#         清洗后的 DataFrame
#     """
#
#     # 检查文件是否存在
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"文件不存在：{file_path}")
#
#     # 检查文件扩展名
#     file_ext = os.path.splitext(file_path)[1].lower()
#     if file_ext not in ['.xls', '.xlsx']:
#         raise ValueError(f"不支持的文件格式：{file_ext}，请使用.xls 或.xlsx")
#
#     # 读取 Excel 文件
#     df = pd.read_excel(file_path)
#
#     # 定义需要保持格式的列
#     target_columns = [
#         '岗位名称', '地址', '薪资范围', '公司名称', '所属行业',
#         '公司规模', '公司类型', '岗位编码', '岗位详情'
#     ]
#
#     # 检查必要列是否存在
#     missing_cols = [col for col in target_columns if col not in df.columns]
#     if missing_cols:
#         raise ValueError(f"缺少必要列：{missing_cols}")
#
#     print(f"📊 原始数据行数：{len(df)}")
#     print(f"📁 文件格式：{file_ext}")
#
#     # 1. 清洗岗位详情
#     df['岗位详情'] = df['岗位详情'].apply(
#         lambda x: re.sub(r'<br\s*/?>|\n|\r|\t', '', str(x) if pd.notna(x) else '').strip()
#     )
#
#     # 2. 统一其他列格式
#     for col in target_columns:
#         if col != '岗位详情':
#             df[col] = df[col].apply(lambda x: '' if pd.isna(x) else str(x).strip())
#
#     # 3. 统一薪资格式
#     if clean_salary:
#         print(f"🔧 正在统一薪资格式（单位：{salary_unit}）...")
#
#         def standardize_salary(text):
#             if pd.isna(text) or str(text).strip() == '':
#                 return '面议'
#
#             text = str(text).strip()
#
#             if '面议' in text:
#                 return '面议'
#
#             # 提取数字
#             match = re.search(r'(\d+\.?\d*)-?(\d*\.?\d*)', text)
#             if match:
#                 min_val = float(match.group(1))
#                 max_val = float(match.group(2)) if match.group(2) else min_val
#
#                 # 处理"万"单位
#                 if '万' in text:
#                     min_val *= 10000
#                     max_val *= 10000
#
#                 # 处理"元/天"
#                 if '元/天' in text:
#                     min_val *= 22
#                     max_val *= 22
#
#                 # 处理"X 薪"
#                 if '薪' in text:
#                     salary_match = re.search(r'(\d+) 薪', text)
#                     if salary_match:
#                         months = int(salary_match.group(1))
#                         if salary_unit == '年':
#                             min_val *= months
#                             max_val *= months
#                         # 否则保持月薪
#
#                 min_val = int(min_val)
#                 max_val = int(max_val)
#
#                 if salary_unit == '年':
#                     return f'{min_val}-{max_val}元/年' if min_val != max_val else f'{min_val}元/年'
#                 else:
#                     return f'{min_val}-{max_val}元/月' if min_val != max_val else f'{min_val}元/月'
#
#             return '面议'
#
#         df['薪资范围'] = df['薪资范围'].apply(standardize_salary)
#
#     # 3.5. 统一日期格式
#     if clean_date:
#
#         def standardize_date(text):
#             """统一日期格式为：YYYY年M月D日"""
#             if pd.isna(text) or str(text).strip() == '':
#                 return ''
#
#             text = str(text).strip()
#
#             # 处理 "2025-07-27 00:13:40" 格式
#             match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', text)
#             if match:
#                 year = match.group(1)
#                 month = match.group(2)
#                 day = match.group(3)
#                 # 去掉月份和日期的前导零
#                 month = str(int(month))
#                 day = str(int(day))
#                 return f'{year}年{month}月{day}日'
#
#             # 处理 "7月22日" 格式（需要补充年份，默认使用当前年份）
#             match = re.search(r'(\d{1,2})月(\d{1,2})日', text)
#             if match:
#                 month = match.group(1)
#                 day = match.group(2)
#                 # 去掉月份和日期的前导零
#                 month = str(int(month))
#                 day = str(int(day))
#                 # 默认使用2025年
#                 return f'{datetime.now().year}年{month}月{day}日'
#
#             # 其他情况保留原样
#             return text
#
#         # 检查是否有日期相关的列
#         date_columns = [col for col in df.columns if '日期' in col or 'date' in col.lower() or '更新' in col]
#         if date_columns:
#             for date_col in date_columns:
#                 print(f"  处理列: {date_col}")
#                 df[date_col] = df[date_col].apply(standardize_date)
#         else:
#             print("  未找到日期列，跳过日期格式统一")
#
#     # 4. 删除重复记录
#     if remove_duplicates:
#         original_count = len(df)
#
#         if duplicate_cols is None:
#             duplicate_cols = ['岗位编码'] if '岗位编码' in df.columns else ['岗位名称', '公司名称', '地址']
#
#         df = df.drop_duplicates(subset=duplicate_cols, keep='first')
#         print(f"✓ 删除重复记录：{original_count - len(df)}条")
#
#     # 5. 按岗位名称排序
#     df = df.sort_values(by='岗位名称', ascending=True, kind='stable').reset_index(drop=True)
#
#     # 6. 保存文件
#     if output_path is None:
#         save_path = file_path
#     else:
#         save_path = output_path
#
#     # 确定输出格式
#     if output_format is None:
#         save_format = os.path.splitext(save_path)[1].lower()
#     else:
#         save_format = '.' + output_format.lower().replace('.', '')
#         save_path = os.path.splitext(save_path)[0] + save_format
#
#     print(f"💾 保存格式：{save_format}")
#
#     # 根据格式选择引擎
#     if save_format == '.xls':
#         df.to_excel(save_path, index=False, engine='openpyxl')
#         if len(df) > 65536:
#             print("⚠️  警告：数据行数超过.xls 限制（65536 行），建议使用.xlsx 格式！")
#     else:
#         df.to_excel(save_path, index=False, engine='openpyxl')
#
#     return df



