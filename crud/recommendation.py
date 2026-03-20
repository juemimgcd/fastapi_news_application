from datetime import datetime

from sqlalchemy import select, union
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.history import History
from models.news import News, NewsEmbedding


async def get_user_history_news(
        db: AsyncSession,
        user_id: int,
        limit: int
) -> list[tuple[News, datetime]]:
    stmt = (
        select(News, History.view_time.label("event_time"))
        .join(History, History.news_id == News.id)
        .where(History.user_id == user_id)
        .order_by(History.view_time.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.all()


async def get_user_favorite_news(
        db: AsyncSession,
        user_id: int,
        limit: int
) -> list[tuple[News, datetime]]:
    stmt = (
        select(News, Favorite.created_at.label("event_time"))
        .join(Favorite, Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.all()


async def get_candidate_news(
        db: AsyncSession,
        user_id: int,
        limit: int
) -> list[News]:
    interacted_news = union(
        select(History.news_id.label("news_id")).where(History.user_id == user_id),
        select(Favorite.news_id.label("news_id")).where(Favorite.user_id == user_id),
    ).subquery()

    stmt = (
        select(News)
        .where(~News.id.in_(select(interacted_news.c.news_id)))
        .order_by(News.publish_time.desc(), News.views.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_latest_popular_news(db: AsyncSession, limit: int) -> list[News]:
    stmt = select(News).order_by(News.views.desc(), News.publish_time.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_news_embedding_records(
        db: AsyncSession,
        news_ids: list[int]
) -> dict[int, NewsEmbedding]:
    if not news_ids:
        return {}

    stmt = select(NewsEmbedding).where(NewsEmbedding.news_id.in_(news_ids))
    result = await db.execute(stmt)
    records = result.scalars().all()
    return {record.news_id: record for record in records}
