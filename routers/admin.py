from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from conf.db_conf import get_database
from crud import admin
from models.admin import Admin
from schemas.admin import (
    AdminAuthResponse,
    AdminInfoResponse,
    AdminLoginRequest,
    AdminLoginStreakListResponse,
    AdminLoginStreakUserResponse,
    AdminNewsItemResponse,
    AdminNewsFavoriteRankingResponse,
    AdminNewsListResponse,
    AdminNewsPeakConcurrentViewItemResponse,
    AdminNewsPeakConcurrentViewResponse,
    AdminUserItemResponse,
    AdminUserListResponse,
    AdminNewsFavoriteRankingItemResponse
)
from utils.admin_auth import get_current_admin
from utils.response import success_response

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/login")
async def login_admin(data: AdminLoginRequest, db: AsyncSession = Depends(get_database)):
    super_user = await admin.authenticate_admin(db=db, username=data.username, password=data.password)
    if not super_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="wrong admin username or password",
        )

    token = await admin.create_admin_token(db=db, admin_id=super_user.id)
    resp = AdminAuthResponse(token=token, admin_info=AdminInfoResponse.model_validate(super_user))
    return success_response(data=resp)


@router.get("/users")
async def get_admin_user_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    keyword: str | None = Query(None),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_database),
):
    rows, total = await admin.get_admin_user_list(
        db=db,
        page=page,
        page_size=page_size,
        keyword=keyword,
    )
    user_rows = [AdminUserItemResponse.model_validate(row) for row in rows]
    has_more = page * page_size < total
    data = AdminUserListResponse(
        list=user_rows,
        total=total,
        page=page,
        pageSize=page_size,
        hasMore=has_more,
    )
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
    rows, total = await admin.get_admin_news_list(
        db=db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        category_id=category_id,
    )
    news_rows = [AdminNewsItemResponse.model_validate(row) for row in rows]
    has_more = page * page_size < total
    data = AdminNewsListResponse(
        list=news_rows,
        total=total,
        page=page,
        pageSize=page_size,
        hasMore=has_more,
    )
    return success_response(data=data)


@router.get("/users/login-streak")
async def get_users_with_login_streak(
    days: int = Query(..., ge=1, lt=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_database),
):
    rows, total = await admin.get_users_with_login_streak(
        db=db,
        days=days,
        page=page,
        page_size=page_size,
    )
    user_rows = [AdminLoginStreakUserResponse.model_validate(row) for row in rows]
    data = AdminLoginStreakListResponse(days=days, list=user_rows, total=total)
    return success_response(data=data)



@router.get("/news/favorite-ranking")
async def get_news_favorite_ranking(
    limit: int = Query(10, ge=1, le=100),
    category_id: int | None = Query(None, alias="categoryId"),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_database),
):
    rows = await admin.get_news_favorite_ranking(
        db=db,
        limit=limit,
        category_id=category_id,
    )
    favorite_rows = [AdminNewsFavoriteRankingItemResponse.model_validate(row) for row in rows]


    data = AdminNewsFavoriteRankingResponse(list=favorite_rows, limit=limit)
    return success_response(data=data)




@router.get("/news/peak-concurrent-viewers")
async def get_news_peak_concurrent_viewers(
    stat_date: date = Query(..., alias="date"),
    limit: int = Query(10, ge=1, le=100),
    category_id: int | None = Query(None, alias="categoryId"),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_database),
):
    rows, total = await admin.get_news_peak_concurrent_viewers(
        db=db,
        stat_date=stat_date,
        limit=limit,
        category_id=category_id,
    )
    peak_rows = [AdminNewsPeakConcurrentViewItemResponse.model_validate(row) for row in rows]
    data = AdminNewsPeakConcurrentViewResponse(
        date=stat_date,
        list=peak_rows,
        total=total,
        limit=limit,
    )
    return success_response(data=data)
