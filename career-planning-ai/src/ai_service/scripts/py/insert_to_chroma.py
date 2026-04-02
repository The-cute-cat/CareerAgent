"""
将 internships_detail.json 和 books_detail.json 数据插入到 Chroma 向量数据库

用法:
    python -m ai_service.scripts.py.insert_to_chroma
    或
    python src/ai_service/scripts/py/insert_to_chroma.py
"""
import json
import os
from datetime import datetime
from typing import Any

from langchain_core.documents import Document

from ai_service.scripts import log as logger
from ai_service.services.chroma_service import ChromaService
from ai_service.utils.path_tool import get_abs_path
from config import settings

# 配置
BATCH_SIZE = 50  # 每批处理的文档数量

# 失败记录保存目录
FAILED_RECORDS_DIR = get_abs_path("scripts/failed_records")

INTERN_PATH = get_abs_path("scripts/js/internships_detail.json")
BOOKS_PATH = get_abs_path("scripts/js/books_data/books_detail.json")
VIDEO_PATH = get_abs_path("scripts/js/video_data/bilibili_courses_cleaned.json")

# Collection 名称
INTERN_COLLECTION = settings.chroma_config.collection_name.intern_collection
BOOKS_COLLECTION = settings.chroma_config.collection_name.book_collection
VIDEO_COLLECTION = settings.chroma_config.collection_name.video_collection


