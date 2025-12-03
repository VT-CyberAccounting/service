from litestar import Litestar, get
from httpx import AsyncClient
from typing import *
from litestar.params import Parameter
from lib.net import ThrottledTransport

client: AsyncClient

def startup():
    global client
    client = AsyncClient(
        transport=ThrottledTransport(
            delay=0.5
        ),
	    headers={
		    'User-Agent': 'CyberAccounting samartha@vt.edu'
	    }
    )

def close():
    global client
    client.aclose()

@get("/data")
async def data(
        ciks: List[str] = Parameter(
			required=False,
			description="cik associated with company",
			default=None
		)
) -> Dict[str, Dict[str, int]]:
	global client
	res = {}
	for cik in ciks:
		comp = (await client.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json")).json()
		res[cik] = {
			"revenue": comp['facts']['us-gaap']['Revenues']['units']['USD'][-1]["val"],
			"expense": comp['facts']['us-gaap']['OperatingExpenses']['units']['USD'][-1]["val"],
			"tax": comp['facts']['us-gaap']['IncomeTaxExpenseBenefit']['units']['USD'][-1]["val"]
		}
	return res

app = Litestar(
    route_handlers=[data],
    on_startup=[startup],
    on_shutdown=[close],
	debug=True
)