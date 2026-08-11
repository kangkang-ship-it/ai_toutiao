# from passlib.context import CryptContext
#
# #创建密码上下文
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# #密码加密
# def get_hash_password(password: str):
#     return pwd_context.hash(password)
import bcrypt

def get_hash_password(password: str) -> str:
    """
    使用 bcrypt 加密密码（自动截断至 72 字节）
    """
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码（同样截断至 72 字节）
    """
    plain_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(plain_bytes, hashed_password.encode("utf-8"))