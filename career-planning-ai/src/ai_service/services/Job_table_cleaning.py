__all__ = ['clean_job_excel','read_excel_to_jobinfo']
# 清洗招聘数据 Excel 文件（支持.xls 和.xlsx 格式）
#从文件中读取数据，并转换为JobInfo/字典实体对象列表
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd
from datetime import datetime
import re
import os
from ai_service.models.job_info import JobInfo  # 替换为您的实际导入路径

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


# ========== 进阶版本：支持更多自定义选项 ==========
def clean_job_excel_advanced(file_path,
                             clean_salary=False,
                             clean_date=True,
                             remove_duplicates=False,
                             salary_unit='月',  # 薪资格式单位：'月' 或 '年'
                             duplicate_cols=None,  # 去重依据列
                             output_path=None,  # 输出路径（None 则覆盖原文件）
                             output_format=None):  # 输出格式（'xls' 或 'xlsx'）
    """
    进阶版清洗函数，支持更多自定义选项（支持.xls 和.xlsx）

    参数:
        file_path: 文件路径
        clean_salary: 是否统一薪资格式（默认 False）
        clean_date: 是否统一日期格式为"YYYY年M月D日"（默认 True）
        remove_duplicates: 是否删除重复记录（默认 False）
        salary_unit: 薪资格式单位（'月' 或 '年'）
        duplicate_cols: 去重依据列列表（默认 ['岗位编码']）
        output_path: 输出路径（None 则覆盖原文件）
        output_format: 输出格式（'xls' 或 'xlsx'，默认 None 保持原格式）

    返回:
        清洗后的 DataFrame
    """

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在：{file_path}")

    # 检查文件扩展名
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in ['.xls', '.xlsx']:
        raise ValueError(f"不支持的文件格式：{file_ext}，请使用.xls 或.xlsx")

    # 读取 Excel 文件
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
    print(f"📁 文件格式：{file_ext}")

    # 1. 清洗岗位详情
    df['岗位详情'] = df['岗位详情'].apply(
        lambda x: re.sub(r'<br\s*/?>|\n|\r|\t', '', str(x) if pd.notna(x) else '').strip()
    )

    # 2. 统一其他列格式
    for col in target_columns:
        if col != '岗位详情':
            df[col] = df[col].apply(lambda x: '' if pd.isna(x) else str(x).strip())

    # 3. 统一薪资格式
    if clean_salary:
        print(f"🔧 正在统一薪资格式（单位：{salary_unit}）...")

        def standardize_salary(text):
            if pd.isna(text) or str(text).strip() == '':
                return '面议'

            text = str(text).strip()

            if '面议' in text:
                return '面议'

            # 提取数字
            match = re.search(r'(\d+\.?\d*)-?(\d*\.?\d*)', text)
            if match:
                min_val = float(match.group(1))
                max_val = float(match.group(2)) if match.group(2) else min_val

                # 处理"万"单位
                if '万' in text:
                    min_val *= 10000
                    max_val *= 10000

                # 处理"元/天"
                if '元/天' in text:
                    min_val *= 22
                    max_val *= 22

                # 处理"X 薪"
                if '薪' in text:
                    salary_match = re.search(r'(\d+) 薪', text)
                    if salary_match:
                        months = int(salary_match.group(1))
                        if salary_unit == '年':
                            min_val *= months
                            max_val *= months
                        # 否则保持月薪

                min_val = int(min_val)
                max_val = int(max_val)

                if salary_unit == '年':
                    return f'{min_val}-{max_val}元/年' if min_val != max_val else f'{min_val}元/年'
                else:
                    return f'{min_val}-{max_val}元/月' if min_val != max_val else f'{min_val}元/月'

            return '面议'

        df['薪资范围'] = df['薪资范围'].apply(standardize_salary)

    # 3.5. 统一日期格式
    if clean_date:

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
                return f'{datetime.now().year}年{month}月{day}日'

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

    # 4. 删除重复记录
    if remove_duplicates:
        original_count = len(df)

        if duplicate_cols is None:
            duplicate_cols = ['岗位编码'] if '岗位编码' in df.columns else ['岗位名称', '公司名称', '地址']

        df = df.drop_duplicates(subset=duplicate_cols, keep='first')
        print(f"✓ 删除重复记录：{original_count - len(df)}条")

    # 5. 按岗位名称排序
    df = df.sort_values(by='岗位名称', ascending=True, kind='stable').reset_index(drop=True)

    # 6. 保存文件
    if output_path is None:
        save_path = file_path
    else:
        save_path = output_path

    # 确定输出格式
    if output_format is None:
        save_format = os.path.splitext(save_path)[1].lower()
    else:
        save_format = '.' + output_format.lower().replace('.', '')
        save_path = os.path.splitext(save_path)[0] + save_format

    print(f"💾 保存格式：{save_format}")

    # 根据格式选择引擎
    if save_format == '.xls':
        df.to_excel(save_path, index=False, engine='openpyxl')
        if len(df) > 65536:
            print("⚠️  警告：数据行数超过.xls 限制（65536 行），建议使用.xlsx 格式！")
    else:
        df.to_excel(save_path, index=False, engine='openpyxl')

    return df


# ========== 使用示例 ==========
if __name__ == "__main__":
    file_path = r"E:\软件工程相关资料\项目比赛\服创2026\a13基于AI的大学生职业规划智能体-JD采样数据  - 副本.xls"
    # clean_job_excel_advanced(file_path)

    job_list=read_excel_to_jobinfo(file_path)
    for job in job_list:
        print(job.to_json())

