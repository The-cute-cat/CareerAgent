"""Word 文档处理路由模块

提供 Word 文档（doc/docx）的结构化文本提取接口。
"""
from ai_service.services.document_analysis_service import DocumentAnalysisService
from fastapi import FastAPI, Depends

from ai_service.schemas.file import validate_docx
from src.ai_service.utils.logger_handler import log

app = FastAPI()
document_analysis_service = DocumentAnalysisService()


@app.post("/process/docx/struct-text")
async def process_docx(file_info=Depends(validate_docx)):
    """
    处理上传的 Word 文档，提取结构化文本信息。

    通过 validate_docx 依赖自动完成文件类型验证和安全检测，
    仅接受 doc 或 docx 格式的 Word 文档。

    Args:
        file_info: 由 validate_docx 返回的文件信息字典，包含 save_path 等字段

    Returns:
        dict: 包含 structured_data 字段的响应，其中为提取的结构化文本数据

    Example:
        POST /process/docx/struct-text
        Content-Type: multipart/form-data
        files: <word_document.docx>
    """
    file_path = file_info["save_path"]

    try:
        # 使用 DocumentAnalysisService 提取结构化文本信息
        structured_data = await document_analysis_service.analyze_docx(file_path)
        return {"structured_data": structured_data}

    except Exception as e:
        log.error(f"Error processing docx file: {e}")
        return {"message": "Error processing Docx file", "error": str(e)}
