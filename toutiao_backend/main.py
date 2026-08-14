from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()  # 需在读取环境变量的模块（config.db_conf 等）导入前执行

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import news, users, favorite, history, ai
from utils.exception_handlers import register_exception_handlers
from config.db_conf import engine
from models.base import Base
# 导入全部模型，确保其注册到统一 Base 的 metadata（create_all 依赖此注册）
from models import news as news_models  # noqa: F401
from models import users as users_models  # noqa: F401
from models import favorite as favorite_models  # noqa: F401
from models import history as history_models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时自动建表（统一 Base 保证所有模型已注册）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

#注册异常处理器
register_exception_handlers(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源，开发阶段允许所有源，生产环境需要指定源
    allow_credentials=False,  # 通配符 origin 下必须为 False
    allow_methods=["*"],  # 允许的请求方法
    allow_headers=["*"],  # 允许的请求头
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

# 挂载路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)
app.include_router(ai.router)
