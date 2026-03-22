"""
图片文本提取模块

提供图片验证、预处理及文本提取功能，支持通过视觉模型识别图片中的文字内容。
"""

import base64
import time
from pathlib import Path

from PIL import Image
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from ai_service.services.prompt_loader import prompt_loader
from ai_service.utils.logger_handler import log
from config import settings

__all__ = ["image_extractor"]


class ImageExtractor:
    """图片文本提取器，封装图片验证、预处理和 OCR 文本提取功能"""

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.llm.api_key.get_secret_value(),
            base_url=settings.llm.base_url,
            timeout=settings.llm.timeout,
            max_retries=settings.llm.max_retries,
            model=settings.image.model_name,
            temperature=settings.image.extra["temperature"]
        )

    @staticmethod
    async def validate_image(image_path: str) -> dict[str, None | bool | str | int | tuple[int, int]]:
        """
        验证图片文件是否符合处理要求

        检查文件是否存在、大小是否超限、尺寸是否过大、格式是否支持。

        Args:
            image_path: 图片文件路径

        Returns:
            dict: 包含验证结果的字典
                - valid: 是否通过验证
                - format: 图片格式（如 JPEG、PNG）
                - size: 文件大小（字节）
                - dimensions: 图片尺寸 (宽, 高)
                - preprocessed: 是否需要预处理（尺寸或大小超限时为 True）
        """
        result = {
            "valid": False,
            "format": None,
            "size": 0,
            "dimensions": (0, 0),
            "preprocessed": False,
        }
        try:
            path = Path(image_path)
            # 检查文件是否存在
            if not path.exists():
                log.warning(f"文件不存在: {image_path}")
                return result
            # 检查是否为文件
            if not path.is_file():
                log.warning(f"不是文件: {image_path}")
                return result

            # 检查文件大小
            size = path.stat().st_size
            result["size"] = size
            if size > settings.image.max_size * 1024 * 1024:
                log.warning(f"文件大小过大: {size}B > {settings.image.max_size} MB")
                result["preprocessed"] = True

            # 检查图片属性
            with Image.open(path) as img:
                result["format"] = img.format
                width, height = img.size
                result["dimensions"] = (width, height)

                # 检查图片尺寸
                if width > settings.image.max_dimension or height > settings.image.max_dimension:
                    log.warning(
                        f"图片尺寸过大: {width}x{height} > {settings.image.max_dimension}x{settings.image.max_dimension}")
                    result["preprocessed"] = True

                # 检查图片格式是否支持
                if img.format not in [s.upper() for s in settings.image.suffix]:
                    log.warning(f"图片格式不支持: {img.format}")
                    return result

            result["valid"] = True
        except Exception as e:
            log.error(f"验证图片失败: {e}", exc_info=True)
        return result

    @staticmethod
    async def preprocess_image(image_path: str) -> None:
        """
        预处理图片：调整尺寸和压缩大小

        将图片转换为 RGB 模式，缩放到允许的最大尺寸，并通过降低 JPEG 质量
        压缩文件大小直到满足限制。

        Args:
            image_path: 图片文件路径（将原地修改）

        Raises:
            ValueError: 当质量降至 50 仍无法满足大小时抛出
        """
        with Image.open(image_path) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")

            img.thumbnail((settings.image.max_dimension, settings.image.max_dimension), Image.Resampling.LANCZOS)

            quality = 99
            while Path(image_path).stat().st_size > settings.image.max_size * 1024 * 1024:
                img.save(image_path, "JPEG", quality=quality)
                quality -= 1
                if quality == 50:
                    raise ValueError("图片尺寸过于大，无法处理")

    @staticmethod
    def _image_to_base64(image_bytes: bytes) -> str:
        """将图片字节数据转换为 Base64 编码字符串"""
        return base64.b64encode(image_bytes).decode("utf-8")

    async def _identify_image(self, image_path: str = None, image_bytes: bytes = None, prompt: str = "",
                              llm: ChatOpenAI = None) -> str | None:
        if not image_path and not image_bytes:
            log.warning("请传入图片路径或图片字节数组")
            raise ValueError("请传入图片路径或图片字节数组")
        if not llm:
            log.warning("请传入 LLM 实例")
            raise ValueError("请传入 LLM 实例")
        if not prompt:
            log.warning("请传入提示词")
            raise ValueError("请传入提示词")

        start_time = time.time()

        # 从文件读取图片数据
        if not image_bytes and image_path:
            with open(image_path, "rb") as f:
                image_bytes = f.read()

        base64_image = self._image_to_base64(image_bytes)

        # 构造多模态消息（文本 + 图片）
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ]
        )
        try:
            # 调用视觉模型提取文本
            response = llm.invoke([message])
            end_time = time.time()

            log.info(f"耗时: {end_time - start_time}秒；response_metadata:{response.response_metadata}")
            return response.content
        except Exception as e:
            log.warning(f"Failed to extract page content: {e}", exc_info=True)
            return None

    async def extract_text(self, image_path: str = None, image_bytes: bytes = None, prompt: str = "",
                           llm: ChatOpenAI = None) -> str | None:
        """
        使用视觉模型提取图片中的文本内容

        Args:
            image_path: 图片文件路径，与 image_bytes 二选一
            image_bytes: 图片字节数据，与 image_path 二选一
            prompt: 自定义提示词，为空时使用默认提示词
            llm: 自定义 LLM 实例，为空时使用初始化时的实例

        Returns:
            str | None: 提取的文本内容，失败时返回 None

        Raises:
            ValueError: 未提供图片路径或字节数据时抛出
        """
        r = await self.validate_image(image_path)
        if not r["valid"] and not r["preprocessed"]:
            log.warning(f"图片验证失败: {r}")
            raise ValueError("图片验证失败")
        if r["preprocessed"]:
            await self.preprocess_image(image_path)
        if not image_path and not image_bytes:
            log.warning("请传入图片路径或图片字节数组")
            raise ValueError("请传入图片路径或图片字节数组")
        return await self._identify_image(
            image_path,
            image_bytes,
            prompt if prompt else prompt_loader.image_extract_text,
            llm if llm else self.llm
        )

    async def extract_visual_content(self, image_path: str = None, image_bytes: bytes = None, prompt: str = "",
                                     llm: ChatOpenAI = None):
        if not image_path and not image_bytes:
            log.warning("请传入图片路径或图片字节数组")
            raise ValueError("请传入图片路径或图片字节数组")
        return await self._identify_image(
            image_path,
            image_bytes,
            prompt if prompt else prompt_loader.image_extract_visual_content,
            llm if llm else self.llm
        )


image_extractor = ImageExtractor()
