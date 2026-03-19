from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import Depends, Header, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from conf.db_conf import get_database
from models.admin import Admin, AdminToken
from utils import security


async def get_admin_by_username(db: AsyncSession, username: str):
    stmt = select(Admin).where(Admin.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def authenticate_admin(db: AsyncSession, username: str, password: str):
    admin = await get_admin_by_username(db, username)
    if not admin or not admin.is_active:
        return None
    if not security.verify_password(password, admin.password):
        return None
    return admin


async def create_admin_token(db: AsyncSession, admin_id: int, expire_days: int = 7):
    expires_at = datetime.now() + timedelta(days=expire_days)
    token = str(uuid4())

    result = await db.execute(select(AdminToken).where(AdminToken.admin_id == admin_id))
    admin_token = result.scalar_one_or_none()

    if admin_token:
        admin_token.token = token
        admin_token.expires_at = expires_at
    else:
        admin_token = AdminToken(admin_id=admin_id, token=token, expires_at=expires_at)
        db.add(admin_token)

    admin = await db.get(Admin, admin_id)
    if admin:
        admin.last_login_at = datetime.now()

    await db.commit()
    return token


async def get_admin_by_token(db: AsyncSession, token: str):
    stmt = (
        select(Admin)
        .join(AdminToken, AdminToken.admin_id == Admin.id)
        .where(
            and_(
                AdminToken.token == token,
                AdminToken.expires_at >= datetime.now(),
                Admin.is_active.is_(True),
            )
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_current_admin(
    authorization: str = Header(..., alias="Authorization"),
    db: AsyncSession = Depends(get_database),
):
    token = authorization.replace("Bearer ", "")
    admin = await get_admin_by_token(db, token)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的管理员令牌或令牌已过期",
        )
    return admin
