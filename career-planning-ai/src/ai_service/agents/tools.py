from langchain_core.tools import tool

from ai_service.services.chroma_service import ChromaService
from config import settings

__all__ = [
    "query_project",
]

@tool(
    description="""开源项目推荐工具。根据用户的技术栈、学习目标或项目需求，从向量数据库中检索最匹配的开源项目。

适用场景：
- 用户想要学习某个技术栈，需要推荐实战项目
- 用户想找适合做毕设/简历亮点的项目
- 用户想找某个业务领域（电商、博客、后台管理等）的开源项目
- 用户想了解某个难度等级（初级/进阶/高级）的项目

输入：自然语言查询描述
输出：匹配的项目列表，包含项目名称、技术标签、适用场景、难度、星数、地址等信息"""
)
def query_project(query: str, top_k: int = settings.chroma_config.k) -> list[dict]:
    """
    查询开源项目推荐，根据用户需求从向量数据库中检索最匹配的项目。

    Args:
        query: 查询描述，如 "Java 后台管理系统"、"电商项目"、"微服务架构学习"
        top_k: 返回结果数量，默认 5

    Returns:
        匹配的项目列表，每项包含:
        - name: 项目名称
        - score: 相似度分数 (越小越相似)
        - description: 项目简介
        - tech_tags: 技术标签
        - use_cases: 适用场景
        - difficulty: 难度等级
        - stars: GitHub/Gitee 星数
        - url: 项目地址
    """
    service = ChromaService.get_instance(settings.chroma_config.collection_name.project_collection)
    results = service.similarity_search_with_score(query, k=top_k)

    projects = []
    for doc, score in results:
        meta = doc.metadata
        projects.append({
            "name": meta.get("name", "Unknown"),
            "score": round(score, 4),
            "description": meta.get("description", ""),
            "content": doc.page_content,  # 项目详细说明
            "tech_tags": meta.get("tech_tags", ""),
            "use_cases": meta.get("use_cases", ""),
            "difficulty": meta.get("difficulty", "进阶"),
            "stars": meta.get("stars", 0),
            "language": meta.get("language", ""),
            "url": doc.metadata.get("source", "") == "github"
                   and f"https://github.com/{meta.get('full_name', '')}"
                   or f"https://gitee.com/{meta.get('full_name', '')}"
        })

    return projects


def query_learning_path(skill: str, difficulty: str = "进阶") -> dict:
    """
    查询某技能的学习路径，推荐课程、书籍、文档等资源。

    Args:
        skill: 技能名称，如 "Spring Boot", "Vue3", "MySQL优化"
        difficulty: 难度等级

    Returns:
        - recommended_courses: 推荐课程列表
        - recommended_books: 推荐书籍
        - estimated_time: 预估学习时长
    """


if __name__ == "__main__":
    ...
