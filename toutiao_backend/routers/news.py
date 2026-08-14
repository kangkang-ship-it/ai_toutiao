# from email import message
#
# from fastapi import APIRouter, Depends, Query, HTTPException
# from sqlalchemy import null
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from config.db_conf import get_db
# from crud import news
#
# # 创建APIRout实例
# # prefix 路由前缀
# # tags 分组 标签
# router = APIRouter(prefix="/api/news",tags=["news"])
#
# # 接口实现流程
# # 1.模块化路由
# # 2.定义模型类
# # 3.在crud文件夹里创建文件,封装操作数据库的方法
# # 4.在路由处理函数里面调用crud封装好的方法,响应结果
#
#
# @router.get("/categories")
# async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession=Depends(get_db)):
#
#     # 先获取数据库里面的新闻分类信息,先定义模型类,封装查询数据的方法
#     categories=await news.get_categories(db,skip, limit)
#     return {
#         "code": 200,
#         "message": "获取新闻分类成功",
#         "data": categories
#     }
#
# @router.get("/list")
# async def get_news_list(
#         category_id: int=Query(...,alias="categoryId"),
#         page: int = 1,
#         page_size: int = Query(10, alias="pageSize",le=100),
#         db: AsyncSession=Depends(get_db),
# ):
#     #思路:处理分页规则->查询新闻列表->计算总量->计算是否还有更多
#     offset=(page - 1) * page_size
#     news_list=await news.get_news_list(db,category_id,offset,page_size)
#     total=await news.get_news_count(db,category_id)
#     # (跳过的 + 当前列表里面的数量) < 总量
#     has_more = (offset + len(news_list)) < total
#     return {
#         "code": 200,
#         "message":"获取新闻列表",
#         "data":{
#             "list":news_list,
#             "total":total,
#             "hasMore":has_more
#         }
#     }
#
# @router.get("/detail")
# async def get_news_detail(news_id: int=Query(...,alias="id"), db: AsyncSession=Depends(get_db)):
#     #获取新闻详情 + 浏览量 + 1 + 相关新闻
#     news_detail = await news.get_news_detail(db,news_id)
#     if not news_detail:
#         raise HTTPException(status_code=404,detail="新闻不存在")
#
#     views_res = await news.increase_news_views(db,news_detail.id)
#     if not views_res:
#         raise HTTPException(status_code=404, detail="新闻不存在")
#
#     related_news = await news.get_related_news(db, news_detail.id,news_detail.category_id)
#
#     return {
#         "code": 200,
#         "message": "success",
#         "data": {
#             "id": news_detail.id,
#             "title": news_detail.title,
#             "content": news_detail.content,
#             "image": news_detail.image,
#             "author": news_detail.author,
#             "publishTime": news_detail.publish_time,
#             "categoryId": news_detail.category_id,
#             "views": news_detail.views,
#             "relatedNews": related_news,
#         }
#     }





from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import news
from utils.redis_cache import get_json_cache, set_cache   # 导入缓存工具

router = APIRouter(prefix="/api/news", tags=["news"])


def _serialize_news(n):
    """把 News ORM 对象转为前端使用的 camelCase 字典（可直接 json.dumps 存入缓存）"""
    return {
        "id": n.id,
        "title": n.title,
        "description": n.description,
        "image": n.image,
        "author": n.author,
        "categoryId": n.category_id,
        "views": n.views,
        "publishTime": n.publish_time.isoformat() if n.publish_time else None,
    }


@router.get("/categories")
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    获取新闻分类列表（带缓存）
    """
    cache_key = "news_categories"  # 固定 key，因为参数固定

    # 1. 尝试从缓存读取
    cached = await get_json_cache(cache_key)
    if cached is not None:
        return {
            "code": 200,
            "message": "获取新闻分类成功（缓存）",
            "data": cached
        }

    # 2. 缓存未命中，查询数据库
    categories = await news.get_categories(db, skip, limit)

    # 3. 序列化为可 JSON 化的字典（ORM 对象直接 json.dumps 会抛 TypeError，导致缓存写入静默失败）
    categories_data = [{"id": c.id, "name": c.name} for c in categories]

    # 4. 存入缓存（过期时间 1 小时）
    await set_cache(cache_key, categories_data, expire=3600)

    return {
        "code": 200,
        "message": "获取新闻分类成功",
        "data": categories_data
    }


@router.get("/list")
async def get_news_list(
    category_id: int = Query(..., alias="categoryId"),
    page: int = 1,
    page_size: int = Query(10, alias="pageSize", le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    获取新闻列表（分页 + 缓存）
    """
    offset = (page - 1) * page_size

    # 1. 构造缓存键（包含所有影响结果的参数）
    cache_key = f"news_list:{category_id}:{page}:{page_size}"

    # 2. 尝试从缓存读取
    cached = await get_json_cache(cache_key)
    if cached is not None:
        return {
            "code": 200,
            "message": "获取新闻列表（缓存）",
            "data": cached
        }

    # 3. 缓存未命中，查询数据库
    news_list = await news.get_news_list(db, category_id, offset, page_size)
    total = await news.get_news_count(db, category_id)
    has_more = (offset + len(news_list)) < total

    data = {
        "list": [_serialize_news(n) for n in news_list],
        "total": total,
        "hasMore": has_more
    }

    # 4. 存入缓存（过期时间 60 秒，新闻列表变化较快）
    await set_cache(cache_key, data, expire=60)

    return {
        "code": 200,
        "message": "获取新闻列表",
        "data": data
    }


@router.get("/detail")
async def get_news_detail(
    news_id: int = Query(..., alias="id"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取新闻详情（不缓存，因为浏览量实时更新）
    """
    # 获取新闻详情
    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    # 增加浏览量
    views_res = await news.increase_news_views(db, news_detail.id)
    if not views_res:
        raise HTTPException(status_code=404, detail="新闻不存在")

    # 获取相关新闻
    related_news = await news.get_related_news(db, news_detail.id, news_detail.category_id)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news,
        }
    }

