import asyncio
from typing import Any

from fastapi import APIRouter, Depends, BackgroundTasks

from ai_service.exceptions import CommonHandleError
from ai_service.response.result import success
from ai_service.schemas.file import handle_file, handle_files
from ai_service.services.redis_service import RedisService
from ai_service.services.struct_text_extractor import struct_text_extractor
from ai_service.services.image_extractor import image_extractor
from ai_service.services.pdf_extractor import pdf_extractor
from ai_service.services.word_extractor import word_extractor
from ai_service.utils.fingerprint_util import HashAlgorithm, file_fingerprint
from ai_service.utils.logger_handler import log
from config import settings

__all__ = ["router"]
router = APIRouter(prefix="/parse", tags=["parse"])

semaphore = asyncio.Semaphore(3)  # 限制最多 3 个并发
redis = RedisService.get_instance("parse")


@router.post("/file")
async def parse_file(file_info=Depends(handle_file), background_tasks: BackgroundTasks = None):
    try:
        cached_results, uncached_infos = await get_cache(file_info=file_info)
    except Exception as e:
        log.error(f"获取缓存失败: {e}", exc_info=True)
        cached_results, uncached_infos = [], [file_info]
    if len(uncached_infos) == 0:
        return success(cached_results[0])
    text = await _extract_text_from_file(file_info["save_path"], file_info["extension"])
    result = await struct_text_extractor.extract_from_text_to_user_form(text)
    background_tasks.add_task(save_cache, [result], uncached_infos)
    return success(result)


@router.post("/files")
async def parse_files(file_infos=Depends(handle_files), background_tasks: BackgroundTasks = None):
    try:
        cached_results, uncached_infos = await get_cache(file_infos=file_infos)
    except Exception as e:
        log.error(f"获取缓存失败: {e}", exc_info=True)
        cached_results, uncached_infos = [], file_infos
    if len(uncached_infos) == 0:
        return success(cached_results)
    file_infos = uncached_infos
    async with semaphore:
        texts = await asyncio.gather(*[
            _extract_text_from_file(info["save_path"], info["extension"])
            for info in file_infos
        ])
    results = await asyncio.gather(*[
        struct_text_extractor.extract_from_text_to_user_form(text)
        for text in texts
    ])
    background_tasks.add_task(save_cache, results, uncached_infos)
    return success(results + cached_results)


async def _extract_text_from_file(file_path: str, extension: str) -> str:
    """
    从文件提取文本内容

    Args:
        file_path: 文件路径
        extension: 文件扩展名

    Returns:
        提取的文本内容
    """
    if extension == "pdf":
        content = await pdf_extractor.get_pdf_content(file_path)
        if not content:
            raise CommonHandleError("PDF 文件提取失败")
        text = ""
        for page in content:
            if not page.get("error"):
                text += f"第{page['page']}页：{page['content']}\n"
        return text

    elif extension in ["doc", "docx"]:
        return await word_extractor.detect_word_to_enhance_text(file_path)

    elif extension.lower() in [suffix.lower() for suffix in settings.image.suffix]:
        return await image_extractor.extract_text(image_path=file_path)

    else:
        raise CommonHandleError(f"不支持的文件类型: {extension}")


async def get_cache(file_info=None, file_infos=None) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
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
            result.append(redis.get(fingerprint))
        else:
            info_list.append(info)
    return result, info_list


def save_cache(results, info_list: list[dict[str, str]]):
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
