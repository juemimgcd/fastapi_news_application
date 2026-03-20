from models.users import User, UserLoginLog, UserToken
from sqlalchemy import select, func, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.users import UserRequest, UserUpdateRequest, UserChangePasswordRequest
from utils import security
from uuid import uuid4
from datetime import datetime, timedelta


async def get_user_by_name(db: AsyncSession, username: str):
    sql = select(User).where(User.username == username)
    result = await db.execute(sql)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int):
    sql = select(User).where(User.id == user_id)
    result = await db.execute(sql)
    return result.scalar_one_or_none()



async def create_user(db: AsyncSession, user_data: UserRequest):
    hash_password = security.get_hashed_password(password=user_data.password)
    user = User(username=user_data.username, password=hash_password)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_token(db: AsyncSession, user_id: int):
    expires_at = datetime.now() + timedelta(days=7)

    # 以 user\_id 为主：该用户已有 token 就更新，没有就新增
    result = await db.execute(select(UserToken).where(UserToken.user_id == user_id))
    user_token = result.scalar_one_or_none()

    token = str(uuid4())

    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)

    await db.commit()
    return token


async def record_user_login(db: AsyncSession, user_id: int):
    """
    记录用户当天登录行为。
    同一天重复登录只更新 login_at，不重复插入新记录。
    """
    today = datetime.now().date()
    result = await db.execute(
        select(UserLoginLog).where(
            UserLoginLog.user_id == user_id,
            UserLoginLog.login_date == today,
        )
    )
    login_log = result.scalar_one_or_none()

    if login_log:
        login_log.login_at = datetime.now()
    else:
        login_log = UserLoginLog(user_id=user_id, login_date=today, login_at=datetime.now())
        db.add(login_log)

    await db.commit()
    await db.refresh(login_log)
    return login_log


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_name(db, username)
    if not user:
        return None
    if not security.verify_password(password, hashed_password=user.password):
        return None

    return user


async def get_user_by_token(db: AsyncSession, token: str):

    sql = (
        select(User)
        .join(UserToken, UserToken.user_id == User.id)
        .where(
            and_(
                UserToken.token == token,
                UserToken.expires_at >= datetime.now(),
                )
        )
    )
    result = await db.execute(sql)
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user_name: str, user_data: UserUpdateRequest):
    updated_user = await get_user_by_name(db, user_name)
    if not updated_user:
        return None

    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(updated_user, field, value)

    await db.commit()
    await db.refresh(updated_user)

    return updated_user



async def change_user_password(db:AsyncSession,user:User,user_data:UserChangePasswordRequest):
    if not security.verify_password(user_data.old_password,user.password):
        return False

    new_hash_password = security.get_hashed_password(user_data.new_password)

    user.password = new_hash_password

    await db.commit()
    await db.refresh(user)

    return True





