import asyncio
from typing import Any

from fastapi import APIRouter, Depends, BackgroundTasks, Form

from ai_service.response.result import success
from ai_service.schemas.file import handle_file, handle_files
from ai_service.services.extract_text import extract_from_file
from ai_service.services.redis_service import RedisService
from ai_service.services.struct_text_extractor import struct_text_extractor
from ai_service.utils.fingerprint_util import HashAlgorithm, file_fingerprint, text_fingerprint
from ai_service.utils.logger_handler import log
from config import settings

__all__ = ["router"]
router = APIRouter(prefix="/parse", tags=["parse"])

semaphore = asyncio.Semaphore(3)  # 限制最多 3 个并发
redis = RedisService.get_instance("parse")
if not redis.is_available:
    log.warning(f"⚠️警告：{__name__}的Redis缓存服务不可用")

@router.post("/file")
async def parse_file(
        file_info=Depends(handle_file),
        cache_enabled: bool = Form(True, alias="cache_enabled"),
        background_tasks: BackgroundTasks = None
):
    if cache_enabled:
        try:
            cache = await _get_cache(file_info=file_info)
            if cache:
                return success(cache)
        except Exception as e:
            log.error(f"获取缓存失败: {e}", exc_info=True)
    text = await extract_from_file(file_info["save_path"], file_info["extension"])
    result = await struct_text_extractor.extract_from_text_to_user_form(text)
    background_tasks.add_task(_save_cache, result, [file_info])
    return success(result)


@router.post("/files")
async def parse_files(
        file_infos=Depends(handle_files),
        cache_enabled: bool = Form(True, alias="cache_enabled"),
        background_tasks: BackgroundTasks = None
):
    if cache_enabled:
        try:
            cache = await _get_cache(file_infos=file_infos)
            if cache:
                return success(cache)
        except Exception as e:
            log.error(f"获取缓存失败: {e}", exc_info=True)
    async with semaphore:
        texts = await asyncio.gather(*[
            extract_from_file(info["save_path"], info["extension"])
            for info in file_infos
        ])
    combined_text = ""
    for text, info in zip(texts, file_infos):
        combined_text += f"\n\n--- 文件分隔 ---\n\n文件名：{info['original_name']}\n\n文件内容：{text}"
    result = await struct_text_extractor.extract_from_text_to_user_form(combined_text)
    if file_infos:
        background_tasks.add_task(_save_cache, result, file_infos)
    return success(result)


async def _get_cache(file_info=None, file_infos=None) -> dict[str, Any]:
    if not file_info and not file_infos:
        raise ValueError("file_info和file_infos不能同时为空")
    if file_info and file_infos:
        raise ValueError("file_info和file_infos不能同时存在")
    if file_info:
        file_infos = [file_info]
    if not redis.is_available:
        return {}
    fingerprint_list = []
    for info in file_infos:
        fingerprint_list.append(file_fingerprint(info["save_path"], HashAlgorithm.SHA256))
    fingerprint_list.sort()
    fingerprint = text_fingerprint("\n".join(fingerprint_list), HashAlgorithm.SHA256)
    if redis.exists(fingerprint):
        return redis.get(fingerprint, ttl=settings.redis.cache_timeout.file_parse)
    else:
        return {}


def _save_cache(result: dict[str, Any], info_list: list[dict[str, str]]) -> None:
    if not redis.is_available:
        return
    fingerprint_list = []
    for info in info_list:
        fingerprint_list.append(file_fingerprint(info["save_path"], HashAlgorithm.SHA256))
    fingerprint_list.sort()
    fingerprint = text_fingerprint("\n".join(fingerprint_list), HashAlgorithm.SHA256)
    try:
        redis.set(fingerprint, result, settings.redis.cache_timeout.file_parse)
    except Exception as e:
        log.error(f"保存缓存失败: {e}", exc_info=True)
