CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE TABLE IF NOT EXISTS raw (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    environmental NUMERIC NOT NULL,
    social NUMERIC NOT NULL,
    governance NUMERIC NOT NULL,
    esg NUMERIC NOT NULL,
    gvkey NUMERIC NOT NULL,
    cik VARCHAR(10) NOT NULL,
    name VARCHAR(255) NOT NULL,
    sic NUMERIC NOT NULL,
    current_assets NUMERIC NOT NULL,
    assets NUMERIC NOT NULL,
    cash NUMERIC NOT NULL,
    inventory NUMERIC NOT NULL,
    current_marketable_securities NUMERIC NOT NULL,
    current_liabilities NUMERIC NOT NULL,
    liabilities NUMERIC NOT NULL,
    property_plant_equipment NUMERIC NOT NULL,
    pref_stock NUMERIC NOT NULL,
    allowance_doubtful_receivables NUMERIC NOT NULL,
    total_receivables NUMERIC NOT NULL,
    stockholders_equity NUMERIC NOT NULL,
    cost_goods_sold NUMERIC NOT NULL,
    dividends_pref NUMERIC NOT NULL,
    dividends NUMERIC NOT NULL,
    earnings_before_interest_taxes NUMERIC NOT NULL,
    earnings_per_share_basic NUMERIC NOT NULL,
    net_income_loss NUMERIC NOT NULL,
    net_income_adjusted_common_stocks NUMERIC NOT NULL,
    sales_by_turnover NUMERIC NOT NULL,
    interest_related_expense NUMERIC NOT NULL,
    common_shares_outstanding NUMERIC NOT NULL,
    total_debt_including_current NUMERIC NOT NULL,
    price_closed_annual NUMERIC NOT NULL,
    net_receivables NUMERIC NOT NULL,
    total_assets_last_year NUMERIC NOT NULL,
    net_receivables_last_year NUMERIC NOT NULL,
    inventory_last_year NUMERIC NOT NULL,
    stockholders_equity_last_year NUMERIC NOT NULL,
    cost_goods_sold_last_year NUMERIC NOT NULL,
    common_shares_outstanding_last_year NUMERIC NOT NULL,
);

CREATE TYPE industry_type AS ENUM ('Mining', 'Construction', 'Manufacturing', 'Transportation Public Utilities', 'Wholesale Trade', 'Retail Trade', 'Services');

CREATE VIEW IF NOT EXISTS sln AS (
    SELECT
        id,
        (current_assets - current_liabilities) AS working_capital,
        (current_assets / NULLIF(current_liabilities, 0)) AS current_ratio,
        ((cash + current_marketable_securities + (total_receivables - allowance_doubtful_receivables)) / NULLIF(current_liabilities, 0)) AS quick_ratio,
        (sales_by_turnover / NULLIF((net_receivables + net_receivables_last_year) / 2.0, 0)) AS accounts_receivable_turnover,
        (365.0 / NULLIF(sales_by_turnover / NULLIF((net_receivables + net_receivables_last_year) / 2.0, 0), 0)) AS average_days_to_collect_receivables,
        (cost_goods_sold / NULLIF((inventory + inventory_last_year) / 2.0, 0)) AS inventory_turnover,
        (365.0 / NULLIF(cost_goods_sold / NULLIF((inventory + inventory_last_year) / 2.0, 0), 0)) AS average_days_to_collect_inventory,
        (liabilities / NULLIF(assets, 0)) AS debt_to_assets,
        (liabilities / NULLIF(stockholders_equity, 0)) AS debt_to_equity,
        (earnings_before_interest_taxes / NULLIF(interest_related_expense, 0)) AS number_of_times_interest_is_earned,
        (net_income_loss / NULLIF(sales_by_turnover, 0)) AS net_margin,
        (sales_by_turnover / NULLIF((assets + total_assets_last_year) / 2.0, 0)) AS asset_turnover_ratio,
        (net_income_loss / NULLIF((assets + total_assets_last_year) / 2.0, 0)) AS return_on_investment,
        (net_income_loss / NULLIF((stockholders_equity + stockholders_equity_last_year) / 2.0, 0)) AS return_on_equity,
        (net_income_loss / NULLIF(common_shares_outstanding, 0)) AS earnings_per_share,
        ((stockholders_equity - pref_stock) / NULLIF(common_shares_outstanding, 0)) AS book_value_per_share,
        (price_closed_annual / NULLIF((net_income_loss / NULLIF(common_shares_outstanding, 0)), 0)) AS price_earnings_ratio,
        (dividends / NULLIF(price_closed_annual, 0)) AS dividend_yield,
        CASE
            WHEN sic BETWEEN 1000 AND 1499 THEN 'Mining'
            WHEN sic BETWEEN 1500 AND 1799 THEN 'Construction'
            WHEN sic BETWEEN 2000 AND 3999 THEN 'Manufacturing'
            WHEN sic BETWEEN 4000 AND 4999 THEN 'Transportation Public Utilities'
            WHEN sic BETWEEN 5000 AND 5199 THEN 'Wholesale Trade'
            WHEN sic BETWEEN 5200 AND 5999 THEN 'Retail Trade'
            WHEN sic BETWEEN 7000 AND 8999 THEN 'Services'
            ELSE NULL
        END::industry_type AS industry
    FROM raw
);