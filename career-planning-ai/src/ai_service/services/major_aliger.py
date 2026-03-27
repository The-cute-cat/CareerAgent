import os
from functools import lru_cache
from pathlib import Path

from rapidfuzz import process, utils

__all__ = ["major_aligner"]

from ai_service.services import log
from config import settings


class MajorAligner:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.standard_majors = self._load_file()
        log.info(f"[MajorAligner] 成功加载 {len(self.standard_majors)} 条标准专业数据")

    def _load_file(self) -> list[str]:
        """读取 txt 文件并清洗数据"""
        if not self.file_path.exists():
            log.error(f"错误: 找不到文件 {self.file_path}")
            return []

        with open(self.file_path, "r", encoding="utf-8") as f:
            # 去除空行和首尾空格
            return [line.strip() for line in f if line.strip()]

    def align_list(self, queries: list[str], score_cutoff: float = 70.0) -> list[str]:
        """批量对齐专业名称"""
        return [self.align(query, score_cutoff) for query in queries]

    @lru_cache(maxsize=1024)
    def align(self, query: str, score_cutoff: float = 70.0) -> str:
        """
        执行模糊匹配
        query: AI 提取出的原始专业名（如 "计科"）
        score_cutoff: 相似度阈值（0-100），低于此分返回原词
        """
        if not query or query == "无":
            return query

        if query in self.standard_majors:
            return query

        result = process.extractOne(
            query,
            self.standard_majors,
            processor=utils.default_process,  # 自动转小写、去标点、处理空格
            score_cutoff=score_cutoff,
        )

        if result:
            matched_name, score, _ = result
            # log.info(f"匹配成功: {query} -> {matched_name} (分数: {score:.2f})")
            return matched_name
        return query


major_aligner = MajorAligner(os.path.join(settings.path_config.data, "major.txt"))
