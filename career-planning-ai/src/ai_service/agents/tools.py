"""
资源检索工具集

设计原则：
1. 返回资源 ID，供后续查库获取完整信息
2. 仅返回必要字段供 AI 理解资源内容
3. 所有工具统一返回格式：{id, type, summary, ...}
"""
from typing import Dict, Any
from langchain_core.tools import tool

from ai_service.models.growth_plan import GrowthPlan
from ai_service.services.chroma_service import ChromaService
from config import settings

__all__ = [
    "query_project",
    "query_books",
    "query_intern",
    "query_videos",
    "get_resources_by_ids",
    "submit_growth_plan",
]


@tool(
    description="""开源项目推荐工具。根据技术栈、学习目标检索匹配的开源项目。

返回：项目ID、名称、技术标签、难度等关键信息。
后续可通过ID查询获取完整项目详情（包括URL、描述等）。"""
)
def query_project(query: str, top_k: int = settings.chroma_config.k) -> list[dict]:
    """查询开源项目，返回 ID 和摘要信息"""
    service = ChromaService.get_instance(settings.chroma_config.collection_name.project_collection)
    results = service.similarity_search_with_score(query, k=min(top_k, 10))

    projects = []
    for doc, score in results:
        meta = doc.metadata
        projects.append({
            "id": doc.id,  # Chroma 文档 ID
            "type": "project",
            "name": meta.get("name", "Unknown"),
            "tech_tags": meta.get("tech_tags", ""),
            "difficulty": meta.get("difficulty", "进阶"),
            "stars": meta.get("stars", 0),
            "language": meta.get("language", ""),
            "score": round(score, 4),
            "summary": doc.page_content[:200] if doc.page_content else "",
        })
    return projects


@tool(
    description="""书籍推荐工具。根据学习需求、技术方向检索匹配的书籍。

返回：书籍ID、书名、作者、评分等关键信息。
后续可通过ID查询获取完整书籍详情（包括URL、封面、简介等）。"""
)
def query_books(query: str, top_k: int = settings.chroma_config.k) -> list[dict]:
    """查询书籍，返回 ID 和摘要信息"""
    service = ChromaService.get_instance(settings.chroma_config.collection_name.book_collection)
    results = service.similarity_search_with_score(query, k=min(top_k, 10))

    books = []
    for doc, score in results:
        meta = doc.metadata
        books.append({
            "id": doc.id,
            "type": "book",
            "title": meta.get("title", "Unknown"),
            "author": meta.get("author", ""),
            "publisher": meta.get("publisher", ""),
            "rating_score": meta.get("rating_score", ""),
            "category": meta.get("category", ""),
            "score": round(score, 4),
            "summary": doc.page_content[:200] if doc.page_content else "",
        })
    return books


@tool(
    description="""实习岗位推荐工具。根据求职意向、技术栈检索匹配的实习岗位。

返回：岗位ID、职位名称、公司、城市等关键信息。
后续可通过ID查询获取完整岗位详情（包括URL、薪资、要求等）。"""
)
def query_intern(query: str, top_k: int = settings.chroma_config.k) -> list[dict]:
    """查询实习岗位，返回 ID 和摘要信息"""
    service = ChromaService.get_instance(settings.chroma_config.collection_name.intern_collection)
    results = service.similarity_search_with_score(query, k=min(top_k, 10))

    interns = []
    for doc, score in results:
        meta = doc.metadata
        interns.append({
            "id": doc.id,
            "type": "intern",
            "job_title": meta.get("jobTitle", "Unknown"),
            "company_name": meta.get("company_name", ""),
            "city": meta.get("city", ""),
            "tech_stack": meta.get("techStack", ""),
            "job_type": meta.get("jobType", ""),
            "score": round(score, 4),
            "summary": doc.page_content[:200] if doc.page_content else "",
        })
    return interns


@tool(
    description="""视频课程推荐工具。根据学习需求、技术方向检索匹配的视频课程。

返回：视频ID、标题、作者、播放量等关键信息。
后续可通过ID查询获取完整视频详情（包括URL、封面、时长等）。"""
)
def query_videos(query: str, top_k: int = settings.chroma_config.k) -> list[dict]:
    """查询视频课程，返回 ID 和摘要信息"""
    service = ChromaService.get_instance(settings.chroma_config.collection_name.video_collection)
    results = service.similarity_search_with_score(query, k=min(top_k, 10))

    videos = []
    for doc, score in results:
        meta = doc.metadata
        videos.append({
            "id": doc.id,
            "type": "video",
            "title": meta.get("title", "Unknown"),
            "author": meta.get("author", ""),
            "category_name": meta.get("category_name", ""),
            "play_count": meta.get("play_count", "0"),
            "duration": meta.get("duration", ""),
            "score": round(score, 4),
            "summary": doc.page_content[:200] if doc.page_content else "",
        })
    return videos


