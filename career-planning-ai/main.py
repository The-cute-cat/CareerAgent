import time

from fastapi import FastAPI, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from ai_service.exceptions import ApiException
from ai_service.response.result import success
from ai_service.routers import parse, question, matching, convert, code_ability, graph_path, report, chat
from ai_service.utils.logger_handler import log

app = FastAPI()

app.include_router(parse.router)
app.include_router(question.router)
app.include_router(matching.router)
app.include_router(convert.router)
app.include_router(code_ability.router)
app.include_router(graph_path.router)
app.include_router(report.router)
app.include_router(chat.router)


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(_: Request, exc: StarletteHTTPException):
    """处理所有 Starlette HTTP 异常（包括 405 Method Not Allowed）"""
    log.error(f"StarletteHTTPException: {exc}", exc_info=True)
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "code": exc.status_code,
            "state": False,
            "msg": exc.detail,
            "data": None
        })
    )


@app.exception_handler(ApiException)
async def api_exception_handler(_: Request, exc: ApiException):
    log.error(f"ApiException: {exc}", exc_info=True)
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "code": exc.code,
            "state": exc.code < 400,
            "msg": exc.msg,
            "data": exc.data
        })
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    """统一处理 FastAPI 的 HTTPException"""
    log.error(f"HTTPException: {exc}", exc_info=True)
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "code": exc.status_code,
            "state": False,
            "msg": exc.detail,
            "data": None
        })
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    """统一处理请求参数验证错误（422）"""
    log.error(f"请求参数验证失败: {exc}", exc_info=True)
    errors = exc.errors()
    if errors:
        error = errors[0]
        loc = " -> ".join(str(x) for x in error["loc"])
        msg = f"{loc}: {error['msg']}"
    else:
        msg = "请求参数验证失败"

    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "code": 422,
            "state": False,
            "msg": msg,
            "data": {"errors": errors} if len(errors) > 1 else None
        })
    )


@app.exception_handler(Exception)
async def exception_handler(_: Request, exc: Exception):
    """统一处理其他异常"""
    log.error(f"服务器内部错误: {exc}", exc_info=True)
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "code": 500,
            "state": False,
            "msg": "服务器内部错误",
            "data": {"errors": str(exc)}
        })
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有请求头
)


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    end_time = time.time()
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk
    log.info(f"请求路径: {request.url.path}, 响应时间: {end_time - start_time:.3f}s")
    log.debug(f"响应内容: {response_body.decode()}")
    from fastapi.responses import Response
    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )


@app.get("/")
async def root():
    return success("Emptiness is also an attitude!(=^･ω･^=)")
