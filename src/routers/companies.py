from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Company, Financials, PriceHistory
from src.analysis.ratios import enrich_financial_record

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("/")
def get_all_companies(db: Session = Depends(get_db)):
    """Return a list of all requested tracked companies."""
    companies = db.query(Company).all()
    return companies

@router.get("/{ticker}")
def get_company_by_ticker(ticker: str, db: Session = Depends(get_db)):
    """Return core info of a single company."""
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.get("/{ticker}/financials")
def get_company_financials(ticker: str, db: Session = Depends(get_db)):
    """Return historical financials, automatically enriched with calculated ratios."""
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    financials = db.query(Financials).filter(Financials.company_id == company.id).order_by(Financials.period_end_date.desc()).all()
    
    # Enrich each record with the ratios engine on-the-fly
    enriched_results = []
    for f in financials:
        raw_dict = {column.name: getattr(f, column.name) for column in f.__table__.columns}
        enriched_results.append(enrich_financial_record(raw_dict))
        
    return enriched_results
