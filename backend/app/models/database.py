import os
import json
from sqlalchemy import create_engine, Column, String, Integer, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./invoice_agent.db")

engine = create_engine(DB_PATH, connect_args={"check_same_thread": False} if "sqlite" in DB_PATH else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class VendorModel(Base):
    __tablename__ = "vendors"

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    tax_id = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), default="active")  # active, blocked
    payment_terms_days = Column(Integer, default=30)
    credit_limit = Column(Float, default=100000.0)

class PurchaseOrderModel(Base):
    __tablename__ = "purchase_orders"

    po_number = Column(String(50), primary_key=True)
    vendor_id = Column(String(50), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(20), default="open")  # open, closed
    lines_json = Column(Text, default="[]")

class ProcessedInvoiceModel(Base):
    __tablename__ = "processed_invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(50), nullable=False)
    vendor_tax_id = Column(String(50), nullable=False)
    vendor_name = Column(String(200), nullable=False)
    po_number = Column(String(50), nullable=True)
    issue_date = Column(String(20), nullable=False)
    total_amount = Column(Float, nullable=False)
    outcome = Column(String(20), nullable=False)  # APPROVE, REVIEW, REJECT
    raw_document_json = Column(Text, nullable=False)
    violations_json = Column(Text, default="[]")
    processed_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
