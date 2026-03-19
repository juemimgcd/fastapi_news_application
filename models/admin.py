from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Admin(Base):
    """
    管理员表ORM模型。
    """
    __tablename__ = "admin"

    __table_args__ = (
        Index("admin_username_unique_idx", "username"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="管理员ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="管理员用户名")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="管理员密码（加密存储）")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="管理员昵称")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="是否启用")
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="最后登录时间")

    def __repr__(self):
        return f"<Admin(id={self.id}, username='{self.username}', is_active={self.is_active})>"


class AdminToken(Base):
    """
    管理员令牌表ORM模型。
    """
    __tablename__ = "admin_token"

    __table_args__ = (
        Index("admin_token_unique_idx", "token"),
        Index("idx_admin_token_admin_id", "admin_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="管理员令牌ID")
    admin_id: Mapped[int] = mapped_column(Integer, ForeignKey(Admin.id), nullable=False, comment="管理员ID")
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment="令牌值")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="过期时间")

    def __repr__(self):
        return f"<AdminToken(id={self.id}, admin_id={self.admin_id}, token='{self.token}')>"
