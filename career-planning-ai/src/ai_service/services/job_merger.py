# ai_service/api/job_merge_api.py
import datetime
import json

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from ai_service.repository.connection_session import get_db_url
from ai_service.repository.job_info_repository import JobRepository
from ai_service.repository.job_portrait_repository import JobPortraitRepository
from ai_service.models.job_info import JobInfo
from ai_service.models.job_portrait import JobPortrait
from ai_service.response.result import error_msg, success_msg
from ai_service.services.job_profile_builder import analyze_job_description
from ai_service.utils.HDBSCAN import cluster_standard_jobs_with_hdbscan
from ai_service.utils.logger_handler import log
from typing import Dict, Any, List

router = APIRouter()

# 数据库会话配置
engine = create_async_engine(get_db_url(), echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def job_merger() -> Dict[str, Any]:
    """
    进行岗位合并
    步骤：
    1. 调用 cluster_standard_jobs_with_hdbscan 进行岗位聚类
    2. 对每个簇调用 analyze_job_description 合并成岗位画像
    3. 将 JSON 格式数据存入 skills_req 并保存到 job_portrait 表
    4. 更新 job_info 表的 job_profile_id 指向合并后的岗位画像 ID
    """

    try:
        async with AsyncSessionLocal() as session:
            # ==================== 步骤 1: 岗位聚类 ====================
            log.info("开始岗位聚类...")
            clustered_result: Dict[int, List[JobInfo]] = await cluster_standard_jobs_with_hdbscan(
                session=session,
                min_cluster_size=8,
                hdbscan_min_samples=3,
                batch_size=64,
                embedding_model="BAAI/bge-base-zh-v1.5",
                desc_max_len=150
            )

            if not clustered_result:
                log.warning("聚类结果为空，无岗位可合并")
                return error_msg("聚类结果为空，无岗位可合并")

            job_repo = JobRepository(session)
            portrait_repo = JobPortraitRepository(session)

            # ==================== 步骤 3: 处理每个簇 ====================
            portrait_ids = []
            total_jobs_processed = 0
            noise_jobs = 0

            for cluster_id, jobs in clustered_result.items():
                # 跳过噪声点 (cluster_id = -1)
                if cluster_id == -1:
                    noise_jobs = len(jobs)
                    log.info(f"跳过噪声簇，共 {noise_jobs} 个岗位")
                    continue

                if len(jobs) < 2:
                    log.warning(f"簇 {cluster_id} 只有 {len(jobs)} 个岗位，跳过合并")
                    continue

                log.info(f"处理簇 {cluster_id}，共 {len(jobs)} 个岗位")

                try:
                    # ==================== 步骤 4: 调用 LLM 分析合并 ====================
                    job_profile_data =analyze_job_description(jobs)

                    # 检查是否有错误
                    if "error" in job_profile_data:
                        log.error(f"簇 {cluster_id} 分析失败：{job_profile_data['error']}")
                        continue

                    # ==================== 步骤 5: 构建岗位画像对象 ====================
                    # 从 LLM 返回数据中提取信息
                    standard_title = job_profile_data.get("job_name", "未命名岗位")

                    # 创建岗位画像对象（skills_req 直接传入字典，SQLAlchemy JSON类型会自动序列化）
                    portrait = JobPortrait(
                        job_title=standard_title,
                        skills_req=job_profile_data,  # 直接传入字典，不转JSON字符串
                        is_deleted=0
                    )

                    # ==================== 步骤 6: 保存岗位画像 ====================
                    saved_portrait = await portrait_repo.create(portrait)
                    portrait_ids.append(saved_portrait.id)
                    job_profile_data["id"] = saved_portrait.id
                    # 更新时直接传入字典，不转JSON字符串
                    await portrait_repo.update(
                        portrait_id=saved_portrait.id,
                        update_data={"skills_req": job_profile_data}
                    )
                    log.info(f"簇 {cluster_id} 画像已保存，ID={saved_portrait.id}")

                    # ==================== 步骤 7: 更新 job_info 的 job_profile_id ====================
                    for job in jobs:
                        await job_repo.update(
                            job_id=job.id,
                            update_data={"job_profile_id": saved_portrait.id}
                        )
                        total_jobs_processed += 1

                except Exception as e:
                    log.error(f"处理簇 {cluster_id} 时出错：{e}", exc_info=True)
                    continue

            log.info(f"岗位合并完成！创建 {len(portrait_ids)} 个岗位画像，处理 {total_jobs_processed} 个岗位")

    except Exception as e:
        log.error(f"岗位合并失败：{e}", exc_info=True)
        return error_msg(f"岗位合并失败：{str(e)}")

    finally:
        await engine.dispose()

    return success_msg(f"岗位合并完成！创建 {len(portrait_ids)} 个岗位画像，处理 {total_jobs_processed} 个岗位")