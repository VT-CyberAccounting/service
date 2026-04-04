from typing import Dict
import pandas as pd
import psycopg
from os import getenv

data = pd.read_csv("/app/config/sln.csv", skipinitialspace=True)
data.columns = data.columns.str.strip()
pgclient = psycopg.connect(
	f"postgresql://postgres:{getenv('POSTGRES_PASSWORD')}@db:80/postgres"
)

mapping: Dict[str, str] = {
	"Ticker": "ticker",
	"YEAR": "year",
	"Environmental": "environmental",
	"Social": "social",
	"Governance": "governance",
	"ESG_score": "esg",
	"GVKEY": "gvkey",
	"CIK Number": "cik",
	"Company Name": "name",
	"SIC code": "sic",
	"Current Assets": "current_assets",
	"Assets": "assets",
	"Cash": "cash",
	"Inventory": "inventory",
	"Current Marketable Securities": "current_marketable_securities",
	"Current Liabilities": "current_liabilities",
	"Liabilities": "liabilities",
	"Property, Plant and Equipment": "property_plant_equipment",
	"Preferred/Preference Stock": "pref_stock",
	"Allowance for Doubtful Receivables": "allowance_doubtful_receivables",
	"Total Receivables": "total_receivables",
	"Stockholders Equity": "stockholders_equity",
	"Cost of Goods Sold": "cost_goods_sold",
	"Dividends - Preferred/Preference": "dividends_pref",
	"Dividends": "dividends",
	"Earnings Before Interest and Taxes": "earnings_before_interest_taxes",
	"Earnings Per Share (Basic)": "earnings_per_share_basic",
	"Net Income (Loss)": "net_income_loss",
	"Net Income Adjusted for common stocks": "net_income_adjusted_common_stocks",
	"Sales/Turnover (Net)": "sales_by_turnover",
	"Interest and Related Expense": "interest_related_expense",
	"Common Shares Outstanding": "common_shares_outstanding",
	"Total Debt Including Current": "total_debt_including_current",
	"Price Close - Annual -": "price_closed_annual",
	"Net receivables": "net_receivables",
	"Total assets last year": "total_assets_last_year",
	"Net receivables last year": "net_receivables_last_year",
	"Inventory last year": "inventory_last_year",
	"Stockholder equity last year": "stockholders_equity_last_year",
	"Cost of Goods Sold last year": "cost_goods_sold_last_year",
	"Common shares outstanding last year": "common_shares_outstanding_last_year",
}

data = data[list(mapping.keys())]
data = data.rename(columns=mapping)
data = data.dropna(how='all')
data = data.replace(".", None)

records = [tuple(None if pd.isna(v) else v for v in row) for row in data.values]

cols = ", ".join(list(mapping.values()))
placeholders = ", ".join(["%s"] * len(mapping))
insert_query = f"INSERT INTO raw ({cols}) VALUES ({placeholders})"

try:
	with pgclient.cursor() as cur:
		cur.executemany(insert_query, records)
	pgclient.commit()
	print(f"Successfully inserted {len(records)} records into the 'raw' table")
except Exception as e:
	pgclient.rollback()
	print(f"Error during batch insert: {e}")
	raise
finally:
	pgclient.close()
