import asyncio
from typing import Any

from fastapi import APIRouter, Depends, BackgroundTasks, Form

from ai_service.response.result import success
from ai_service.schemas.file import handle_file, handle_files
from ai_service.services.extract_text import extract_from_file
from ai_service.services.redis_service import RedisService
from ai_service.services.struct_text_extractor import struct_text_extractor
from ai_service.utils.fingerprint_util import HashAlgorithm, file_fingerprint
from ai_service.utils.logger_handler import log
from config import settings

__all__ = ["router"]
router = APIRouter(prefix="/parse", tags=["parse"])

semaphore = asyncio.Semaphore(3)  # 限制最多 3 个并发
redis = RedisService.get_instance("parse")


@router.post("/file")
async def parse_file(
        file_info=Depends(handle_file),
        cache_enabled: bool = Form(True, alias="cache_enabled"),
        background_tasks: BackgroundTasks = None
):
    cached_results, uncached_infos = [], [file_info]
    if cache_enabled:
        try:
<<<<<<< HEAD
<<<<<<< HEAD
            cached_results, uncached_infos = await get_cache(file_info=file_info)
=======
            cached_results, uncached_infos = await _get_cache(file_info=file_info)
>>>>>>> origin/master
=======
            cached_results, uncached_infos = await _get_cache(file_info=file_info)
>>>>>>> 46c4c4915a8e69a1e650eca09eaaa76221b03829
        except Exception as e:
            log.error(f"获取缓存失败: {e}", exc_info=True)
        if len(uncached_infos) == 0:
            return success(cached_results[0])
<<<<<<< HEAD
<<<<<<< HEAD
    text = await _extract_text_from_file(file_info["save_path"], file_info["extension"])
=======
    text = await extract_from_file(file_info["save_path"], file_info["extension"])
>>>>>>> origin/master
=======
    text = await extract_from_file(file_info["save_path"], file_info["extension"])
>>>>>>> 46c4c4915a8e69a1e650eca09eaaa76221b03829
    result = await struct_text_extractor.extract_from_text_to_user_form(text)
    background_tasks.add_task(_save_cache, [result], uncached_infos)
    return success(result)


@router.post("/files")
async def parse_files(
        file_infos=Depends(handle_files),
        cache_enabled: bool = Form(True, alias="cache_enabled"),
        background_tasks: BackgroundTasks = None
):
    cached_results, uncached_infos = [], file_infos
    if cache_enabled:
        try:
<<<<<<< HEAD
<<<<<<< HEAD
            cached_results, uncached_infos = await get_cache(file_infos=file_infos)
=======
            cached_results, uncached_infos = await _get_cache(file_infos=file_infos)
>>>>>>> origin/master
=======
            cached_results, uncached_infos = await _get_cache(file_infos=file_infos)
>>>>>>> 46c4c4915a8e69a1e650eca09eaaa76221b03829
        except Exception as e:
            log.error(f"获取缓存失败: {e}", exc_info=True)
        if len(uncached_infos) == 0:
            return success(cached_results)
    file_infos = uncached_infos
    async with semaphore:
        texts = await asyncio.gather(*[
            extract_from_file(info["save_path"], info["extension"])
            for info in file_infos
        ])
    results = await asyncio.gather(*[
        struct_text_extractor.extract_from_text_to_user_form(text)
        for text in texts
    ])
    background_tasks.add_task(_save_cache, results, uncached_infos)
    return success(results + cached_results)




async def _get_cache(file_info=None, file_infos=None) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    if not file_info and not file_infos:
        raise ValueError("file_info和file_infos不能同时为空")
    if file_info and file_infos:
        raise ValueError("file_info和file_infos不能同时存在")
    if file_info:
        file_infos = [file_info]
    if not redis.is_available:
        return [], file_infos
    info_list = []
    result = []
    for info in file_infos:
        fingerprint = file_fingerprint(info["save_path"], HashAlgorithm.SHA256)
        if redis.exists(fingerprint):
            result.append(redis.get(fingerprint, ttl=settings.redis.cache_timeout.file_parse))
        else:
            info_list.append(info)
    return result, info_list


def _save_cache(results, info_list: list[dict[str, str]]):
    if len(results) == 0:
        return
    if not redis.is_available:
        return
    for result, info in zip(results, info_list):
        try:
            fingerprint = file_fingerprint(info["save_path"], HashAlgorithm.SHA256)
            redis.set(fingerprint, result, settings.redis.cache_timeout.file_parse)
        except Exception as e:
            log.error(f"保存缓存失败: {e}", exc_info=True)
