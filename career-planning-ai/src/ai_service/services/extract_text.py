from ai_service.exceptions import CommonHandleError
from ai_service.services.image_extractor import image_extractor
from ai_service.services.pdf_extractor import pdf_extractor
from ai_service.services.word_extractor import word_extractor
from config import settings


async def extract_from_file(file_path: str, extension: str) -> str:
    """
    从文件提取文本内容

    Args:
        file_path: 文件路径
        extension: 文件扩展名

    Returns:
        提取的文本内容
    """
    if extension.lower() in [suffix.lower() for suffix in settings.pdf.suffix]:
        content = await pdf_extractor.get_pdf_content(file_path)
        if not content:
            raise CommonHandleError(msg="PDF 文件提取失败")
        text = ""
        for page in content:
            if not page.get("error"):
                text += f"第{page['page']}页：{page['content']}\n"
        return text

    elif extension.lower() in [suffix.lower() for suffix in settings.other.word_file_suffix]:
        return await word_extractor.detect_word_to_enhance_text(file_path)

    elif extension.lower() in [suffix.lower() for suffix in settings.image.suffix]:
        return await image_extractor.extract_text(image_path=file_path)

    elif extension.lower() in [suffix.lower() for suffix in settings.other.text_file_suffix]:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    else:
        raise CommonHandleError(msg=f"不支持的文件类型: {extension}")