def get_resources_by_ids(resource_refs: list[dict]) -> dict[str, list[dict]]:
    """
    根据资源引用批量查询完整资源信息

    Args:
        resource_refs: 资源引用列表，每项包含 {id, type}

    Returns:
        按类型分组的完整资源信息
        {
            "books": [...],
            "videos": [...],
            "projects": [...],
            "interns": [...]
        }
    """
    # 按类型分组
    by_type = {"book": [], "video": [], "project": [], "intern": []}
    for ref in resource_refs:
        rtype = ref.get("type", "")
        rid = ref.get("id", "")
        if rtype in by_type and rid:
            by_type[rtype].append(rid)

    results = {"books": [], "videos": [], "projects": [], "interns": []}

    # 批量查询各类型资源
    if by_type["book"]:
        service = ChromaService.get_instance(settings.chroma_config.collection_name.book_collection)
        data = service.get(ids=by_type["book"])
        results["books"] = _format_books(data)

    if by_type["video"]:
        service = ChromaService.get_instance(settings.chroma_config.collection_name.video_collection)
        data = service.get(ids=by_type["video"])
        results["videos"] = _format_videos(data)

    if by_type["project"]:
        service = ChromaService.get_instance(settings.chroma_config.collection_name.project_collection)
        data = service.get(ids=by_type["project"])
        results["projects"] = _format_projects(data)

    if by_type["intern"]:
        service = ChromaService.get_instance(settings.chroma_config.collection_name.intern_collection)
        data = service.get(ids=by_type["intern"])
        results["interns"] = _format_interns(data)

    return results


