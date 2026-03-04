from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from .database import Base

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    country = Column(String(50))
    currency = Column(String(10))
    exchange = Column(String(50))
    is_active = Column(Boolean, default=True)
    description = Column(Text)
    
    financials = relationship("Financials", back_populates="company")
    prices = relationship("PriceHistory", back_populates="company")


class Financials(Base):
    __tablename__ = "financials"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    period_end_date = Column(Date, nullable=False)
    period_type = Column(String(10)) # 'A' for Annual, 'Q' for Quarter, 'H' for Half-year
    
    # Income Statement core metrics
    revenue = Column(Float)
    gross_profit = Column(Float)
    ebitda = Column(Float)
    net_income = Column(Float)
    
    # Balance Sheet core metrics
    total_assets = Column(Float)
    total_debt = Column(Float)
    cash_and_equivalents = Column(Float)
    total_equity = Column(Float)
    
    # Cash Flow core
    operating_cash_flow = Column(Float)
    free_cash_flow = Column(Float)
    
    company = relationship("Company", back_populates="financials")


class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    adjusted_close = Column(Float)
    volume = Column(Float)
    
    company = relationship("Company", back_populates="prices")
