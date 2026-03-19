from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from utils.response import success_response
from conf.db_conf import get_database
from crud import admin
from models.admin import Admin
from schemas.admin import (
    AdminAuthResponse,
    AdminLoginRequest,
    AdminLoginStreakListResponse,
    AdminNewsFavoriteRankingResponse,
    AdminNewsPeakConcurrentViewResponse,
    AdminNewsListResponse,
    AdminUserListResponse,
    AdminInfoResponse
)
from utils.admin_auth import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/login")
async def login_admin(data: AdminLoginRequest, db: AsyncSession = Depends(get_database)):
    """
    管理员登录接口。
    你实现时建议：
    返回 AdminAuthResponse。
    """
    super_user = await admin.authenticate_admin(db=db,username=data.username,password=data.password)

    if not super_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="wrong admin username or password")
    
    token = await admin.create_admin_token(db=db,admin_id=super_user.id)
    resp = AdminAuthResponse(token=token,admin_info=AdminInfoResponse.model_validate(super_user))
    return success_response(data=resp)






@router.get("/users")
async def get_admin_user_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    keyword: str | None = Query(None),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_database),
):
    """
    管理员分页查询全部用户。
    你实现时建议调用 crud.admin.get_admin_user_list，并返回 AdminUserListResponse。
    """
    rows,total = await admin.get_admin_user_list(
        db=db,
        page=page,
        page_size=page_size,
        keyword=keyword
    )

    has_more = page * page_size < total

    data = AdminUserListResponse(list=rows,total=total,page=page,pageSize=page_size,hasMore=has_more)

    return success_response(data=data)





@router.get("/news")
async def get_admin_news_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    keyword: str | None = Query(None),
    category_id: int | None = Query(None, alias="categoryId"),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_database),
):
    """
    管理员分页查询全部新闻。
    你实现时建议调用 crud.admin.get_admin_news_list，并返回 AdminNewsListResponse。
    """
    rows,total = await admin.get_admin_news_list(
        db=db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        category_id=category_id
    )
    has_more = page * page_size < total

    data = AdminNewsListResponse(list=rows,total=total,page=page,pageSize=page_size,hasMore=has_more)
    return success_response(data=data)










































@router.get("/users/login-streak")
async def get_users_with_login_streak(
    days: int = Query(..., ge=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_database),
):
    """
    查询连续登录 n 天的用户列表。
    你实现时建议调用 crud.admin.get_users_with_login_streak，并返回 AdminLoginStreakListResponse。
    """
    rows, total = await admin.get_users_with_login_streak(
        db=db,
        days=days,
        page=page,
        page_size=page_size,
    )
    data = AdminLoginStreakListResponse(days=days, list=rows, total=total)
    return success_response(data=data)


@router.get("/news/favorite-ranking")
async def get_news_favorite_ranking(
    limit: int = Query(10, ge=1, le=100),
    category_id: int | None = Query(None, alias="categoryId"),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_database),
):
    """
    查询新闻收藏数量排行榜。
    你实现时建议调用 crud.admin.get_news_favorite_ranking，并返回 AdminNewsFavoriteRankingResponse。
    """
    rows = await admin.get_news_favorite_ranking(
        db=db,
        limit=limit,
        category_id=category_id,
    )
    data = AdminNewsFavoriteRankingResponse(list=rows, limit=limit)
    return success_response(data=data)


@router.get("/news/peak-concurrent-viewers")
async def get_news_peak_concurrent_viewers(
    stat_date: str = Query(..., alias="date"),
    limit: int = Query(10, ge=1, le=100),
    category_id: int | None = Query(None, alias="categoryId"),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_database),
):
    """
    查询指定日期内每个新闻的最大同时观看人数。
    你实现时建议：
    1. 调用 crud.admin.get_news_peak_concurrent_viewers。
    2. 返回 AdminNewsPeakConcurrentViewResponse。
    3. 如果当前表结构没有观看会话/心跳数据，这个接口需要先补统计基础表。
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="admin peak concurrent viewers query not implemented yet",
    )
