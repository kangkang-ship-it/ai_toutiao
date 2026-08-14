from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有 ORM 模型的统一基类（全局唯一，main.py 依赖其 metadata 自动建表）"""
    pass
