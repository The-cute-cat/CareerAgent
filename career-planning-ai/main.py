

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from ai_service.exceptions import ApiException
from ai_service.routers import parse

app = FastAPI()

app.include_router(parse.router)

@app.exception_handler(ApiException)
async def api_exception_handler(_: Request, exc: ApiException):
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "code": exc.code,
            "state": exc.code < 400,
            "msg": exc.msg,
            "data": exc.data
        })
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有请求头
)


@app.get("/")
async def root():
    return "Emptiness is also an attitude!(=^･ω･^=)"
