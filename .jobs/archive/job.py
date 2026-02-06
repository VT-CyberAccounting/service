import pandas as pd
import zipfile, httpx, io
import psycopg
from os import getenv

urls = [
	"https://www.sec.gov/files/dera/data/financial-statement-data-sets-archive/2024q4-archive.zip"
]

client = httpx.Client(
	headers={
		"User-Agent": "CyberAccounting samartha@vt.edu"
	}
)

pgclient = psycopg.connect(
	f"dbname=postgres user=postgres password={getenv("POSTGRES_PASSWORD")} host=db"
)

for url in urls:
	response = client.get(url)
	if response.status_code == 200:
		with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
			zf.extractall(path=".data")
			zf.close()
			response.close()
			del zf, response
			sub = pd.read_csv(
				".data/sub.txt",
				sep="\t",
				dtype={
					'adsh': str,
					'cik': str,
					'fy': str
				}
			)
			num = pd.read_csv(
				".data/num.txt",
				sep="\t",
				dtype={
					'adsh': str,
					'version': str,
					'ddate': str
				}
			)

			sub = sub[
				sub['form']=="10-Q"
			][
				["adsh", "cik", "name", "fy", "fp"]
			]

			num = num[
				num['adsh'].isin(sub['adsh'])
			][
				num['version'].str.contains('us-gaap', case=False, na=False)
			][
				num['tag'].isin(
					[
						'Revenues',
					    'CostsAndExpenses',
					    'EarningsPerShareBasic'
					]
				)
			].pivot_table(
				index='adsh',
				columns='tag',
				values='value',
				aggfunc='max'
			).reset_index()

			res = pd.merge(
				sub,
				num,
				on='adsh',
				how='left'
			).rename(
				columns={
					"adsh": "accn",
					"EarningsPerShareBasic": "eps",
					"CostsAndExpenses": "costs",
					"Revenues": "revenues",
				}
			).dropna(
				subset=["costs", "revenues", "eps"],
			)
			batch = list(res.itertuples(index=False, name=None))
			with pgclient.cursor() as cur:
				cur.executemany(
					"""
					INSERT INTO financials (accn, cik, name, fy, fp, costs, eps, revenues)
					VALUES (%s, %s, %s, %s, %s, %s, %s)
					ON CONFLICT (adsh) DO UPDATE SET
						revenues = EXCLUDED.revenues,
						costs = EXCLUDED.costs,
						eps = EXCLUDED.eps;
					""",
					batch
				)
				pgclient.commit()