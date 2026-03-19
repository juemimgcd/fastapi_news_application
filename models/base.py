from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from datetime import datetime
from sqlalchemy import DateTime, func


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="created time"
    )

    updated_time: Mapped[datetime] = mapped_column(
        DateTime,
        insert_default=func.now(),
        nullable=False,
        comment="updated time"
    )
