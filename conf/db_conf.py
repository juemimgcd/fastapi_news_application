from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from conf.settings import settings



engine = create_async_engine(
    settings.async_database_url,
    echo=False,
    pool_size=20,
    max_overflow=10
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False

)


async def get_database():
    async with AsyncSessionLocal as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()
