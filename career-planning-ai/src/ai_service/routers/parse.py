import asyncio

from fastapi import APIRouter, Depends

__all__ = ["router"]

from ai_service.exceptions import CommonHandleError
from ai_service.response.result import success
from ai_service.schemas.file import handle_file, handle_files
from ai_service.services.struct_text_extractor import struct_text_extractor
from ai_service.services.image_extractor import image_extractor
from ai_service.services.pdf_extractor import pdf_extractor
from ai_service.services.word_extractor import word_extractor
from config import settings

router = APIRouter(prefix="/parse", tags=["parse"])

semaphore = asyncio.Semaphore(3)  # 限制最多 3 个并发


@router.post("/file")
async def parse_file(file_info=Depends(handle_file)):
    text = await _extract_text_from_file(file_info["save_path"], file_info["extension"])
    return success(await struct_text_extractor.extract_from_text_to_userform(text))


@router.post("/files")
async def parse_files(file_infos=Depends(handle_files)):
    async with semaphore:
        texts = await asyncio.gather(*[
            _extract_text_from_file(info["save_path"], info["extension"])
            for info in file_infos
        ])

    results = await asyncio.gather(*[
        struct_text_extractor.extract_from_text_to_userform(text)
        for text in texts
    ])
    return success(results)


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
