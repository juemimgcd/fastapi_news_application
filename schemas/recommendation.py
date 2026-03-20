from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.base import NewsItemBase


class RecommendationNewsItemResponse(NewsItemBase):
    score: float
    reason: str

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


class RecommendationListResponse(BaseModel):
    list: list[RecommendationNewsItemResponse]
    total: int
    profile_source: str = Field(alias="profileSource")
    generated_at: datetime = Field(alias="generatedAt")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )
