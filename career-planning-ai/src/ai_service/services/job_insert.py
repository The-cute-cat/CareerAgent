import asyncio
import os
import time
from typing import List

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# 导入你提供的模块
from ai_service.models.job_info import JobInfo
from ai_service.models.job_portrait import JobPortrait
from ai_service.services.job_table_cleaning import read_excel_to_jobinfo
from ai_service.services.job_profile_builder import analyze_job_description
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
        file_path: Excel 文件路径
        max_process: 最大处理条数（用于测试，防止一次性消耗过多 Token，设为 None 则处理全部）
    """
    print(f"开始处理文件: {file_path}")
    # 1. 读取 Excel 文件生成 JobInfo 列表
    try:
        job_list: List[JobInfo] = read_excel_to_jobinfo(file_path)
        print(f"成功从 Excel 读取 {len(job_list)} 条岗位数据。")
    except Exception as e:
        print(f"读取 Excel 失败: {e}")
        return

    if max_process:
        job_list = job_list[:max_process]
        print(f"⚠开启测试模式，截取前 {max_process} 条数据进行处理。")

    async with AsyncSessionLocal() as session:
        from ai_service.repository.job_info_repository import JobRepository
        job_repo = JobRepository(session)
        from ai_service.repository.job_portrait_repository import JobPortraitRepository
        portrait_repo = JobPortraitRepository(session)

        # 2. 批量保存岗位信息到数据库
        print("正在将岗位基础信息保存到数据库...")
        try:
            saved_jobs = await job_repo.create_all(job_list)
            print("岗位基础信息保存成功！")
        except Exception as e:
            print(f"保存岗位信息失败: {e}")
            return

        # 3. 遍历保存后的岗位，生成并保存岗位画像
        print("开始调用大模型生成岗位画像...")
        portrait_list: List[JobPortrait] = []

        for index, job in enumerate(saved_jobs):
            try:
                # 注意：analyze_job_description 是同步的 LLM 调用
                # 为了不阻塞底层的 asyncio 事件循环，我们使用 asyncio.to_thread 将其放入线程池运行
                # analyze_job_description 期望接收 jd_text（字符串），而不是字典
                jd_text = job.job_desc or ""
                if not jd_text:
                    print(f" 岗位ID {job.id} 没有岗位描述，跳过")
                    continue

                result_data = await asyncio.to_thread(analyze_job_description, jd_text)

                # job_json = job.to_json(exclude_fields=['job_source_url', 'created_at', 'updated_at'], indent=2)
                # result_data = await asyncio.to_thread(analyze_job_description, job_json)

                if "error" in result_data:
                    print(f" 岗位ID {job.id} 画像解析失败: {result_data['error']}")
                    continue

                # 提取 profiles 数据作为 skills_req
                profiles_data = result_data.get("profiles", {})

                # 构建 JobPortrait 对象
                portrait = JobPortrait(
                    job_id=job.id,
                    skills_req=profiles_data,
                    radar_data={}  # 此处雷达图数据暂且置空，你可以后续补充计算逻辑
                )
                portrait_list.append(portrait)
                print(f" 岗位ID {job.id} 画像生成成功！")

                # ⚠️ API 速率控制：防止高并发导致阿里云通义千问 API 报错 (HTTP 429 Too Many Requests)
                await asyncio.sleep(1)

            except Exception as e:
                print(f" 岗位ID {job.id} 处理发生未知异常: {e}")
                continue

        # 4. 批量保存岗位画像到数据库
        if portrait_list:
            print(f"💾 正在将 {len(portrait_list)} 条岗位画像存入数据库...")
            try:
                await portrait_repo.create_all(portrait_list)
                print("🎉 所有画像保存成功！整体流程结束。")
            except Exception as e:
                print(f"❌ 保存岗位画像失败: {e}")
        else:
            print("⚠️ 没有成功生成的岗位画像需要保存。")


async def main():
    """主函数：处理任务并确保资源正确清理"""
    EXCEL_FILE_PATH = r"E:\软件工程相关资料\项目比赛\服创2026\a13基于AI的大学生职业规划智能体-JD采样数据  - 副本.xls"

    # 确保在运行前设置了环境变量
    # os.environ["LLM__API_KEY"] = "your-tongyi-api-key"

    try:
        # 运行异步主函数
        # 建议先用 max_process=5 测试一下整条链路，没问题后再去掉这个参数跑全量
        await process_and_insert_jobs(EXCEL_FILE_PATH, max_process=1)
    finally:
        # 确保引擎被正确关闭
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())