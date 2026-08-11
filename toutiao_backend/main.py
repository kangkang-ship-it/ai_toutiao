from fastapi import FastAPI
from routers import news, users, favorite, history
from fastapi.middleware.cors import CORSMiddleware

from utils.exception_handlers import register_exception_handlers
from config.db_conf import engine
from sqlalchemy.orm import DeclarativeBase


app = FastAPI()

#注册异常处理器
register_exception_handlers(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源，开发阶段允许所有源，生产环境需要指定源
    allow_credentials=False,  # 通配符 origin 下必须为 False
    allow_methods=["*"],  # 允许的请求方法
    allow_headers=["*"],  # 允许的请求头
)

class Base(DeclarativeBase):
    pass


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 挂载路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)