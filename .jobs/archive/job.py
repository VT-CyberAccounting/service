import pandas as pd
import zipfile, httpx, io
import psycopg
from os import getenv

with open("/app/config/urls.txt") as f:
	urls = [line.strip() for line in f if line.strip()]

client = httpx.Client(
	headers={
		"User-Agent": "CyberAccounting samartha@vt.edu"
	}
)

pgclient = psycopg.connect(
	f"postgresql://postgres:{getenv('POSTGRES_PASSWORD')}@db:80/postgres"
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

			sub['cik'] = sub['cik'].str.zfill(10)

			num = num[
				num['adsh'].isin(sub['adsh'])
			][
				num['version'].str.contains('us-gaap', case=False, na=False)
			][
				num['tag'].isin(
					[
						'Revenues',
					    'CostsAndExpenses',
					    'EarningsPerShareBasic',
						'IncomeTaxExpenseBenefit'
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
					"IncomeTaxExpenseBenefit": "taxes"
				}
			).dropna(
				subset=["costs", "revenues", "eps"],
			)
			batch = list(res.itertuples(index=False, name=None))
			with pgclient.cursor() as cur:
				cur.executemany(
					"""
					INSERT INTO financials (accn, cik, name, fy, fp, costs, eps, revenues, taxes)
					VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
					ON CONFLICT (accn) DO UPDATE SET
						revenues = EXCLUDED.revenues,
						costs = EXCLUDED.costs,
						eps = EXCLUDED.eps,
						taxes = EXCLUDED.taxes;
					""",
					batch
				)
				pgclient.commit()