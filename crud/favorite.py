from models.favorite import Favorite
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from models.news import News
from sqlalchemy.engine import CursorResult


async def is_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    sql = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)

    result = await db.execute(sql)

    flag = result.scalar_one_or_none()

    return flag is not None


async def add_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    existing = await db.execute(
        select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    )
    favorite = existing.scalar_one_or_none()
    if favorite:
        return favorite

    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite


async def remove_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    sql = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)

    result = await db.execute(sql)
    await db.commit()
    return result.rowcount > 0


async def get_favorite_list(
        db:AsyncSession,
        user_id:int,
        page:int = 1,
        page_size:int = 20

):
    sql1 = select(func.count(Favorite.id)).where(Favorite.user_id == user_id)

    result1 = await db.execute(sql1)

    total = result1.scalar_one_or_none()

    offset = (page - 1)*page_size


    stmt = (
        select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id"))
        .join(Favorite,Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .offset(offset).limit(page_size)
    )
    result2 = await db.execute(stmt)

    rows = result2.all()
    return rows,total



async def remove_all_favorites(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()

    # 返回一个删除的数量
    return result.rowcount or 0










