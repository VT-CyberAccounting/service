import sqlite3
# Note to dev: this is a synchronous class and must be updated to async when possible
class Stuff:
	def __init__(self):
		self.conn = sqlite3.connect(":memory:")
		self.cursor = self.conn.cursor()
		self.cursor.execute(
			"""
				CREATE TABLE tickers (
			    cik INTEGER PRIMARY KEY,
			    ticker VARCHAR(5),
			    title VARCHAR(25)
				)
            """
		)
		with open("lib/refs/company_tickers.json") as file:
			import json
			data = json.load(file)
			for key in data.keys():
				self.cursor.execute(
					"""
					INSERT INTO tickers VALUES (?, ?, ?)
					""",
					(data[key]['cik_str'], data[key]['ticker'], data[key]['title'])
				)
			self.conn.commit()

	def title(self, title: str) -> str:
		return self.cursor.execute("SELECT cik FROM tickers WHERE title = ?", (title,)).fetchone()[0]

	def ticker(self, ticker: str) -> str:
		return self.cursor.execute("SELECT cik FROM tickers WHERE ticker = ?", (ticker,)).fetchone()[0]

	def close(self):
		self.cursor.close()
		self.conn.close()