from fastapi import APIRouter, Body, Depends
from ai_service.models.userform import UserForm
from ai_service.response.result import success
from ai_service.services.struct_text_extractor import struct_text_extractor


__all__ = ["router"]

router = APIRouter(prefix="/convert", tags=["convert"])

@router.post("/userform_to_userprofile", summary="将用户表单转换为用户画像")
async def userform_to_userprofile(user_form: UserForm = Body(..., description="用户表单数据")):
    """
    将用户表单转换为用户画像

    Args:
        user_form: 用户表单数据

    Returns:
        转换后的用户画像数据
    """
    user_profile = await struct_text_extractor.extract_from_userform_to_userprofile(user_form)
    # 这里直接返回输入的用户表单数据，实际应用中可以进行更复杂的转换逻辑
    return success(user_profile)
