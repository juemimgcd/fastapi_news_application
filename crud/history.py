from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


async def add_history(db: AsyncSession, user_id: int, news_id: int):
    sql = select(History).where(History.user_id == user_id,History.news_id == news_id)

    result = await db.execute(sql)
    is_exits = result.scalar_one_or_none()

    if is_exits:
        is_exits.view_time = func.now()
        await db.commit()
        await db.refresh(is_exits)
        return is_exits
    else:
        history = History(user_id=user_id,news_id=news_id)
        db.add(history)
        await db.commit()
        await db.refresh(history)

        return history


async def get_history_list(db:AsyncSession,user_id:int,page:int,page_size:int = 20):
    offset = (page - 1)*page_size

    sql = select(func.count(History.id)).where(History.user_id == user_id)
    result = await db.execute(sql)
    total = result.scalar_one_or_none()


    stmt = (
        select(News,History.view_time.label("view_time"),History.id.label("history_id"))
        .join(History,History.news_id == News.id)
        .where(History.user_id == user_id)
        .order_by(History.view_time.desc())
        .offset(offset).limit(page_size)
    )

    result2 = await db.execute(stmt)

    rows = result2.all()
    return rows,total



async def delete_history(db: AsyncSession, user_id: int, history_id: int):
    """
    删除历史记录
    """
    query = delete(History).where(History.user_id == user_id, History.id == history_id)
    result = await db.execute(query)
    await db.commit()

    return result.rowcount > 0


async def clear_history(db: AsyncSession, user_id: int):
    """
    清空历史记录
    """
    query = delete(History).where(History.user_id == user_id)
    result = await db.execute(query)
    await db.commit()

    return result.rowcount or 0