@tool(
    description="""成长计划提交工具。**这是最终提交步骤**，用于校验成长计划字段是否完整合规。

**完整字段规范（所有字段必填）**：

```json
{
  "student_summary": "学生背景概述（必填）",
  "target_position": "目标岗位名称（必填）",
  "current_gap": "当前与目标的主要差距（必填）",
  "short_term_plan": {
    "duration": "如'1-3个月'（必填）",
    "goal": "短期核心目标（必填）",
    "focus_areas": ["重点提升领域1", "重点提升领域2"]（必填，数组）,
    "milestones": [{
      "milestone_name": "里程碑名称（必填）",
      "target_date": "目标时间如'第1个月末'（必填）",
      "key_results": ["成果1", "成果2"]（必填，数组）,
      "tasks": [{
        "task_name": "任务名称（必填）",
        "description": "具体要做什么（必填）",
        "priority": "高/中/低（必填）",
        "estimated_time": "如'2周'（必填）",
        "skill_target": "要提升的技能点（必填）",
        "success_criteria": "如何判断完成（必填）",
        "resources": [{"id": "xxx", "type": "book/video/project/intern", "name": "名称", "reason": "推荐理由"}]
      }]
    }],
    "quick_wins": ["快速成果1", "快速成果2"]
  },
  "mid_term_plan": {
    "duration": "如'3-12个月'（必填）",
    "goal": "中期核心目标（必填）",
    "skill_roadmap": ["技能1", "技能2"]（必填，数组）,
    "milestones": [{同上结构}],
    "career_progression": "预期达到的职业水平（必填）",
    "recommended_internships": [{"id": "xxx", "type": "intern", "name": "岗位名", "reason": "推荐理由"}]
  },
  "action_checklist": ["行动项1", "行动项2"],
  "tips": ["建议1", "建议2"]
}
```

**关键约束**：
1. 必须先完成资源检索，resources 中的 id 必须来自工具返回
2. 所有标记"必填"的字段不可省略或为空
3. 数组字段至少包含一个元素"""
)
def submit_growth_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    提交最终的职业成长计划（仅校验字段）
    
    Args:
        plan: 完整的成长计划字典，必须符合 GrowthPlan 模型结构
        
    Returns:
        仅返回成功/失败状态，不返回计划内容
    """
    try:
        # 验证并解析为 GrowthPlan 模型（仅校验字段）
        GrowthPlan(**plan)
        return {
            "status": "success",
            "message": "成长计划校验通过"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"成长计划校验失败: {str(e)}",
            "error_type": type(e).__name__
        }


# noinspection SpellCheckingInspection
def _format_books(data) -> list[dict]:
    """格式化书籍数据"""
    if not data or not data.get("ids"):
        return []
    books = []
    for i, doc_id in enumerate(data["ids"]):
        meta = data["metadatas"][i] if data.get("metadatas") else {}
        books.append({
            "id": doc_id,
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "translator": meta.get("translator", ""),
            "publisher": meta.get("publisher", ""),
            "publish_date": meta.get("publish_date", ""),
            "category": meta.get("category", ""),
            "keyword": meta.get("keyword", ""),
            "isbn": meta.get("isbn", ""),
            "pages": meta.get("pages", ""),
            "url": meta.get("url", ""),
            "cover_url": meta.get("cover_url", ""),
            "rating_score": meta.get("rating_score", ""),
            "content": data["documents"][i] if data.get("documents") else "",
        })
    return books


# noinspection SpellCheckingInspection
def _format_videos(data) -> list[dict]:
    """格式化视频数据"""
    if not data or not data.get("ids"):
        return []
    videos = []
    for i, doc_id in enumerate(data["ids"]):
        meta = data["metadatas"][i] if data.get("metadatas") else {}
        videos.append({
            "id": doc_id,
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "url": meta.get("url", ""),
            "cover_image": meta.get("cover_image", ""),
            "category": meta.get("category", ""),
            "category_name": meta.get("category_name", ""),
            "tags": meta.get("tags", ""),
            "play_count": meta.get("play_count", "0"),
            "like_count": meta.get("like_count", "0"),
            "favorite_count": meta.get("favorite_count", "0"),
            "duration": meta.get("duration", ""),
            "publish_date": meta.get("publish_date", ""),
            "content": data["documents"][i] if data.get("documents") else "",
        })
    return videos


# noinspection SpellCheckingInspection
def _format_projects(data) -> list[dict]:
    """格式化项目数据"""
    if not data or not data.get("ids"):
        return []
    projects = []
    for i, doc_id in enumerate(data["ids"]):
        meta = data["metadatas"][i] if data.get("metadatas") else {}
        source = meta.get("source", "")
        full_name = meta.get("full_name", "")
        url = f"https://github.com/{full_name}" if source == "github" else f"https://gitee.com/{full_name}"
        projects.append({
            "id": doc_id,
            "name": meta.get("name", ""),
            "description": meta.get("description", ""),
            "tech_tags": meta.get("tech_tags", ""),
            "use_cases": meta.get("use_cases", ""),
            "difficulty": meta.get("difficulty", ""),
            "stars": meta.get("stars", 0),
            "language": meta.get("language", ""),
            "url": url,
            "content": data["documents"][i] if data.get("documents") else "",
        })
    return projects


def _format_interns(data) -> list[dict]:
    """格式化实习数据"""
    if not data or not data.get("ids"):
        return []
    interns = []
    for i, doc_id in enumerate(data["ids"]):
        # noinspection SpellCheckingInspection
        meta = data["metadatas"][i] if data.get("metadatas") else {}
        interns.append({
            "id": doc_id,
            "job_title": meta.get("jobTitle", ""),
            "company_name": meta.get("company_name", ""),
            "company_industry": meta.get("company_industry", ""),
            "company_scale": meta.get("company_scale", ""),
            "salary": meta.get("salary", ""),
            "city": meta.get("city", ""),
            "degree": meta.get("degree", ""),
            "days_per_week": meta.get("daysPerWeek", ""),
            "months": meta.get("months", ""),
            "job_type": meta.get("jobType", ""),
            "tech_stack": meta.get("techStack", ""),
            "url": meta.get("url", ""),
            "content": data["documents"][i] if data.get("documents") else "",
        })
    return interns


if __name__ == "__main__":
    # 第一步：查询获取摘要信息
    result = query_videos.invoke({"query": "Java入门", "top_k": 3})
    print("摘要信息:", result)
    # 第二步：获取完整信息
    if result:
        refs = [{"id": r["id"], "type": r["type"]} for r in result]
        full_info = get_resources_by_ids(refs)
        print("完整信息:", full_info)
