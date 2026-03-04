import sys
import os

# Ensure src is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database import SessionLocal, engine, Base
from src.crud import create_or_update_company, add_financials, add_price_history_bulk
from src.ingestion.yfinance_client import fetch_company_info, fetch_annual_financials, fetch_historical_prices
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_company(ticker: str):
    logger.info(f"Seeding metadata for {ticker}...")
    db = SessionLocal()
    try:
        # 1. Company Info
        info = fetch_company_info(ticker)
        company = create_or_update_company(db, info)
        logger.info(f"Company {company.name} (ID: {company.id}) inserted/updated.")
        
        # 2. Financials
        logger.info(f"Fetching financials for {ticker}...")
        financials_list = fetch_annual_financials(ticker, company.id)
        for f in financials_list:
            add_financials(db, f)
        logger.info(f"Inserted {len(financials_list)} annual financial records.")
        
        # 3. Prices
        logger.info(f"Fetching historical prices (10y) for {ticker}...")
        prices_list = fetch_historical_prices(ticker, company.id, period="10y")
        add_price_history_bulk(db, prices_list)
        logger.info(f"Inserted {len(prices_list)} trading days.")
        
    except Exception as e:
        logger.error(f"Error seeding {ticker}: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Asegurarse de que las tablas existen
    Base.metadata.create_all(bind=engine)
    
    # Lista inicial de empresas (Euro-Centric y un gigante de US)
    tickers_to_seed = ["ITX.MC", "MC.PA", "NVDA"]
    
    for t in tickers_to_seed:
        seed_company(t)
    
    logger.info("Database seeding process finished.")
