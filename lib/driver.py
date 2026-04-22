from os import getenv

from minio import Minio
from sqlalchemy.ext.asyncio import create_async_engine


class AlchemyDriver:
    @classmethod
    def init(cls):
        cls.engine = create_async_engine(
            f"postgresql+psycopg://postgres:{getenv('POSTGRES_PASSWORD')}@db:80/postgres",
            pool_pre_ping=True,
        )
        cls.client = Minio(
            getenv("S3_URL"),
            access_key="minio",
            secret_key=getenv("MINIO_PASSWORD"),
            secure=True,
        )

    @classmethod
    async def close(cls):
        await cls.engine.dispose()