def load_json(file_path: str) -> list[dict[str, Any]]:
    """加载 JSON 文件"""
    logger.info(f"加载 JSON 文件: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    logger.info(f"成功加载 {len(data)} 条数据")
    return data


def save_failed_records(
        failed_records: list[dict[str, Any]],
        collection_name: str,
        record_type: str
) -> str | None:
    """
    保存插入失败的记录到 JSON 文件
    
    Args:
        failed_records: 失败记录列表，每条记录包含 original_data 和 error_message
        collection_name: 集合名称
        record_type: 记录类型 (如 'internship', 'book', 'video')
        
    Returns:
        保存的文件路径，如果没有失败记录则返回 None
    """
    if not failed_records:
        return None

    # 确保目录存在
    os.makedirs(FAILED_RECORDS_DIR, exist_ok=True)

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"failed_{record_type}_{timestamp}.json"
    filepath = os.path.join(FAILED_RECORDS_DIR, filename)

    # 构建保存数据
    save_data = {
        "collection_name": collection_name,
        "record_type": record_type,
        "failed_count": len(failed_records),
        "timestamp": datetime.now().isoformat(),
        "records": failed_records
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    logger.info(f"失败记录已保存到: {filepath}")
    return filepath


def prepare_intern_document(item: dict[str, Any]) -> Document:
    """
    将实习数据转换为 Document 对象
    
    主要内容: jobDescription + jobTitle + 技术栈
    元数据: 其他字段
    """
    # 构建主要内容
    content_parts = [
        f"职位名称: {item.get('jobTitle', '')}",
        f"公司: {item.get('company', {}).get('name', '')}",
        f"薪资: {item.get('salary', '')}",
        f"城市: {item.get('city', '')}",
        f"学历要求: {item.get('degree', '')}",
        f"每周工作天数: {item.get('daysPerWeek', '')}",
        f"实习月数: {item.get('months', '')}",
    ]

    tech_stack = item.get('techStack', [])
    if tech_stack:
        content_parts.append(f"技术栈: {', '.join(tech_stack)}")

    tags = item.get('tags', [])
    if tags:
        content_parts.append(f"标签: {', '.join(tags)}")

    job_desc = item.get('jobDescription', '')
    if job_desc:
        content_parts.append(f"职位描述:\n{job_desc}")

    content = "\n".join(content_parts)

    # 构建元数据
    metadata = {
        "type": "internship",
        "jobTitle": item.get('jobTitle', ''),
        "company_name": item.get('company', {}).get('name', ''),
        "company_industry": item.get('company', {}).get('industry', ''),
        "company_scale": item.get('company', {}).get('scale', ''),
        "salary": item.get('salary', ''),
        "city": item.get('city', ''),
        "degree": item.get('degree', ''),
        "daysPerWeek": item.get('daysPerWeek', ''),
        "months": item.get('months', ''),
        "jobType": item.get('jobType', ''),
        "url": item.get('url', ''),
        "internId": item.get('internId', ''),
        "techStack": ','.join(tech_stack) if tech_stack else '',
        "keyword": item.get('keyword', ''),
        "crawlTime": item.get('crawlTime', ''),
    }

    return Document(page_content=content, metadata=metadata)


def prepare_book_document(item: dict[str, Any]) -> Document:
    """
    将书籍数据转换为 Document 对象
    
    主要内容: summary + title + 目录
    元数据: 其他字段
    """
    # 构建主要内容
    content_parts = [
        f"书名: {item.get('title', '')}",
        f"作者: {item.get('author', '')}",
    ]

    subtitle = item.get('subtitle', '')
    if subtitle:
        content_parts.append(f"副标题: {subtitle}")

    category = item.get('category', '')
    if category:
        content_parts.append(f"分类: {category}")

    keyword = item.get('keyword', '')
    if keyword:
        content_parts.append(f"关键词: {keyword}")

    publisher = item.get('publisher', '')
    if publisher:
        content_parts.append(f"出版社: {publisher}")

    publish_date = item.get('publish_date', '')
    if publish_date:
        content_parts.append(f"出版日期: {publish_date}")

    rating = item.get('rating', {})
    if rating and rating.get('score'):
        content_parts.append(f"评分: {rating.get('score')}")

    summary = item.get('summary', '')
    if summary:
        content_parts.append(f"内容简介:\n{summary}")

    author_intro = item.get('author_intro', '')
    if author_intro:
        content_parts.append(f"作者简介:\n{author_intro}")

    content = "\n".join(content_parts)

    # 构建元数据
    metadata = {
        "type": "book",
        "book_id": str(item.get('id', '')),
        "title": item.get('title', ''),
        "author": item.get('author', ''),
        "translator": item.get('translator', ''),
        "publisher": publisher,
        "publish_date": publish_date,
        "category": category,
        "keyword": keyword,
        "isbn": item.get('isbn', ''),
        "pages": item.get('pages', ''),
        "url": item.get('url', ''),
        "cover_url": item.get('cover_url', ''),
        "rating_score": str(rating.get('score', '')) if rating else '',
        "crawl_time": item.get('crawl_time', ''),
    }

    return Document(page_content=content, metadata=metadata)


def insert_documents_batch(
        service: ChromaService,
        documents: list[Document],
        batch_size: int = BATCH_SIZE,
        original_data: list[dict[str, Any]] | None = None
) -> tuple[int, list[dict[str, Any]]]:
    """
    批量插入文档到 Chroma
    
    Args:
        service: Chroma 服务实例
        documents: 文档列表
        batch_size: 每批处理的数量
        original_data: 原始数据列表，用于记录失败时的原始数据
        
    Returns:
        tuple: (成功插入的文档数量, 失败记录列表)
    """
    total = len(documents)
    inserted = 0
    failed_records: list[dict[str, Any]] = []

    try:
        for i in range(0, total, batch_size):
            batch = documents[i:i + batch_size]
            batch_indices = list(range(i, min(i + batch_size, total)))

            try:
                service.add_documents(batch)
                inserted += len(batch)
                logger.info(f"已插入 {inserted}/{total} 条文档")
            except Exception as e:
                logger.error(f"插入批次 {i // batch_size + 1} 失败: {e}", exc_info=True)
                # 尝试逐个插入
                for j, doc in enumerate(batch):
                    try:
                        service.add_documents([doc])
                        inserted += 1
                    except Exception as e2:
                        error_msg = str(e2)
                        logger.error(f"插入单条文档失败: {error_msg}", exc_info=True)

                        # 记录失败信息
                        failed_record = {
                            "index": batch_indices[j],
                            "error": error_msg,
                            "page_content": doc.page_content,
                            "metadata": doc.metadata
                        }

                        # 如果有原始数据，也保存原始数据
                        if original_data and batch_indices[j] < len(original_data):
                            failed_record["original_data"] = original_data[batch_indices[j]]

                        failed_records.append(failed_record)
    except KeyboardInterrupt:
        logger.warning("用户中断操作，正在保存失败记录...")
    except Exception as e:
        logger.error(f"插入过程中发生未预期的错误: {e}", exc_info=True)
    finally:
        # 记录剩余未处理的文档为失败
        remaining_start = inserted + len(failed_records)
        if remaining_start < total and original_data:
            logger.info(f"记录剩余未处理的 {total - remaining_start} 条文档...")
            for idx in range(remaining_start, total):
                failed_record = {
                    "index": idx,
                    "error": "未处理（程序中断或终止）",
                    "page_content": documents[idx].page_content,
                    "metadata": documents[idx].metadata,
                    "original_data": original_data[idx]
                }
                failed_records.append(failed_record)

    return inserted, failed_records


def insert_internships(clear_existing: bool = True) -> tuple[int, int]:
    """
    插入实习数据到 Chroma
    
    Args:
        clear_existing: 是否清空已有数据
        
    Returns:
        tuple: (插入的文档数量, 失败的文档数量)
    """
    logger.info("=" * 50)
    logger.info("开始处理实习数据")

    # 加载数据
    if not os.path.exists(INTERN_PATH):
        logger.error(f"实习数据文件不存在: {INTERN_PATH}", exc_info=True)
        return 0, 0

    data = load_json(INTERN_PATH)

    # 获取 Chroma 服务
    service = ChromaService.get_instance(collection_name=INTERN_COLLECTION)

    # 清空已有数据
    if clear_existing:
        try:
            service.delete_all()
            logger.info(f"已清空集合: {INTERN_COLLECTION}")
        except Exception as e:
            logger.warning(f"清空集合失败: {e}")

    # 转换文档
    documents = [prepare_intern_document(item) for item in data]

    # 插入文档
    inserted, failed_records = insert_documents_batch(service, documents, original_data=data)

    # 保存失败记录
    if failed_records:
        save_failed_records(failed_records, INTERN_COLLECTION, "internship")

    failed_count = len(failed_records)
    logger.info(f"实习数据处理完成，共插入 {inserted} 条文档，失败 {failed_count} 条")
    return inserted, failed_count


def insert_books(clear_existing: bool = True) -> tuple[int, int]:
    """
    插入书籍数据到 Chroma
    
    Args:
        clear_existing: 是否清空已有数据
        
    Returns:
        tuple: (插入的文档数量, 失败的文档数量)
    """
    logger.info("=" * 50)
    logger.info("开始处理书籍数据")

    # 加载数据
    if not os.path.exists(BOOKS_PATH):
        logger.error(f"书籍数据文件不存在: {BOOKS_PATH}", exc_info=True)
        return 0, 0

    data = load_json(BOOKS_PATH)

    # 获取 Chroma 服务
    service = ChromaService.get_instance(collection_name=BOOKS_COLLECTION)

    # 清空已有数据
    if clear_existing:
        try:
            service.delete_all()
            logger.info(f"已清空集合: {BOOKS_COLLECTION}")
        except Exception as e:
            logger.warning(f"清空集合失败: {e}")

    # 转换文档
    documents = [prepare_book_document(item) for item in data]

    # 插入文档
    inserted, failed_records = insert_documents_batch(service, documents, original_data=data)

    # 保存失败记录
    if failed_records:
        save_failed_records(failed_records, BOOKS_COLLECTION, "book")

    failed_count = len(failed_records)
    logger.info(f"书籍数据处理完成，共插入 {inserted} 条文档，失败 {failed_count} 条")
    return inserted, failed_count


def prepare_video_document(item: dict[str, Any]) -> Document:
    """
    将视频课程数据转换为 Document 对象
    
    主要内容: title + description + tags
    元数据: 其他字段
    """
    # 构建主要内容
    content_parts = [
        f"标题: {item.get('title', '')}",
        f"作者: {item.get('author', '')}",
    ]

    category = item.get('category', '')
    if category:
        content_parts.append(f"分类: {category}")

    category_name = item.get('categoryName', '')
    if category_name:
        content_parts.append(f"子分类: {category_name}")

    tags = item.get('tags', [])
    if tags:
        content_parts.append(f"标签: {', '.join(tags)}")

    description = item.get('description', '')
    if description:
        content_parts.append(f"简介:\n{description}")

    content = "\n".join(content_parts)

    # 构建元数据
    metadata = {
        "type": "video_course",
        "bvid": item.get('bvid', ''),
        "aid": str(item.get('aid', '')),
        "title": item.get('title', ''),
        "author": item.get('author', ''),
        "author_id": str(item.get('authorId', '')),
        "url": item.get('url', ''),
        "cover_image": item.get('coverImage', ''),
        "category": category,
        "category_name": category_name,
        "category_tags": ','.join(item.get('categoryTags', [])),
        "tags": ','.join(tags) if tags else '',
        "play_count": str(item.get('playCount', 0)),
        "like_count": str(item.get('likeCount', 0)),
        "favorite_count": str(item.get('favoriteCount', 0)),
        "danmaku_count": str(item.get('danmakuCount', 0)),
        "comment_count": str(item.get('commentCount', 0)),
        "duration": item.get('duration', ''),
        "publish_date": item.get('publishDate', ''),
        "search_keyword": item.get('searchKeyword', ''),
        "source": item.get('source', 'bilibili'),
        "crawl_time": item.get('crawledAt', ''),
    }

    return Document(page_content=content, metadata=metadata)


def insert_videos(clear_existing: bool = True) -> tuple[int, int]:
    """
    插入视频课程数据到 Chroma
    
    Args:
        clear_existing: 是否清空已有数据
        
    Returns:
        tuple: (插入的文档数量, 失败的文档数量)
    """
    logger.info("=" * 50)
    logger.info("开始处理视频课程数据")

    # 加载数据
    if not os.path.exists(VIDEO_PATH):
        logger.error(f"视频数据文件不存在: {VIDEO_PATH}", exc_info=True)
        return 0, 0

    data = load_json(VIDEO_PATH)

    # 获取 Chroma 服务
    service = ChromaService.get_instance(collection_name=VIDEO_COLLECTION)

    # 清空已有数据
    if clear_existing:
        try:
            service.delete_all()
            logger.info(f"已清空集合: {VIDEO_COLLECTION}")
        except Exception as e:
            logger.warning(f"清空集合失败: {e}")

    # 转换文档
    documents = [prepare_video_document(item) for item in data]

    # 插入文档
    inserted, failed_records = insert_documents_batch(service, documents, original_data=data)

    # 保存失败记录
    if failed_records:
        save_failed_records(failed_records, VIDEO_COLLECTION, "video")

    failed_count = len(failed_records)
    logger.info(f"视频课程数据处理完成，共插入 {inserted} 条文档，失败 {failed_count} 条")
    return inserted, failed_count


if __name__ == "__main__":
    # insert_books(False)
    # insert_internships(False)
    insert_videos(True)
    ...
