
import bcrypt


def get_hashed_password(password: str) -> str:
    """
    返回可存数据库的 bcrypt 哈希字符串（包含盐和 cost）。
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()  # 可选：bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)  # bytes
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    校验明文密码是否匹配已存的 bcrypt 哈希字符串。
    """
    password_bytes = password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


