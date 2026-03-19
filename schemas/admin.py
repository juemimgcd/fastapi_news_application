from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from schemas.base import NewsItemBase


class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=6)


class AdminInfoResponse(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    is_active: bool = Field(alias="isActive")
    last_login_at: Optional[datetime] = Field(default=None, alias="lastLoginAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminAuthResponse(BaseModel):
    token: str
    admin_info: AdminInfoResponse = Field(alias="adminInfo")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminUserItemResponse(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminUserListResponse(BaseModel):
    list: list[AdminUserItemResponse]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminNewsItemResponse(NewsItemBase):
    favorite_count: int = Field(default=0, alias="favoriteCount")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminNewsListResponse(BaseModel):
    list: list[AdminNewsItemResponse]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminLoginStreakUserResponse(BaseModel):
    user_id: int = Field(alias="userId")
    username: str
    nickname: Optional[str] = None
    streak_days: int = Field(alias="streakDays")
    last_login_date: date | None = Field(default=None, alias="lastLoginDate")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminLoginStreakListResponse(BaseModel):
    days: int
    list: list[AdminLoginStreakUserResponse]
    total: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminNewsFavoriteRankingItemResponse(BaseModel):
    news_id: int = Field(alias="newsId")
    title: str
    category_id: int = Field(alias="categoryId")
    views: int
    publish_time: Optional[datetime] = Field(default=None, alias="publishTime")
    favorite_count: int = Field(alias="favoriteCount")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminNewsFavoriteRankingResponse(BaseModel):
    list: list[AdminNewsFavoriteRankingItemResponse]
    limit: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminNewsPeakConcurrentViewItemResponse(BaseModel):
    news_id: int = Field(alias="newsId")
    title: str
    category_id: int = Field(alias="categoryId")
    stat_date: date = Field(alias="statDate")
    peak_concurrent_viewers: int = Field(alias="peakConcurrentViewers")
    peak_time: Optional[datetime] = Field(default=None, alias="peakTime")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminNewsPeakConcurrentViewResponse(BaseModel):
    date: date
    list: list[AdminNewsPeakConcurrentViewItemResponse]
    total: int
    limit: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
