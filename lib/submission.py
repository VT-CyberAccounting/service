from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlmodel import SQLModel, Field, select
import strawberry
from sqlmodel.ext.asyncio.session import AsyncSession

from .driver import AlchemyDriver


class SubmissionClass(SQLModel, table=True):
    __tablename__ = "submissions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str
    label: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


@strawberry.type
class Submission:
    label: Optional[str] = None
    url: Optional[str] = None
    created_at: Optional[datetime] = None


@strawberry.type
class Query:
    @strawberry.field
    async def getSubmission(
        self,
        info: strawberry.Info,
        username: Optional[str] = None,
        label: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Submission]:
        process_url: bool = any(
            f.name == "url"
            for sel in info.selected_fields
            for f in sel.selections
        )
        query = select(SubmissionClass)
        if username is not None:
            query = query.where(SubmissionClass.username == username)
        if label is not None:
            query = query.where(SubmissionClass.label == label)
        query = query.order_by(SubmissionClass.created_at.desc())
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        async with AsyncSession(AlchemyDriver.engine) as session:
            rows = (await session.exec(query)).all()
        return [
            Submission(
                label=r.label,
                url=(
                    AlchemyDriver.client.presigned_get_object(
                        "submissions",
                        f"{r.id}.csv",
                        expires=timedelta(minutes=5),
                    )
                    if process_url
                    else None
                ),
                created_at=r.created_at,
            )
            for r in rows
        ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def insertSubmission(self, username: str, label: str) -> str:
        row = SubmissionClass(username=username, label=label)
        async with AsyncSession(AlchemyDriver.engine) as session:
            session.add(row)
            await session.commit()
            await session.refresh(row)
        return AlchemyDriver.client.presigned_put_object(
            "submissions",
            f"{row.id}.csv",
            expires=timedelta(minutes=5),
        )

    @strawberry.mutation
    async def updateSubmission(self) -> None:
        return None

    @strawberry.mutation
    async def deleteSubmission(self) -> None:
        return None
