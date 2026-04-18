import asyncio
import io
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

import strawberry
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from strawberry.file_uploads import Upload

from .driver import AlchemyDriver
from .s3 import S3Driver


class Submission(SQLModel, table=True):
    __tablename__ = "submissions"

    id: Optional[UUID] = Field(default=None, primary_key=True)
    username: str
    label: str
    created_at: Optional[datetime] = None


@strawberry.type
class SubmissionGQL:
    id: UUID
    username: str
    label: str
    created_at: datetime


async def _find(session: AsyncSession, username: str, label: str) -> Optional[Submission]:
    return (await session.exec(
        select(Submission).where(
            Submission.username == username,
            Submission.label == label,
        )
    )).first()


@strawberry.type
class SubmissionQuery:
    @strawberry.field
    async def submissions(self, username: str) -> List[SubmissionGQL]:
        async with AsyncSession(AlchemyDriver.engine) as session:
            rows = (await session.exec(
                select(Submission)
                .where(Submission.username == username)
                .order_by(Submission.created_at.desc())
            )).all()
        return [
            SubmissionGQL(id=r.id, username=r.username, label=r.label, created_at=r.created_at)
            for r in rows
        ]

    @strawberry.field
    async def download(self, username: str, label: str) -> Optional[str]:
        async with AsyncSession(AlchemyDriver.engine) as session:
            row = await _find(session, username, label)
        if row is None:
            return None
        return S3Driver.client.presigned_get_object(
            S3Driver.bucket,
            str(row.id),
            expires=timedelta(minutes=5),
        )


@strawberry.type
class SubmissionMutation:
    @strawberry.mutation
    async def create_submission(
        self,
        username: str,
        label: str,
        file: Upload,
    ) -> SubmissionGQL:
        if not username.strip() or not label.strip():
            raise ValueError("username and label must be non-empty")

        data = await file.read()
        if not data:
            raise ValueError("file is empty")

        sub = Submission(username=username, label=label)
        async with AsyncSession(AlchemyDriver.engine) as session:
            session.add(sub)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise ValueError(f"submission '{label}' already exists for '{username}'")
            await session.refresh(sub)

        try:
            await asyncio.to_thread(
                S3Driver.client.put_object,
                S3Driver.bucket,
                str(sub.id),
                io.BytesIO(data),
                len(data),
                "text/csv",
            )
        except Exception:
            async with AsyncSession(AlchemyDriver.engine) as session:
                orphan = await session.get(Submission, sub.id)
                if orphan is not None:
                    await session.delete(orphan)
                    await session.commit()
            raise

        return SubmissionGQL(
            id=sub.id,
            username=sub.username,
            label=sub.label,
            created_at=sub.created_at,
        )

    @strawberry.mutation
    async def update_submission(
        self,
        username: str,
        label: str,
        new_label: str,
    ) -> SubmissionGQL:
        if not new_label.strip():
            raise ValueError("new_label must be non-empty")

        async with AsyncSession(AlchemyDriver.engine) as session:
            row = await _find(session, username, label)
            if row is None:
                raise ValueError(f"submission '{label}' not found for '{username}'")
            row.label = new_label
            session.add(row)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise ValueError(f"submission '{new_label}' already exists for '{username}'")
            await session.refresh(row)

        return SubmissionGQL(
            id=row.id,
            username=row.username,
            label=row.label,
            created_at=row.created_at,
        )

    @strawberry.mutation
    async def delete_submission(self, username: str, label: str) -> bool:
        async with AsyncSession(AlchemyDriver.engine) as session:
            row = await _find(session, username, label)
            if row is None:
                return False
            sub_id = row.id
            await session.delete(row)
            await session.commit()
        await asyncio.to_thread(S3Driver.client.remove_object, S3Driver.bucket, str(sub_id))
        return True