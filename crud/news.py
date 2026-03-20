from fastapi.encoders import jsonable_encoder
from models.news import News, Category
from sqlalchemy import select, func, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from cache.news_cache import get_cached_categories, get_cache_news_list, set_cache_categories, set_cache_news_list


async def get_categories(db: AsyncSession, skip: int, limit: int = 20):
    cached_categories = await get_cached_categories()
    if cached_categories:
        return cached_categories

    sql = select(Category).offset(skip).limit(limit)

    result = await db.execute(sql)

    categories = result.scalars().all()
    if categories:
        js = jsonable_encoder(categories)
        await set_cache_categories(js)
        return categories
    return None


async def get_news_list(db: AsyncSession, category_id: int, skip: int, limit: int):
    # skip = (page - 1)*limit
    if limit <= 0:
        return []

    page = skip // limit + 1
    cached_news_list = await get_cache_news_list(category_id, page, limit)
    if cached_news_list:
        return [News(**item) for item in cached_news_list]

    sql = select(News).where(News.category_id == category_id).offset(skip).limit(limit)

    result = await db.execute(sql)

    news_list = result.scalars().all()
    if news_list:
        js = jsonable_encoder(news_list)
        await set_cache_news_list(category_id, page, limit, js)
        return news_list
    return []


async def get_news_total(db: AsyncSession, category_id: int):
    sql = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(sql)
    return result.scalar_one()


async def get_news_by_category_id(db: AsyncSession, category_id: int):
    sql = select(News).where(News.category_id == category_id)

    result = await db.execute(sql)

    return result.scalars().all()


async def get_news_detail(db: AsyncSession, news_id: int):
    sql = select(News).where(News.id == news_id)

    result = await db.execute(sql)

    return result.scalar_one_or_none()


async def increase_news_views(db: AsyncSession, news_id: int):
    stmt = (
        update(News)
        .where(News.id == news_id)
        .values(views=News.views + 1)
        .returning(News.views)
    )

    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()


async def get_related_news(db: AsyncSession, category_id: int, news_id: int, limit: int = 5):
    sql = (
        select(News)
        .where(and_(News.category_id == category_id, News.id != news_id))
        .order_by(
            News.views.desc(),
            News.publish_time.desc()
        )
        .limit(limit)
    )
    result = await db.execute(sql)
    return result.scalars().all()
