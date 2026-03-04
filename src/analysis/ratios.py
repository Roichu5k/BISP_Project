import math

def safe_divide(numerator: float, denominator: float) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    if math.isnan(numerator) or math.isnan(denominator):
        return None
    return numerator / denominator

def calculate_margins(revenue: float, gross_profit: float, ebitda: float, net_income: float) -> dict:
    """Calculates profitability margins."""
    return {
        "gross_margin": safe_divide(gross_profit, revenue),
        "ebitda_margin": safe_divide(ebitda, revenue),
        "net_margin": safe_divide(net_income, revenue)
    }

def calculate_return_metrics(net_income: float, total_equity: float, total_assets: float) -> dict:
    """Calculates basic return metrics (ROE, ROA).
       Note: A true ROIC requires NOPAT and Invested Capital, which requires deeper data parsing.
    """
    return {
        "roe": safe_divide(net_income, total_equity),
        "roa": safe_divide(net_income, total_assets)
    }

def calculate_leverage(total_debt: float, ebitda: float, total_equity: float, cash: float) -> dict:
    """Calculates basic debt and leverage metrics."""
    net_debt = None
    if total_debt is not None and cash is not None:
        net_debt = total_debt - cash
        
    return {
        "net_debt": net_debt,
        "debt_to_equity": safe_divide(total_debt, total_equity),
        "net_debt_to_ebitda": safe_divide(net_debt, ebitda) if net_debt is not None else None
    }

def enrich_financial_record(financial_record: dict) -> dict:
    """Takes a dictionary of raw financials and returns a dictionary with calculated fundamental ratios."""
    
    rev = financial_record.get("revenue")
    gp = financial_record.get("gross_profit")
    ebitda = financial_record.get("ebitda")
    ni = financial_record.get("net_income")
    
    eq = financial_record.get("total_equity")
    assets = financial_record.get("total_assets")
    debt = financial_record.get("total_debt")
    cash = financial_record.get("cash_and_equivalents")
    
    margins = calculate_margins(rev, gp, ebitda, ni)
    returns = calculate_return_metrics(ni, eq, assets)
    leverage = calculate_leverage(debt, ebitda, eq, cash)
    
    # Merge everything into a single report dictionary
    return {
        **financial_record,
        "ratios": {
            "profitability": margins,
            "returns": returns,
            "leverage": leverage
        }
    }
