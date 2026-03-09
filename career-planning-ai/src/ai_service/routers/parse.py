from fastapi import APIRouter, Depends

__all__ = ["router"]

from ai_service.response.result import success_msg
from ai_service.schemas.file import validate_pdf

router = APIRouter(prefix="/parse", tags=["parse"])


@router.post("/pdf")
async def parse_pdf(file_info=Depends(validate_pdf)):
    return success_msg(file_info)
