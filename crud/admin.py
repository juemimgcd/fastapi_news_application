from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, text
from models.users import User
from models.news import News
from utils.admin_auth import authenticate_admin, create_admin_token





async def get_admin_user_list(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
):
    """
    分页查询全部用户，可按关键字筛选。
    建议返回：(rows, total)
    """
    offset = (page - 1) * page_size

    filters = []
    if keyword:
        like_word = f"%{keyword}%"
        filters.append(
            or_(
                User.username.like(like_word),
                User.nickname.like(like_word),
                User.phone.like(like_word)
            )
        )

    stmt = (
        select(User)
        .where(*filters)
        .limit(page_size)
        .offset(offset)
    )

    count_stmt = select(func.count(User.id)).where(*filters)

    result = await db.execute(stmt)
    rows = result.scalars().all()

    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    return rows, total






async def get_admin_news_list(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    category_id: int | None = None,
):
    """
    分页查询全部新闻，可按关键字和分类筛选。
    建议返回：(rows, total)
    """
    offset = (page - 1) * page_size
    filters = []
    if keyword:
        like_keyword = f"%{keyword}%"
        filters.append(
            or_(
                News.title.ilike(like_keyword),
                News.description.ilike(like_keyword),
                News.author.ilike(like_keyword),
                News.content.ilike(like_keyword),
            )
        )
    if category_id is not None:
        filters.append(News.category_id == category_id)

    stmt = select(News).where(*filters).limit(page_size).offset(offset)
    res1 = await db.execute(stmt)

    sql = select(func.count(News.id)).where(*filters)
    res2 = await db.execute(sql)

    rows,total = res1.scalars().all(),res2.scalar_one_or_none()

    return rows,total






async def get_users_with_login_streak(
    db: AsyncSession,
    days: int,
    page: int = 1,
    page_size: int = 10,
):
    """
    返回满足连续登录天数的用户明细行，而不是纯 user_id 列表。
    行字段包含：user_id / username / nickname / streak_days / last_login_date。
    """
    offset = (page - 1) * page_size

    sql = text("""
        with t1 as (
            select distinct user_id, login_date
            from user_login_log
        ),
        t2 as (
            select
                user_id,
                login_date,
                (
                    login_date - (
                        row_number() over (
                            partition by user_id
                            order by login_date
                        ) * interval '1 day'
                    )
                )::date as flag
            from t1
        ),
        t3 as (
            select
                user_id,
                count(*) as streak_days,
                max(login_date) as last_login_date
            from t2
            group by user_id, flag
            having count(*) >= :days
        ),
        t4 as (
            select
                user_id,
                streak_days,
                last_login_date,
                row_number() over (
                    partition by user_id
                    order by streak_days desc, last_login_date desc
                ) as rn
            from t3
        )
        select
            u.id as user_id,
            u.username,
            u.nickname,
            t4.streak_days,
            t4.last_login_date
        from t4
        join "user" u on u.id = t4.user_id
        where t4.rn = 1
        order by t4.streak_days desc, t4.last_login_date desc
        limit :page_size offset :offset
    """)

    count_sql = text("""
        with t1 as (
            select distinct user_id, login_date
            from user_login_log
        ),
        t2 as (
            select
                user_id,
                login_date,
                (
                    login_date - (
                        row_number() over (
                            partition by user_id
                            order by login_date
                        ) * interval '1 day'
                    )
                )::date as flag
            from t1
        ),
        t3 as (
            select user_id
            from t2
            group by user_id, flag
            having count(*) >= :days
        )
        select count(distinct user_id) from t3
    """)

    result = await db.execute(sql, {
        "days": days,
        "page_size": page_size,
        "offset": offset,
    })
    rows = result.mappings().all()

    count_result = await db.execute(count_sql, {"days": days})
    total = count_result.scalar_one()

    return rows, total

async def get_news_favorite_ranking(
    db: AsyncSession,
    limit: int = 10,
    category_id: int | None = None,
):
    """
    查询新闻收藏数量排行榜。
    """
    sql = """
        select
            n.id as news_id,
            n.title,
            n.category_id,
            n.views,
            n.publish_time,
            count(f.id) as favorite_count
        from news n
        left join favorite f on f.news_id = n.id
    """

    params = {"limit": limit}

    if category_id is not None:
        sql += " where n.category_id = :category_id"
        params["category_id"] = category_id

    sql += """
        group by n.id, n.title, n.category_id, n.views, n.publish_time
        order by favorite_count desc, n.id desc
        limit :limit
    """

    res = await db.execute(text(sql), params)
    rows = res.mappings().all()
    return rows


async def get_news_peak_concurrent_viewers(
    db: AsyncSession,
    stat_date: date,
    limit: int = 10,
    category_id: int | None = None,
):
    """
    查询新闻峰值并发观看人数。
    当前项目尚未落地观看会话/心跳基础表，无法计算真实并发值。
    为了让接口可用，这里先返回空结果。
    """
    _ = db, stat_date, limit, category_id
    return [], 0

