from sqlalchemy.orm import Session
from . import models

def get_company_by_ticker(db: Session, ticker: str):
    return db.query(models.Company).filter(models.Company.ticker == ticker).first()

def create_or_update_company(db: Session, company_data: dict):
    db_company = get_company_by_ticker(db, ticker=company_data["ticker"])
    if db_company:
        for key, value in company_data.items():
            setattr(db_company, key, value)
    else:
        db_company = models.Company(**company_data)
        db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def add_financials(db: Session, financials_data: dict):
    # Basic upsert strategy for financials based on company_id and period_end_date and period_type
    existing = db.query(models.Financials).filter(
        models.Financials.company_id == financials_data["company_id"],
        models.Financials.period_end_date == financials_data["period_end_date"],
        models.Financials.period_type == financials_data["period_type"]
    ).first()
    
    if existing:
        for key, value in financials_data.items():
            setattr(existing, key, value)
        db_financials = existing
    else:
        db_financials = models.Financials(**financials_data)
        db.add(db_financials)
        
    db.commit()
    db.refresh(db_financials)
    return db_financials

def add_price_history_bulk(db: Session, prices_list: list[dict]):
    """Insert or ignore prices. For production, a true UPSERT or Timescale hypertable insert is needed."""
    # Simple strategy: try to insert those that don't exist
    for price_data in prices_list:
        existing = db.query(models.PriceHistory).filter(
            models.PriceHistory.company_id == price_data["company_id"],
            models.PriceHistory.date == price_data["date"]
        ).first()
        if not existing:
            db_price = models.PriceHistory(**price_data)
            db.add(db_price)
    
    db.commit()

