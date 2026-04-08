__all__ = [
    "read_csv_to_jobinfo",
    "read_csv_to_jobinfo_dict",
    "clean_job_csv",
]

from pathlib import Path
from typing import Any, Optional, List, Dict
from datetime import datetime
import os
import re

import pandas as pd

from ai_service.models.job_info import JobInfo
from ai_service.services import log


# ==================== CSV -> JobInfo 字段映射 ====================
CSV_TO_MODEL_MAPPING = {
    "job": "job_title",
    "salary": "salary_range",
    "url": "job_source_url",
    "describtion": "job_desc",   # 原 csv 字段拼写就是 describtion
    "update_time": "updated_time",
}


# ==================== 工具函数 ====================
def parse_chinese_date(date_str: Any) -> Optional[datetime]:
    """
    将日期字符串转换为 datetime 对象
    支持：
    - 2025 年 4 月 11 日
    - 2025-04-11
    - 2025/04/11
    - 2025-04-11 12:30:00
    - 2025/04/11 12:30:00
    """
    if date_str is None or pd.isna(date_str):
        return None

    date_str = str(date_str).strip()
    if not date_str:
        return None

    chinese_pattern = r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日"
    match = re.match(chinese_pattern, date_str)
    if match:
        year, month, day = map(int, match.groups())
        return datetime(year, month, day)

    for fmt in [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
    ]:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


def normalize_text(value: Any) -> Optional[str]:
    """将值转为干净字符串，空值返回 None"""
    if value is None or pd.isna(value):
        return None
    value = str(value).strip()
    return value if value else None


