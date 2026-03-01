from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

#app.include_router()

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
