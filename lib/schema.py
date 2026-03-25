from os import getenv
from typing import List, Optional

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, Field, select
import strawberry
from sqlmodel.ext.asyncio.session import AsyncSession


class AlchemyDriver:
    @classmethod
    def init(cls):
        cls.engine = create_async_engine(f"postgresql+psycopg://postgres:{getenv('POSTGRES_PASSWORD')}@db:80/postgres")

    @classmethod
    async def close(cls):
        await cls.engine.dispose()

class financialsSQL(SQLModel, table=True):
    __tablename__ = "financials"

    accn: str = Field(primary_key=True)
    cik: str
    name: str
    fy: int
    fp: str
    costs: float
    eps: float
    revenues: float
    taxes: float

@strawberry.experimental.pydantic.type(model=financialsSQL, all_fields=True)
class financialsGQL:
    pass

@strawberry.input
class numf:
    eq: Optional[float] = None
    gt: Optional[float] = None
    gte: Optional[float] = None
    lt: Optional[float] = None
    lte: Optional[float] = None
    def apply(self, column):
        conditions = []
        if self.eq is not None:
            conditions.append(column == self.eq)
        if self.gt is not None:
            conditions.append(column > self.gt)
        if self.gte is not None:
            conditions.append(column >= self.gte)
        if self.lt is not None:
            conditions.append(column < self.lt)
        if self.lte is not None:
            conditions.append(column <= self.lte)
        return conditions


@strawberry.input
class strf:
    eq: Optional[str] = None
    contains: Optional[str] = None
    startswith: Optional[str] = None
    endswith: Optional[str] = None
    def apply(self, column):
        conditions = []
        if self.eq is not None:
            conditions.append(column == self.eq)
        if self.contains is not None:
            conditions.append(column.bool_op('<%')(self.contains))
        if self.startswith is not None:
            conditions.append(column.startswith(self.startswith))
        if self.endswith is not None:
            conditions.append(column.endswith(self.endswith))
        return conditions

@strawberry.type
class Query:
    @strawberry.field
    async def financials(
            self,
            accn: Optional[str] = None,
            cik: Optional[str] = None,
            name: Optional[strf] = None,
            fy: Optional[numf] = None,
            fp: Optional[strf] = None,
            costs: Optional[numf] = None,
            eps: Optional[numf] = None,
            revenues: Optional[numf] = None,
            taxes: Optional[numf] = None,
    ) -> List[financialsGQL]:
        conditions = []
        if accn:
            conditions.append(financialsSQL.accn == accn)
        if cik:
            conditions.append(financialsSQL.cik == cik)
        if name:
            conditions.extend(name.apply(financialsSQL.name))
        if fy:
            conditions.extend(fy.apply(financialsSQL.fy))
        if fp:
            conditions.extend(fp.apply(financialsSQL.fp))
        if costs:
            conditions.extend(costs.apply(financialsSQL.costs))
        if eps:
            conditions.extend(eps.apply(financialsSQL.eps))
        if revenues:
            conditions.extend(revenues.apply(financialsSQL.revenues))
        if taxes:
            conditions.extend(taxes.apply(financialsSQL.taxes))
        query = select(financialsSQL).limit(100)
        if len(conditions) > 0:
            query = query.where(*conditions)
        async with AsyncSession(AlchemyDriver.engine) as session:
            return (await session.exec(query)).all()
