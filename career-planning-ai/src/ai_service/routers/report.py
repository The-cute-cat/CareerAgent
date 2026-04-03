from fastapi import APIRouter

__all__ = ["router"]

router = APIRouter(prefix="/report", tags=["report"])


async def get_plan():
    ...