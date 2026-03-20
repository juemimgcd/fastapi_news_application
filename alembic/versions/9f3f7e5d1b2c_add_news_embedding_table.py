"""add news embedding table

Revision ID: 9f3f7e5d1b2c
Revises: 3454695b00e1
Create Date: 2026-03-20 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f3f7e5d1b2c"
down_revision: Union[str, Sequence[str], None] = "3454695b00e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "news_embedding",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="向量记录ID"),
        sa.Column("news_id", sa.Integer(), nullable=False, comment="新闻ID"),
        sa.Column("embedding_model", sa.String(length=100), nullable=False, comment="Embedding模型名称"),
        sa.Column("content_hash", sa.String(length=64), nullable=False, comment="新闻内容哈希"),
        sa.Column("embedding", sa.JSON(), nullable=False, comment="新闻向量"),
        sa.Column("generated_at", sa.DateTime(), nullable=False, comment="向量生成时间"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="created time"),
        sa.Column("updated_time", sa.DateTime(), nullable=False, comment="updated time"),
        sa.ForeignKeyConstraint(["news_id"], ["news.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("news_embedding_news_id_unique_idx", "news_embedding", ["news_id"], unique=True)
    op.create_index("idx_news_embedding_content_hash", "news_embedding", ["content_hash"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_news_embedding_content_hash", table_name="news_embedding")
    op.drop_index("news_embedding_news_id_unique_idx", table_name="news_embedding")
    op.drop_table("news_embedding")
