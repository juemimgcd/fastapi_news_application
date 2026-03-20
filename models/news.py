from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import JSON, DateTime, String, Integer, Index, Text, ForeignKey
from models.base import Base



class Category(Base):
    __tablename__ = "news_category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __str__(self):
        return f"<Category(id={self.id},name={self.name},sort_order={self.sort_order})>"


class News(Base):
    __tablename__ = "news"

    # 创建索引：提升查询速度 → 添加目录
    __table_args__ = (
        Index('fk_news_category_idx', 'category_id'),  # 高频查询场景
        Index('idx_publish_time', 'publish_time')  # 按发布时间排序
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="新闻ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="新闻标题")
    description: Mapped[Optional[str]] = mapped_column(String(500), comment="新闻简介")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="新闻内容")
    image: Mapped[Optional[str]] = mapped_column(String(255), comment="封面图片URL")
    author: Mapped[Optional[str]] = mapped_column(String(50), comment="作者")
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('news_category.id'), nullable=False, comment="分类ID")
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="浏览量")
    publish_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="发布时间")

    def __repr__(self):
        return f"<News(id={self.id}, title='{self.title}', views={self.views})>"


class NewsEmbedding(Base):
    __tablename__ = "news_embedding"

    __table_args__ = (
        Index("news_embedding_news_id_unique_idx", "news_id", unique=True),
        Index("idx_news_embedding_content_hash", "content_hash"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="向量记录ID")
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey("news.id"), nullable=False, comment="新闻ID")
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False, comment="Embedding模型名称")
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, comment="新闻内容哈希")
    embedding: Mapped[list[float]] = mapped_column(JSON, nullable=False, comment="新闻向量")
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, comment="向量生成时间")

    def __repr__(self):
        return f"<NewsEmbedding(news_id={self.news_id}, embedding_model='{self.embedding_model}')>"
