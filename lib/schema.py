from os import getenv
from typing import List, Optional

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, Field, select
import strawberry
from sqlmodel.ext.asyncio.session import AsyncSession


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

class slnSQL(SQLModel, table=True):
    __tablename__ = "sln"

    id: int = Field(primary_key=True)
    ticker: str
    year: int
    cik: str
    name: str
    environmental: Optional[float] = None
    social: Optional[float] = None
    governance: Optional[float] = None
    esg: Optional[float] = None
    gvkey: Optional[float] = None
    sic: Optional[float] = None
    current_assets: Optional[float] = None
    assets: Optional[float] = None
    cash: Optional[float] = None
    inventory: Optional[float] = None
    current_marketable_securities: Optional[float] = None
    current_liabilities: Optional[float] = None
    liabilities: Optional[float] = None
    property_plant_equipment: Optional[float] = None
    pref_stock: Optional[float] = None
    allowance_doubtful_receivables: Optional[float] = None
    total_receivables: Optional[float] = None
    stockholders_equity: Optional[float] = None
    cost_goods_sold: Optional[float] = None
    dividends_pref: Optional[float] = None
    dividends: Optional[float] = None
    earnings_before_interest_taxes: Optional[float] = None
    earnings_per_share_basic: Optional[float] = None
    net_income_loss: Optional[float] = None
    net_income_adjusted_common_stocks: Optional[float] = None
    sales_by_turnover: Optional[float] = None
    interest_related_expense: Optional[float] = None
    common_shares_outstanding: Optional[float] = None
    total_debt_including_current: Optional[float] = None
    price_closed_annual: Optional[float] = None
    net_receivables: Optional[float] = None
    total_assets_last_year: Optional[float] = None
    net_receivables_last_year: Optional[float] = None
    inventory_last_year: Optional[float] = None
    stockholders_equity_last_year: Optional[float] = None
    cost_goods_sold_last_year: Optional[float] = None
    common_shares_outstanding_last_year: Optional[float] = None
    working_capital: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    accounts_receivable_turnover: Optional[float] = None
    average_days_to_collect_receivables: Optional[float] = None
    inventory_turnover: Optional[float] = None
    average_days_to_collect_inventory: Optional[float] = None
    debt_to_assets: Optional[float] = None
    debt_to_equity: Optional[float] = None
    number_of_times_interest_is_earned: Optional[float] = None
    net_margin: Optional[float] = None
    asset_turnover_ratio: Optional[float] = None
    return_on_investment: Optional[float] = None
    return_on_equity: Optional[float] = None
    earnings_per_share: Optional[float] = None
    book_value_per_share: Optional[float] = None
    price_earnings_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    industry: Optional[str] = None

@strawberry.experimental.pydantic.type(model=slnSQL, all_fields=True)
class slnGQL:
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
            conditions.append(column.bool_op('%>')(self.contains))
        if self.startswith is not None:
            conditions.append(column.startswith(self.startswith))
        if self.endswith is not None:
            conditions.append(column.endswith(self.endswith))
        return conditions

@strawberry.type
class Query:
    @strawberry.field
    async def sln(
            self,
            id: Optional[int] = None,
            cik: Optional[str] = None,
            ticker: Optional[str] = None,
            name: Optional[strf] = None,
            year: Optional[int] = None,
    ) -> List[slnGQL]:
        conditions = []
        if id is not None:
            conditions.append(slnSQL.id == id)
        if cik:
            conditions.append(slnSQL.cik == cik)
        if ticker:
            conditions.append(slnSQL.ticker == ticker)
        if name:
            conditions.extend(name.apply(slnSQL.name))
        if year is not None:
            conditions.append(slnSQL.year == year)
        query = select(slnSQL).limit(100)
        if len(conditions) > 0:
            query = query.where(*conditions)
        async with AsyncSession(AlchemyDriver.engine) as session:
            return (await session.exec(query)).all()
