import sys
import os
import pandas as pd
from sqlalchemy import create_engine

# Ensure src is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database import DATABASE_URL

engine = create_engine(DATABASE_URL)

def print_separator(title):
    print("\n" + "="*80)
    print(f" {title} ".center(80, "="))
    print("="*80 + "\n")

if __name__ == "__main__":
    print_separator("1. EMPRESAS EXTRAÍDAS (COMPANIES)")
    df_companies = pd.read_sql("SELECT id, ticker, name, country, currency, sector FROM companies;", engine)
    print(df_companies.to_markdown(index=False))

    print_separator("2. DATOS FINANCIEROS (ÚLTIMOS REPORTES DE LVMH Y NVIDIA)")
    query_financials = """
        SELECT c.ticker, f.period_end_date, f.revenue, f.ebitda, f.net_income, f.total_debt 
        FROM financials f
        JOIN companies c ON f.company_id = c.id
        ORDER BY f.period_end_date DESC
        LIMIT 6;
    """
    df_financials = pd.read_sql(query_financials, engine)
    # Formatear números grandes para que sean legibles (ej. Billones o Millones)
    for col in ['revenue', 'ebitda', 'net_income', 'total_debt']:
        df_financials[col] = df_financials[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "NaN")
    print(df_financials.to_markdown(index=False))

    print_separator("3. RESUMEN DE PRECIOS HISTÓRICOS")
    query_prices = """
        SELECT c.ticker, MIN(p.date) as first_date, MAX(p.date) as last_date, COUNT(*) as total_days_recorded
        FROM price_history p
        JOIN companies c ON p.company_id = c.id
        GROUP BY c.ticker;
    """
    df_prices = pd.read_sql(query_prices, engine)
    print(df_prices.to_markdown(index=False))
