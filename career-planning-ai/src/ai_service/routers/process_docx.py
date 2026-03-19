from fastapi import FastAPI, Depends, UploadFile, File
from pydantic import BaseModel
from src.ai_service.models.word import WordType
from ai_service.services.document_analysis_service import DocumentAnalysisService
from src.ai_service.utils.logger_handler import log
from ai_service.schemas.file import validate_file

app = FastAPI()
document_analysis_service = DocumentAnalysisService()


class DocxRequest(BaseModel):
    file: UploadFile = File("word_file", description="上传的 Word 文档文件")


@app.post("/process/docx/struct-text")
async def process_docx(request: DocxRequest = Depends()):
    """
    处理上传的 Word 文档，提取结构化文本信息。
    """
    file_data = await validate_file(request.file)
    file_path = file_data["save_path"]

    try:
        # 使用 DocumentAnalysisService 提取结构化文本信息
        structured_data = await document_analysis_service.analyze_docx(file_path)
        return {"structured_data": structured_data}

    except Exception as e:
        log.error(f"Error processing docx file: {e}")
        return {"message": "Error processing Docx file", "error": str(e)}
