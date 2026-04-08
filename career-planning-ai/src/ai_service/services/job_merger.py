# ai_service/api/job_merge_api.py
import asyncio
from typing import Dict, Any, List, Tuple

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from ai_service.models.job_info import JobInfo
from ai_service.models.job_portrait import JobPortrait
from ai_service.repository.job_info_repository import JobRepository
from ai_service.repository.job_portrait_repository import JobPortraitRepository
from ai_service.response.result import error_msg, success
from ai_service.services.database_manage import get_db_url
from ai_service.services.job_profile_builder import analyze_job_description
from ai_service.utils.HDBSCAN import cluster_standard_jobs_with_hdbscan
from ai_service.utils.logger_handler import log

router = APIRouter()

# 数据库会话配置
engine = create_async_engine(get_db_url(), echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def _analyze_cluster_with_semaphore(
    cluster_id: int,
    jobs: List[JobInfo],
    semaphore: asyncio.Semaphore,
) -> Tuple[int, List[JobInfo], Dict[str, Any]]:
    """
    并发分析单个簇。
    这里只做 LLM 调用，不做数据库写入，避免并发共享 AsyncSession。
    """
    async with semaphore:
        log.info(f"开始分析簇 {cluster_id}，岗位数={len(jobs)}")
        try:
            result = await analyze_job_description(jobs)
            return cluster_id, jobs, result
        except Exception as e:
            log.error(f"簇 {cluster_id} 分析异常：{e}", exc_info=True)
            return cluster_id, jobs, {"error": str(e)}

async def _analyze_cluster(cluster_id: int, jobs: List[JobInfo], semaphore: asyncio.Semaphore) -> Tuple[int, List[JobInfo], Dict[str, Any]]:
    return await _analyze_cluster_with_semaphore(cluster_id, jobs, semaphore)

async def job_merger(max_concurrency: int = 5) -> Dict[str, Any]:
    portrait_ids: List[int] = []
    total_jobs_processed = 0
    noise_jobs = 0
    skipped_small_clusters = 0
    failed_clusters: List[Dict[str, Any]] = []

    try:
        async with AsyncSessionLocal() as session:
            log.info("开始岗位聚类...")
            clustered_result = await cluster_standard_jobs_with_hdbscan(session=session)
            if not clustered_result:
                return error_msg("聚类结果为空，无岗位可合并")

            job_repo = JobRepository(session)
            portrait_repo = JobPortraitRepository(session)

            valid_clusters: List[Tuple[int, List[JobInfo]]] = []
            for cluster_id, jobs in clustered_result.items():
                if cluster_id == -1:
                    noise_jobs = len(jobs)
                    continue
                if len(jobs) < 2:
                    skipped_small_clusters += 1
                    continue
                valid_clusters.append((cluster_id, jobs))

            if not valid_clusters:
                return error_msg("没有可供合并的有效簇")

            semaphore = asyncio.Semaphore(max_concurrency)
            tasks = [_analyze_cluster(cid, jobs, semaphore) for cid, jobs in valid_clusters]
            analysis_results = await asyncio.gather(*tasks)

            # ======= 批量写数据库 =======
            portraits_to_insert = []
            job_updates = []
            for cluster_id, jobs, profile_data in analysis_results:
                if not isinstance(profile_data, dict) or "error" in profile_data:
                    failed_clusters.append({"cluster_id": cluster_id, "error": profile_data.get("error") if isinstance(profile_data, dict) else "invalid_result"})
                    continue
                standard_title = profile_data.get("job_name", "未命名岗位")
                portraits_to_insert.append(JobPortrait(job_title=standard_title, skills_req=profile_data, is_deleted=0))
                job_updates.append((cluster_id, jobs))

            # 批量创建岗位画像
            for portrait in portraits_to_insert:
                saved_portrait = await portrait_repo.create(portrait)
                portrait_ids.append(saved_portrait.id)

            # 批量更新 job_profile_id
            for idx, (cluster_id, jobs) in enumerate(job_updates):
                portrait_id = portrait_ids[idx]

                analysis_results[idx][2]["job_id"] = portrait_id
                await portrait_repo.update(portrait_id, {"skills_req": analysis_results[idx][2]})
                for job in jobs:
                    await job_repo.update(job.id, {"job_id": portrait_id})
                    total_jobs_processed += 1

            log.info(f"岗位合并完成，创建 {len(portrait_ids)} 个岗位画像，处理 {total_jobs_processed} 个岗位")
    finally:
        await engine.dispose()

    return success({
        "message": f"岗位合并完成！创建 {len(portrait_ids)} 个岗位画像，处理 {total_jobs_processed} 个岗位",
        "portrait_count": len(portrait_ids),
        "processed_jobs": total_jobs_processed,
        "noise_jobs": noise_jobs,
    })

# async def job_merger(
#     max_concurrency: int = 5,# 最大并发数("qwen-max": 3~5,# 高价值模型，保守并发 #"qwen-plus": 10~20,# 平衡型"qwen-turbo": 30~50,  # 轻量型，可较高并发）
# ) -> Dict[str, Any]:
#     """
#     进行岗位合并（并发版）
#
#     步骤：
#     1. 调用 cluster_standard_jobs_with_hdbscan 进行岗位聚类
#     2. 对每个有效簇并发调用 analyze_job_description 合并成岗位画像（Semaphore 限流）
#     3. 顺序保存岗位画像到 job_portrait 表
#     4. 顺序更新 job_info 表的 job_profile_id
#
#     说明：
#     - LLM 分析使用 asyncio.gather 并发执行
#     - 数据库写入仍然顺序执行，避免多个协程并发共用同一个 AsyncSession
#     """
#     portrait_ids: List[int] = []
#     total_jobs_processed = 0
#     noise_jobs = 0
#     skipped_small_clusters = 0
#     failed_clusters: List[Dict[str, Any]] = []
#
#     try:
#         async with AsyncSessionLocal() as session:
#             # ==================== 步骤 1: 岗位聚类 ====================
#             log.info("开始岗位聚类...")
#             clustered_result: Dict[int, List[JobInfo]] = await cluster_standard_jobs_with_hdbscan(
#                 session=session
#             )
#
#             if not clustered_result:
#                 log.warning("聚类结果为空，无岗位可合并")
#                 return error_msg("聚类结果为空，无岗位可合并")
#
#             job_repo = JobRepository(session)
#             portrait_repo = JobPortraitRepository(session)
#
#             # ==================== 步骤 2: 准备可并发处理的簇 ====================
#             log.info("准备可供并发分析的簇...")
#             valid_clusters: List[Tuple[int, List[JobInfo]]] = []
#             for cluster_id, jobs in clustered_result.items():
#                 if cluster_id == -1:
#                     noise_jobs = len(jobs)
#                     log.info(f"跳过噪声簇，共 {noise_jobs} 个岗位")
#                     continue
#
#                 if len(jobs) < 2:
#                     skipped_small_clusters += 1
#                     log.warning(f"簇 {cluster_id} 只有 {len(jobs)} 个岗位，跳过合并")
#                     continue
#
#                 valid_clusters.append((cluster_id, jobs))
#
#             if not valid_clusters:
#                 log.warning("没有可供合并的有效簇")
#                 return error_msg("没有可供合并的有效簇")
#
#             # ==================== 步骤 3: 并发执行 LLM 分析 ====================
#             semaphore = asyncio.Semaphore(max_concurrency)
#             tasks = [
#                 _analyze_cluster_with_semaphore(cluster_id, jobs, semaphore)
#                 for cluster_id, jobs in valid_clusters
#             ]
#
#             log.info(
#                 f"开始并发分析 {len(tasks)} 个簇，最大并发数={max_concurrency}"
#             )
#             analysis_results = await asyncio.gather(*tasks, return_exceptions=True)
#
#             # ==================== 步骤 4: 顺序写入数据库 ====================
#             for item in analysis_results:
#                 if isinstance(item, Exception):
#                     log.error(f"并发任务执行失败：{item}", exc_info=True)
#                     failed_clusters.append({"cluster_id": None, "error": str(item)})
#                     continue
#
#                 cluster_id, jobs, job_profile_data = item
#
#                 if not isinstance(job_profile_data, dict):
#                     log.error(f"簇 {cluster_id} 返回结果不是 dict，已跳过")
#                     failed_clusters.append(
#                         {"cluster_id": cluster_id, "error": "返回结果不是 dict"}
#                     )
#                     continue
#
#                 if "error" in job_profile_data:
#                     log.error(f"簇 {cluster_id} 分析失败：{job_profile_data['error']}")
#                     failed_clusters.append(
#                         {"cluster_id": cluster_id, "error": job_profile_data["error"]}
#                     )
#                     continue
#
#                 try:
#                     standard_title = job_profile_data.get("job_name", "未命名岗位")
#
#                     portrait = JobPortrait(
#                         job_title=standard_title,
#                         skills_req=job_profile_data,
#                         is_deleted=0,
#                     )
#
#                     saved_portrait = await portrait_repo.create(portrait)
#                     portrait_ids.append(saved_portrait.id)
#
#                     job_profile_data["job_id"] = saved_portrait.id
#                     await portrait_repo.update(
#                         portrait_id=saved_portrait.id,
#                         update_data={"skills_req": job_profile_data},
#                     )
#                     log.info(f"簇 {cluster_id} 画像已保存，ID={saved_portrait.id}")
#
#                     for job in jobs:
#                         await job_repo.update(
#                             job_id=job.id,
#                             update_data={"job_profile_id": saved_portrait.id},
#                         )
#                         total_jobs_processed += 1
#
#                 except Exception as e:
#                     log.error(f"处理簇 {cluster_id} 的数据库写入时出错：{e}", exc_info=True)
#                     failed_clusters.append({"cluster_id": cluster_id, "error": str(e)})
#                     continue
#
#             log.info(
#                 f"岗位合并完成！创建 {len(portrait_ids)} 个岗位画像，"
#                 f"处理 {total_jobs_processed} 个岗位，噪声岗位 {noise_jobs} 个，"
#                 f"跳过小簇 {skipped_small_clusters} 个，失败簇 {len(failed_clusters)} 个"
#             )
#
#     except Exception as e:
#         log.error(f"岗位合并失败：{e}", exc_info=True)
#         return error_msg(f"岗位合并失败：{str(e)}")
#
#     finally:
#         await engine.dispose()
#
#     return success(
#         {
#             "message": f"岗位合并完成！创建 {len(portrait_ids)} 个岗位画像，处理 {total_jobs_processed} 个岗位",
#             "portrait_count": len(portrait_ids),
#             "processed_jobs": total_jobs_processed,
#             "noise_jobs": noise_jobs,
#         }
#     )

if __name__ == "__main__":
    asyncio.run(job_merger())