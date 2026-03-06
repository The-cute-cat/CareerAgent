from pathlib import Path

from PIL import Image
from langchain_openai import ChatOpenAI

from ai_service.utils.logger_handler import log
from config import settings


class ImageExtractor:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.llm.api_key.get_secret_value(),
            base_url=settings.llm.base_url,
            timeout=settings.llm.timeout,
            max_retries=settings.llm.max_retries,
            model=settings.pdf.model_name
        )

    @staticmethod
    def validate_image(image_path: str) -> dict:
        raise Exception("正在开发中")
        result = {
            "valid": False,
            "format": None,
            "size": 0,
            "dimensions": (0, 0),
        }
        try:
            path = Path(image_path)
            if not path.exists():
                log.warning(f"文件不存在: {image_path}")
                return result
            if not path.is_file():
                log.warning(f"不是文件: {image_path}")
                return result
            size = path.stat().st_size
            result["size"] = size
            if size > settings.image.max_size * 1024 * 1024:
                log.warning(f"文件大小过大: {size} > {settings.image.max_size} MB")
                return result
            with Image.open(path) as img:
                result["format"] = img.format
                width, height = img.size
                result["dimensions"] = (width, height)
                if width > settings.image.max_dimension or height > settings.image.max_dimension:
                    log.warning(f"图片尺寸过大: {width}x{height} > {settings.image.max_dimension}x{settings.image.max_dimension}")
                    return result
                if img.format not in settings.image.suffix:
                    log.warning(f"图片格式不支持: {img.format}")
                    return result
            result["valid"] = True
        except Exception as e:
            log.error(f"验证图片失败: {e}", exc_info=True)
        return result

    def preprocess_image(self,image_path: str):
        raise Exception("正在开发中")
        ...
