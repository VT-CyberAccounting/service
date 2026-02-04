from litestar import Litestar, get
from typing import *

from litestar.exceptions import HTTPException
from litestar.params import Parameter
from psycopg import AsyncConnection, Error
from os import getenv

client: AsyncConnection

async def startup():
    global client
    client = await AsyncConnection.connect(
        conninfo=f"postgresql://postgres:{getenv('POSTGRES_PASSWORD')}@db:80/postgres"
    )

async def close():
    global client
    await client.close()

@get("/data")
async def data(
        ciks: List[str] = Parameter(
            required=True,
            description="cik associated with company",
            default=None
        )
) -> Dict[str, Dict[str, int]]:
    global client
    res = {}
    cursor = client.cursor()
    for cik in ciks:
        try:
            await cursor.execute("SELECT revenues, operatingexpenses, incometaxexpensebenefit FROM data WHERE cik = %s", (cik,))
        except Error as e:
            await client.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        comp = await cursor.fetchone()
        res[cik] = {
            "revenue": comp[0],
            "expense": comp[1],
            "tax": comp[2]
        }
    return res

app = Litestar(
    route_handlers=[data],
    on_startup=[startup],
    on_shutdown=[close],
    debug=True
)