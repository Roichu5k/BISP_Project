from src.analysis.ratios import calculate_margins, calculate_return_metrics, enrich_financial_record

def test_calculate_margins():
    res = calculate_margins(revenue=1000, gross_profit=600, ebitda=300, net_income=100)
    assert res["gross_margin"] == 0.6
    assert res["ebitda_margin"] == 0.3
    assert res["net_margin"] == 0.1

def test_calculate_margins_zeros():
    res = calculate_margins(revenue=0, gross_profit=0, ebitda=0, net_income=0)
    assert res["gross_margin"] is None

def test_enrich_financial_record():
    raw_data = {
        "revenue": 1000,
        "gross_profit": 500,
        "ebitda": 200,
        "net_income": 50,
        "total_equity": 500,
        "total_assets": 2000,
        "total_debt": 1000,
        "cash_and_equivalents": 200
    }
    
    enriched = enrich_financial_record(raw_data)
    
    assert "ratios" in enriched
    assert enriched["ratios"]["profitability"]["gross_margin"] == 0.5
    assert enriched["ratios"]["returns"]["roe"] == 0.1
    assert enriched["ratios"]["leverage"]["net_debt"] == 800
    assert enriched["ratios"]["leverage"]["net_debt_to_ebitda"] == 4.0
