import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_company_info(ticker_symbol: str) -> dict:
    """Fetch base company information from yfinance."""
    tk = yf.Ticker(ticker_symbol)
    info = tk.info
    
    return {
        "ticker": ticker_symbol,
        "name": info.get("longName", info.get("shortName", ticker_symbol)),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "country": info.get("country"),
        "currency": info.get("financialCurrency", info.get("currency")),
        "exchange": info.get("exchange"),
        "description": info.get("longBusinessSummary"),
        "is_active": True
    }

def fetch_historical_prices(ticker_symbol: str, company_id: int, period: str = "max") -> list[dict]:
    """Fetch historical OHLCV prices and map to DB format."""
    tk = yf.Ticker(ticker_symbol)
    hist = tk.history(period=period)
    
    prices = []
    for date, row in hist.iterrows():
        prices.append({
            "company_id": company_id,
            "date": date.date(),
            "open_price": float(row["Open"]),
            "high_price": float(row["High"]),
            "low_price": float(row["Low"]),
            "close_price": float(row["Close"]),
            "adjusted_close": float(row["Close"]),  # yfinance history is optionally adj. by default
            "volume": float(row["Volume"])
        })
    return prices

def _safe_get(df, index, col, default=None):
    if index in df.index and col in df.columns:
        val = df.loc[index, col]
        return float(val) if pd.notna(val) else default
    return default

def fetch_annual_financials(ticker_symbol: str, company_id: int) -> list[dict]:
    """Fetch annual income, balance, and cashflow, and merge into unified format."""
    tk = yf.Ticker(ticker_symbol)
    
    inc = tk.financials
    bs = tk.balance_sheet
    cf = tk.cashflow
    
    # All dates available across all sheets
    all_dates = set()
    for df in [inc, bs, cf]:
        if df is not None and not df.empty:
            all_dates.update(df.columns)
            
    sorted_dates = sorted(list(all_dates), reverse=True)
    
    financials_list = []
    
    for dt in sorted_dates:
        # P&L
        revenue = _safe_get(inc, "Total Revenue", dt)
        gross_profit = _safe_get(inc, "Gross Profit", dt)
        ebitda = _safe_get(inc, "EBITDA", dt, _safe_get(inc, "Normalized EBITDA", dt))
        net_income = _safe_get(inc, "Net Income", dt)
        
        # Balance Sheet
        assets = _safe_get(bs, "Total Assets", dt)
        debt = _safe_get(bs, "Total Debt", dt)
        cash = _safe_get(bs, "Cash And Cash Equivalents", dt, _safe_get(bs, "Cash", dt))
        equity = _safe_get(bs, "Stockholders Equity", dt, _safe_get(bs, "Total Equity Gross Minority Interest", dt))
        
        # Cash Flow
        ocf = _safe_get(cf, "Operating Cash Flow", dt)
        fcf = _safe_get(cf, "Free Cash Flow", dt)
        
        financials_list.append({
            "company_id": company_id,
            "period_end_date": dt.date() if hasattr(dt, 'date') else pd.to_datetime(dt).date(),
            "period_type": "A",
            "revenue": revenue,
            "gross_profit": gross_profit,
            "ebitda": ebitda,
            "net_income": net_income,
            "total_assets": assets,
            "total_debt": debt,
            "cash_and_equivalents": cash,
            "total_equity": equity,
            "operating_cash_flow": ocf,
            "free_cash_flow": fcf
        })
        
    return financials_list
