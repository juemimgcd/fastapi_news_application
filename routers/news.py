from fastapi import APIRouter, Depends, Query, HTTPException
from conf.db_conf import get_database
from sqlalchemy.ext.asyncio import AsyncSession
from crud import news
from utils.response import success_response

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories")
async def get_categories(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        db: AsyncSession = Depends(get_database)
):
    categories = await news.get_categories(db, skip, limit)
    return success_response(message='success', data=categories)


@router.get("/list")
async def get_news_list(category_id: int = Query(..., alias="categoryId", ge=1),
                        page: int = Query(1, ge=1),
                        page_size: int = Query(10, alias="pageSize", ge=1, le=100),
                        db: AsyncSession = Depends(get_database)
                        ):
    offset = (page - 1) * page_size
    news_list = await news.get_news_list(db, category_id, offset, page_size)
    total = await news.get_news_total(db, category_id)

    has_more = (offset + len(news_list)) < (total or 0)
    return success_response(message='success', data={
        "items": news_list,
        "total": total or 0,
        "page": page,
        "pageSize": page_size,
        "hasMore": has_more,
    })


@router.get("/detail")
async def get_news_detail(
        news_id: int = Query(..., alias="id"),
        db: AsyncSession = Depends(get_database)

):
    detail_info = await news.get_news_detail(db, news_id)

    if not detail_info:
        raise HTTPException(status_code=404, detail="not found")

    await news.increase_news_views(db, news_id)

    related_news = await news.get_related_news(db, detail_info.category_id, detail_info.id)

    return success_response(message="success", data={
        "detail": detail_info,
        "related": related_news,
    })
