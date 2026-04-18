from os import getenv

from sqlalchemy.ext.asyncio import create_async_engine


class AlchemyDriver:
    @classmethod
    def init(cls):
        cls.engine = create_async_engine(
            f"postgresql+psycopg://postgres:{getenv('POSTGRES_PASSWORD')}@db:80/postgres",
            pool_pre_ping=True,
        )

    @classmethod
    async def close(cls):
        await cls.engine.dispose()