from fastapi import Header, Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from  starlette import status

from config.db_conf import get_db
from crud import users


# 整合 根据Token 查询用户,返回用户的功能
# async def get_current_user(
#         authorization: str = Header(...,alias="Authorization"),
#         db: AsyncSession = Depends(get_db)
# ):
#         token = authorization.replace("Bearer ","")
#         user = await users.get_user_by_token(db,token)
#         if not user:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="无效的令牌或者已经过期的令牌")
#         return user
async def get_current_user(
        authorization: str = Header(...),
        db: AsyncSession = Depends(get_db)
):
    # 兼容两种格式：Bearer <token> 或 直接 token
    if authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "").strip()
    else:
        token = authorization.strip()  # 直接使用

    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Token 无效或已过期")
    return user