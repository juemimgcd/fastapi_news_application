from fastapi import APIRouter, Depends, Query, HTTPException
from starlette import status

from conf.db_conf import get_database
from sqlalchemy.ext.asyncio import AsyncSession
from crud import history
from utils.response import success_response
from schemas.history import HistoryAddRequest, HistoryListResponse, HistoryNewsItemResponse
from models.users import User
from utils.auth import get_current_user

router = APIRouter(prefix="/api/history", tags=["history"])


@router.post("/add")
async def add_history(
        data: HistoryAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_database)
):
    result = await history.add_history(db, user.id, data.news_id)

    return success_response(message="success", data=result)


@router.get("/list")
async def get_history_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_database)

):
    rows, total = await history.get_history_list(db, user.id, page, page_size)
    hasMore = total > page * page_size

    history_list = [HistoryNewsItemResponse.model_validate({
        **news.__dict__,
        "view_time": view_time,
        "history_id": history_id
    }) for news, view_time, history_id in rows]

    data = HistoryListResponse(list=history_list, total=total, has_more=hasMore)

    return success_response(message="success", data=data)


@router.delete("/delete/{history_id}")
async def delete_history(history_id: int,
                         user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_database)):
    """
    删除历史记录
    """
    result = await history.delete_history(db, user.id, history_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史记录不存在")
    return success_response(message="删除成功")


@router.delete("/clear")
async def clear_history(user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_database)):
    """
    清空历史记录
    """
    result = await history.clear_history(db, user.id)
    return success_response(message="清空成功")
