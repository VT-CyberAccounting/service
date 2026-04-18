from os import getenv

from minio import Minio
class S3Driver:
    bucket = "submissions"

    @classmethod
    def init(cls):
        cls.client = Minio(
            "s3:80",
            access_key="minio",
            secret_key=getenv("MINIO_ROOT_PASSWORD"),
            secure=False,
        )
