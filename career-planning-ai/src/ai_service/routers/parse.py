import asyncio

from fastapi import APIRouter, Depends

__all__ = ["router"]

from ai_service.exceptions import CommonHandleError
from ai_service.response.result import success
from ai_service.schemas.file import validate_pdf, validate_some_pdf, validate_docx, validate_some_docx, validate_image, \
    validate_some_image
from ai_service.services.image_extractor import image_extractor
from ai_service.services.pdf_extractor import pdf_extractor
from ai_service.services.struct_text_extractor import struct_text_extractor
from ai_service.services.word_extractor import word_extractor

router = APIRouter(prefix="/parse", tags=["parse"])


@router.post("/pdf")
async def parse_pdf(file_info=Depends(validate_pdf)):
    file_path = file_info["save_path"]
    return success(await _extract_structured_data_from_pdf(file_path))


@router.post("/pdfs")
async def parse_pdfs(file_infos=Depends(validate_some_pdf)):
    tasks = [
        _extract_structured_data_from_pdf(file_info["save_path"])
        for file_info in file_infos
    ]
    result = await asyncio.gather(*tasks)
    return success(result)


@router.post("/doc")
async def parse_doc(file_info=Depends(validate_docx)):
    file_path = file_info["save_path"]
    text = await word_extractor.detect_word_to_enhance_text(file_path)
    return success(await struct_text_extractor.extract_from_text_to_json(text))


@router.post("/docs")
async def parse_docs(file_infos=Depends(validate_some_docx)):
    tasks = [
        word_extractor.detect_word_to_enhance_text(file_info["save_path"])
        for file_info in file_infos
    ]
    result = await asyncio.gather(*tasks)
    tasks = [
        struct_text_extractor.extract_from_text_to_json(text)
        for text in result
    ]
    result = await asyncio.gather(*tasks)
    return success(result)


@router.post("/image")
async def parse_image(file_info=Depends(validate_image)):
    file_path = file_info["save_path"]
    text = await image_extractor.extract_text(image_path=file_path)
    return success(await struct_text_extractor.extract_from_text_to_json(text))


@router.post("/images")
async def parse_images(file_infos=Depends(validate_some_image)):
    tasks = [
        image_extractor.extract_text(image_path=file_info["save_path"])
        for file_info in file_infos
    ]
    result = await asyncio.gather(*tasks)
    tasks = [
        struct_text_extractor.extract_from_text_to_json(text)
        for text in result
    ]
    result = await asyncio.gather(*tasks)
    return success(result)


async def _extract_structured_data_from_pdf(file_path: str) -> dict:
    """
    从 PDF 文件提取结构化数据

    Args:
        file_path: PDF 文件路径

    Returns:
        结构化数据字典
    """
    content = await pdf_extractor.get_pdf_content(file_path)
    if not content:
        raise CommonHandleError("PDF 文件提取失败")
    text = ""
    for page in content:
        if not page.get("error"):
            text += f"第{page['page']}页：{page['content']}\n"
    return await struct_text_extractor.extract_from_text_to_json(text)
