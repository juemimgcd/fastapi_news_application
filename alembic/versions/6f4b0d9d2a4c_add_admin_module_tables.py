"""add admin module tables

Revision ID: 6f4b0d9d2a4c
Revises: dd73c4fe6eee
Create Date: 2026-03-19 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6f4b0d9d2a4c"
down_revision: Union[str, Sequence[str], None] = "dd73c4fe6eee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="管理员ID"),
        sa.Column("username", sa.String(length=50), nullable=False, comment="管理员用户名"),
        sa.Column("password", sa.String(length=255), nullable=False, comment="管理员密码（加密存储）"),
        sa.Column("nickname", sa.String(length=50), nullable=True, comment="管理员昵称"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true"), comment="是否启用"),
        sa.Column("last_login_at", sa.DateTime(), nullable=True, comment="最后登录时间"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="created time"),
        sa.Column("updated_time", sa.DateTime(), nullable=False, comment="updated time"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("admin_username_unique_idx", "admin", ["username"], unique=False)

    op.create_table(
        "admin_token",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="管理员令牌ID"),
        sa.Column("admin_id", sa.Integer(), nullable=False, comment="管理员ID"),
        sa.Column("token", sa.String(length=255), nullable=False, comment="令牌值"),
        sa.Column("expires_at", sa.DateTime(), nullable=False, comment="过期时间"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="created time"),
        sa.Column("updated_time", sa.DateTime(), nullable=False, comment="updated time"),
        sa.ForeignKeyConstraint(["admin_id"], ["admin.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )
    op.create_index("admin_token_unique_idx", "admin_token", ["token"], unique=False)
    op.create_index("idx_admin_token_admin_id", "admin_token", ["admin_id"], unique=False)

    op.create_table(
        "user_login_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="登录记录ID"),
        sa.Column("user_id", sa.Integer(), nullable=False, comment="用户ID"),
        sa.Column("login_date", sa.Date(), nullable=False, comment="登录日期"),
        sa.Column("login_at", sa.DateTime(), nullable=False, comment="登录时间"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="created time"),
        sa.Column("updated_time", sa.DateTime(), nullable=False, comment="updated time"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "login_date", name="user_login_date_unique"),
    )
    op.create_index("idx_user_login_log_login_date", "user_login_log", ["login_date"], unique=False)
    op.create_index("idx_user_login_log_user_id", "user_login_log", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_user_login_log_user_id", table_name="user_login_log")
    op.drop_index("idx_user_login_log_login_date", table_name="user_login_log")
    op.drop_table("user_login_log")

    op.drop_index("idx_admin_token_admin_id", table_name="admin_token")
    op.drop_index("admin_token_unique_idx", table_name="admin_token")
    op.drop_table("admin_token")

    op.drop_index("admin_username_unique_idx", table_name="admin")
    op.drop_table("admin")
