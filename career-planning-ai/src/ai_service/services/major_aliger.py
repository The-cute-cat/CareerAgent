from rapidfuzz import process, utils
from functools import lru_cache
from pathlib import Path

__all__ = ["major_aligner"]


class MajorAligner:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        # 1. 启动时一次性加载文件到内存（提速关键）
        self.standard_majors = self._load_file()
        print(f"[MajorAligner] 成功加载 {len(self.standard_majors)} 条标准专业数据")

    def _load_file(self) -> list[str]:
        """读取 txt 文件并清洗数据"""
        if not self.file_path.exists():
            print(f"错误: 找不到文件 {self.file_path}")
            return []

        with open(self.file_path, "r", encoding="utf-8") as f:
            # 去除空行和首尾空格
            return [line.strip() for line in f if line.strip()]

    @lru_cache(maxsize=1024)
    def align(self, query: str, score_cutoff: float = 70.0) -> str:
        """
        执行模糊匹配
        query: AI 提取出的原始专业名（如 "计科"）
        score_cutoff: 相似度阈值（0-100），低于此分返回原词
        """
        if not query or query == "无":
            return query

        # 2. 第一层：尝试完全匹配（0耗时）
        if query in self.standard_majors:
            return query

        # 3. 第二层：RapidFuzz 模糊匹配
        # 返回格式: (匹配到的字符串, 分数, 索引)
        result = process.extractOne(
            query,
            self.standard_majors,
            processor=utils.default_process,  # 自动转小写、去标点、处理空格
            score_cutoff=score_cutoff,
        )

        if result:
            matched_name, score, _ = result
            # print(f"匹配成功: {query} -> {matched_name} (分数: {score:.2f})")
            return matched_name

        # 4. 第三层：匹配不到则返回原词
        return query


# --- 初始化单例 ---
# 假设 major.txt 放在 resources 文件夹下
major_aligner = MajorAligner("data\\major.txt")