def clean_html_and_spaces(text: Any) -> str:
    """清洗描述中的 html / 换行 / 多余空格"""
    if text is None or pd.isna(text):
        return ""
    text = str(text)
    text = re.sub(r"<br\s*/?>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[\r\n\t]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_job_name(text: Any) -> str:
    """清洗岗位名，去掉括号内容"""
    if text is None or pd.isna(text):
        return ""
    text = str(text).strip()
    text = re.sub(r"\(.*?\)|\（.*?\）", "", text)
    return text.strip()


def standardize_salary(text: Any) -> str:
    """
    统一薪资格式
    支持：
    - 1.6-3万·14薪
    - 5000-10000元·13薪
    - 1.1-1.8万
    - 100-150元/天
    - 7000-12000元
    """
    if text is None or pd.isna(text) or str(text).strip() == "":
        return "面议"

    text = str(text).strip()
    if "面议" in text:
        return "面议"

    num_pattern = r"(\d+(?:\.\d+)?)-?(\d+(?:\.\d+)?)?"

    if "万" in text and "薪" in text:
        match = re.search(num_pattern, text)
        salary_match = re.search(r"·\s*(\d+)\s*薪", text)
        if match and salary_match:
            min_val = float(match.group(1))
            max_val = float(match.group(2)) if match.group(2) else min_val
            months = int(salary_match.group(1))
            min_year = int(min_val * 10000 * months)
            max_year = int(max_val * 10000 * months)
            return f"{min_year}-{max_year}元/年"

    elif "元" in text and "薪" in text:
        match = re.search(num_pattern, text)
        salary_match = re.search(r"·\s*(\d+)\s*薪", text)
        if match and salary_match:
            min_val = float(match.group(1))
            max_val = float(match.group(2)) if match.group(2) else min_val
            months = int(salary_match.group(1))
            min_year = int(min_val * months)
            max_year = int(max_val * months)
            return f"{min_year}-{max_year}元/年"

    elif "万" in text:
        match = re.search(num_pattern, text)
        if match:
            min_val = float(match.group(1))
            max_val = float(match.group(2)) if match.group(2) else min_val
            min_yuan = int(min_val * 10000)
            max_yuan = int(max_val * 10000)
            if min_yuan == max_yuan:
                return f"{min_yuan}元/月"
            return f"{min_yuan}-{max_yuan}元/月"

    elif "元/天" in text or "天" in text:
        match = re.search(num_pattern, text)
        if match:
            min_val = float(match.group(1))
            max_val = float(match.group(2)) if match.group(2) else min_val
            min_month = int(min_val * 22)
            max_month = int(max_val * 22)
            return f"{min_month}-{max_month}元/月"

    elif "元" in text:
        match = re.search(num_pattern, text)
        if match:
            min_val = float(match.group(1))
            max_val = float(match.group(2)) if match.group(2) else min_val
            if min_val == max_val:
                return f"{int(min_val)}元/月"
            return f"{int(min_val)}-{int(max_val)}元/月"

    return text


def build_location(city: Any, district: Any) -> Optional[str]:
    """city 和 district 合并为 city-district"""
    city = normalize_text(city)
    district = normalize_text(district)

    if city and district:
        return f"{city}-{district}"
    if city:
        return city
    if district:
        return district
    return None


def build_job_desc(
    experience: Any,
    education: Any,
    skills_item: Any,
    describtion: Any,
) -> str:
    """
    按要求把 experience、education、skills_item 写到 describtion 前面

    格式示例：
    经验不限;大专;职位描述：xxx
    经验不限;大专;技能：Java;Spring;职位描述：xxx
    """
    exp = normalize_text(experience)
    edu = normalize_text(education)
    skills = normalize_text(skills_item)
    desc = clean_html_and_spaces(describtion)

    prefix_parts = []
    prefix_parts.append("职位描述：")
    if exp:
        prefix_parts.append(f"{exp}")
    if edu:
        prefix_parts.append(f"{edu}")
    if skills:
        prefix_parts.append(f"技能:{skills}")

    prefix = ";".join(prefix_parts)

    if prefix and desc:
        return f"{prefix};职位描述：{desc}"
    if prefix and not desc:
        return f"{prefix};职位描述："
    if not prefix and desc:
        return f"职位描述：{desc}"
    return "职位描述："

def read_csv_to_jobinfo_dict(
    file_path: str,
    encoding: Optional[str] = "utf-8",
    skip_rows: int = 0,
) -> List[Dict[str, Any]]:
    """
    读取清洗后的 CSV 文件并生成字典列表
    不保存时间字段 updated_time
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    df = pd.read_csv(
        file_path,
        skiprows=skip_rows,
        dtype=str,
        encoding=encoding,
    )

    required_columns = {"job_title", "salary_range", "job_source_url", "location", "job_desc"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        log.warning(f"警告: CSV 中未找到部分关键列: {missing_columns}")

    data_list: List[Dict[str, Any]] = []

    for _, row in df.iterrows():
        record = {
            "job_title": normalize_text(row.get("job_title")),
            "salary_range": normalize_text(row.get("salary_range")),
            "job_source_url": normalize_text(row.get("job_source_url")),
            "location": normalize_text(row.get("location")),
            "job_desc": normalize_text(row.get("job_desc")),
        }

        # 不保存时间
        # 不写 updated_time

        record = {
            k: v for k, v in record.items()
            if v is not None and str(v).strip() != ""
        }

        data_list.append(record)

    return data_list

# ==================== 读取 CSV -> JobInfo ====================
def read_csv_to_jobinfo(
    file_path: str,
    encoding: Optional[str] = "utf-8",
    skip_rows: int = 0,
) -> List[JobInfo]:
    """
    读取清洗后的 CSV 文件并生成 JobInfo 实体列表

    说明：
    1. 与 clean_job_csv 清洗后的字段对应
    2. 不保存时间字段 updated_time
    3. 保留 address 列，但由于 JobInfo 模型中没有 address 字段，因此不写入实体
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    df = pd.read_csv(
        file_path,
        skiprows=skip_rows,
        dtype=str,
        encoding=encoding,
    )

    # 对应 clean_job_csv 清洗后的字段
    required_columns = {"job_title", "salary_range", "job_source_url", "location", "job_desc"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        log.warning(f"警告: CSV 中未找到部分关键列: {missing_columns}")

    job_info_list: List[JobInfo] = []

    for idx, row in df.iterrows():
        try:
            job_info_data: Dict[str, Any] = {}

            # 直接读取清洗后的字段
            job_info_data["job_title"] = normalize_text(row.get("job_title"))
            job_info_data["salary_range"] = normalize_text(row.get("salary_range"))
            job_info_data["job_source_url"] = normalize_text(row.get("job_source_url"))
            job_info_data["location"] = normalize_text(row.get("location"))
            job_info_data["job_desc"] = normalize_text(row.get("job_desc"))

            # 不保存时间，所以这里不要写：
            # job_info_data["updated_time"] = ...

            # address 保留在 CSV 中，但 JobInfo 模型里没有这个字段，所以不传
            # 如果你后面给 JobInfo 增加了 address 字段，再在这里补上：
            # job_info_data["address"] = normalize_text(row.get("address"))

            # 过滤掉 None / 空字符串
            job_info_data = {
                k: v for k, v in job_info_data.items()
                if v is not None and str(v).strip() != ""
            }

            # 创建 JobInfo
            job_info = JobInfo(**job_info_data)
            job_info_list.append(job_info)

        except Exception as e:
            log.error(f"第 {idx + 2} 行数据解析失败: {e}", exc_info=True)
            continue

    return job_info_list

# ==================== 清洗 CSV ====================
def clean_job_csv(
    file_path: str,
    clean_title: bool = True,
    clean_salary: bool = True,
    remove_duplicates: bool = True,
    output_path: Optional[str] = None,
    encoding: str = "utf-8",
) -> pd.DataFrame:
    """
    清洗招聘 CSV 文件

    功能：
    1. 清洗 job 岗位名称（可选）
    2. 统一 salary 薪资格式（可选）
    3. 不处理 update_time，保留原值
    4. city + district => location
    5. education + skills_item + experience + describtion => 组装为 job_desc
    6. 删除 job_type / headcount / employer_tag
    7. 保留 address
    8. 可选去重
    9. 覆盖保存或另存为新 csv
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在：{file_path}")

    df = pd.read_csv(file_path, dtype=str, encoding=encoding)

    log.info(f"📊 原始数据行数：{len(df)}")

    # 统一空值处理
    for col in df.columns:
        df[col] = df[col].apply(lambda x: "" if pd.isna(x) else str(x).strip())

    # 1. 清洗描述
    if "describtion" in df.columns:
        df["describtion"] = df["describtion"].apply(clean_html_and_spaces)

    # 2. 清洗岗位名称
    if clean_title and "job" in df.columns:
        log.info("🔧 正在清洗岗位名称...")
        df["job"] = df["job"].apply(clean_job_name)

    # 3. 清洗薪资
    if clean_salary and "salary" in df.columns:
        log.info("🔧 正在统一薪资格式...")
        df["salary"] = df["salary"].apply(standardize_salary)

    # 5. 合并 location
    if "city" in df.columns or "district" in df.columns:
        df["location"] = df.apply(
            lambda row: build_location(row.get("city"), row.get("district")) or "",
            axis=1,
        )

    # 6. 组装 job_desc
    df["job_desc"] = df.apply(
        lambda row: build_job_desc(
            experience=row.get("experience"),
            education=row.get("education"),
            skills_item=row.get("skills_item"),
            describtion=row.get("describtion"),
        ),
        axis=1,
    )

    # 7. 字段重命名
    rename_mapping = {
        "job": "job_title",
        "salary": "salary_range",
        "url": "job_source_url",
        "update_time": "updated_time",
    }
    existing_rename_mapping = {k: v for k, v in rename_mapping.items() if k in df.columns}
    df = df.rename(columns=existing_rename_mapping)

    # 8. 删除不需要字段
    # address 保留，不删除
    drop_columns = [
        "job_type",
        "headcount",
        "employer_tag",
        "city",
        "district",
        "education",
        "skills_item",
        "experience",
        "describtion",
    ]
    existing_drop_columns = [col for col in drop_columns if col in df.columns]
    if existing_drop_columns:
        df = df.drop(columns=existing_drop_columns)

    # 9. 可选去重
    if remove_duplicates:
        log.info("🔧 正在删除重复记录...")
        original_count = len(df)

        if "job_source_url" in df.columns:
            df = df.drop_duplicates(subset=["job_source_url"], keep="first")
        elif "job_title" in df.columns and "location" in df.columns:
            df = df.drop_duplicates(subset=["job_title", "location"], keep="first")
        elif "job_title" in df.columns:
            df = df.drop_duplicates(subset=["job_title"], keep="first")

        log.info(f"✓ 删除重复记录：{original_count - len(df)} 条")

    # 10. 排序
    if "job_title" in df.columns:
        df = df.sort_values(by="job_title", ascending=True, kind="stable")

    df = df.reset_index(drop=True)

    # 11. 保存
    if output_path is None:
        output_path = file_path

    log.info(f"💾 正在保存文件：{output_path}")
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    log.info(f"✓ 数据清洗完成！处理后行数：{len(df)}")
    log.info(f"✓ 文件已保存：{output_path}")

    return df


# ==================== 使用示例 ====================
if __name__ == "__main__":
    test_file_path = r"E:\软件工程相关资料\项目比赛\服创2026\岗位数据\.NET-1773231373303.csv"

    clean_job_csv(test_file_path)

    # job_list = read_csv_to_jobinfo(test_file_path)
    # print(f"JobInfo 数量: {len(job_list)}")
    # for job in job_list:
    #     print(job.job_title)
    # dict_list = read_csv_to_jobinfo_dict(test_file_path)
    # print(f"Dict 数量: {len(dict_list)}")