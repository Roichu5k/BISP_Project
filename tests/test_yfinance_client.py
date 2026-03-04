import pytest
from src.ingestion.yfinance_client import fetch_company_info, fetch_annual_financials, fetch_historical_prices

def test_fetch_company_info():
    ticker = "ITX.MC" # Inditex - Spanish market
    info = fetch_company_info(ticker)
    assert info is not None
    assert info["ticker"] == ticker
    assert "Industria de Diseño Textil" in info["name"]
    assert info["country"] == "Spain"
    assert info["currency"] == "EUR"
    
def test_fetch_annual_financials():
    ticker = "ITX.MC"
    financials = fetch_annual_financials(ticker, company_id=1)
    assert isinstance(financials, list)
    assert len(financials) > 0
    # Check that basic structural keys are there
    for f in financials:
        assert f["company_id"] == 1
        assert "revenue" in f
        assert "period_end_date" in f

def test_fetch_historical_prices():
    ticker = "ITX.MC"
    prices = fetch_historical_prices(ticker, company_id=1, period="1mo")
    assert isinstance(prices, list)
    assert len(prices) > 0
    # Check first day
    p = prices[0]
    assert "close_price" in p
    assert p["volume"] >= 0
