import asyncio
from pathlib import Path
<<<<<<< HEAD
from typing import List, Union
=======
from typing import List
>>>>>>> origin/master

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# 导入你提供的模块
from ai_service.models.job_info import JobInfo

from ai_service.scripts.py.job_table_cleaning_csv import read_csv_to_jobinfo, clean_job_csv
from ai_service.scripts.py.job_table_cleaning_excel import clean_job_excel, read_excel_to_jobinfo
from ai_service.utils.logger_handler import log
from config import settings


# ==========================================
# 数据库配置（从配置文件读取）
# ==========================================
DB_URL = (
    f"mysql+aiomysql://{settings.database.user}:{settings.database.password}"
    f"@{settings.database.host}:{settings.database.port}/{settings.database.database}"
    f"?charset=utf8mb4"
)
engine = create_async_engine(DB_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# ==========================================
# 核心业务逻辑
# ==========================================
async def process_and_insert_jobs(file_path: str, max_process: int = None):
    """
    读取 Excel，保存岗位信息，生成岗位画像并保存。

    Args:
        file_path: Excel 文件路径 根据文件后缀自动读取 Excel 或 CSV，并转换为 JobInfo 列表支持：- .xls - .xlsx - .csv
        max_process: 最大处理条数（用于测试，防止一次性消耗过多 Token，设为 None 则处理全部）
    """
    log.info(f"开始处理文件: {file_path}")
    # 1. 读取 Excel 文件生成 JobInfo 列表
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        suffix = path.suffix.lower()
        if suffix in [".xls", ".xlsx"]:
            log.info(f"识别为 Excel 文件，开始读取: {file_path}")
            clean_job_excel(file_path)
            job_list: List[JobInfo] = read_excel_to_jobinfo(file_path)
        elif suffix in [".csv"]:
            log.info(f"识别为 CSV 文件，开始读取: {file_path}")
            clean_job_csv(file_path)
            job_list: List[JobInfo] = read_csv_to_jobinfo(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")

        log.info(f"成功从 Excel 读取 {len(job_list)} 条岗位数据。")
    except Exception as e:
        log.error(f"读取 Excel 失败: {e}")
        return

    if max_process:
        job_list = job_list[:max_process]
        log.info(f"⚠开启测试模式，截取前 {max_process} 条数据进行处理。")

    async with AsyncSessionLocal() as session:
        from ai_service.repository.job_info_repository import JobRepository
        job_repo = JobRepository(session)

        # 2. 批量保存岗位信息到数据库
        log.info("正在将岗位基础信息保存到数据库...")
        try:
            await job_repo.create_all(job_list)
            log.info("岗位基础信息保存成功！")
        except Exception as e:
            log.error(f"保存岗位信息失败: {e}")
            return


def get_all_files(folder_path: Union[str, Path], recursive: bool = True) -> List[str]:
    """
    获取文件夹下所有文件的绝对路径
    :param folder_path: 文件夹路径（支持相对/绝对路径，如 "./data" 或 r"C:\test"）
    :param recursive: 是否递归遍历子目录，默认 True
    :return: 文件绝对路径列表
    """
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"路径不存在: {folder_path}")
    if not folder.is_dir():
        raise NotADirectoryError(f"路径不是文件夹: {folder_path}")

<<<<<<< HEAD
    if recursive:
        return [str(f.resolve()) for f in folder.rglob("*") if f.is_file()]
    else:
        return [str(f.resolve()) for f in folder.iterdir() if f.is_file()]
=======
async def main():
    """主函数：处理任务并确保资源正确清理"""
    EXCEL_FILE_PATH = r"E:\软件工程相关资料\项目比赛\服创2026\岗位数据\.NET-1773231373303.csv"
>>>>>>> origin/master


async def main(max_concurrent: int = 5):
    excel_file_paths = get_all_files(r"E:\软件工程相关资料\项目比赛\服创2026\岗位数据\数据")
    semaphore = asyncio.Semaphore(max_concurrent)  # 限制并发数

    async def safe_process(path):
        async with semaphore:
            try:
                await process_and_insert_jobs(path)
                print(f"✅ 成功: {path}")
            except Exception as e:
                print(f"❌ 失败 {path}: {e}")

    try:
        # 并发调度所有任务，但受信号量严格控流
        await asyncio.gather(*(safe_process(p) for p in excel_file_paths))
    finally:
        await engine.dispose()
        print("🔌 数据库连接池已安全关闭")


if __name__ == "__main__":
    asyncio.run(main())