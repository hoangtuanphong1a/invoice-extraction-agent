import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Base, VendorModel, PurchaseOrderModel, ProcessedInvoiceModel
from app.models.schema import InvoiceDocument, VendorInfo, LineItem
from app.services.rule_engine import (
    check_vendor_unknown,
    check_vendor_blocked,
    check_tax_id_mismatch,
    check_po_not_found,
    check_po_vendor_mismatch,
    check_amount_exceeds_po,
    check_duplicate_invoice,
    check_low_confidence,
    check_payment_terms_odd,
    run_all_rules
)
from app.services.seed_data import VENDORS_SEED, POS_SEED

@pytest.fixture(scope="module")
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed data
    for v in VENDORS_SEED:
        session.add(VendorModel(
            id=v["id"],
            name=v["name"],
            tax_id=v["tax_id"],
            status=v["status"],
            payment_terms_days=v["payment_terms_days"],
            credit_limit=v["credit_limit"]
        ))
    for p in POS_SEED:
        session.add(PurchaseOrderModel(
            po_number=p["po_number"],
            vendor_id=p["vendor_id"],
            total_amount=p["total_amount"],
            status=p["status"]
        ))
    # Seed duplicate test invoice
    session.add(ProcessedInvoiceModel(
        invoice_number="INV-EXISTING-001",
        vendor_tax_id="US-882910394",
        vendor_name="TechCore Solutions Inc",
        po_number="PO-2026-101",
        issue_date="2026-01-15",
        total_amount=13500.0,
        outcome="APPROVE",
        raw_document_json="{}",
        violations_json="[]"
    ))
    session.commit()
    yield session
    session.close()

def create_mock_invoice(
    invoice_number="INV-TEST-001",
    vendor_name="TechCore Solutions Inc",
    tax_id="US-882910394",
    po_number="PO-2026-101",
    total_amount=12500.0,
    subtotal=12500.0,
    tax=0.0,
    issue_date="2026-02-01",
    due_date="2026-03-03",
    confidence=None
):
    return InvoiceDocument(
        invoice_number=invoice_number,
        issue_date=issue_date,
        due_date=due_date,
        vendor=VendorInfo(name=vendor_name, tax_id=tax_id, address="123 Street"),
        po_number=po_number,
        currency="USD",
        line_items=[LineItem(description="Item", quantity=1, unit_price=subtotal, amount=subtotal)],
        subtotal=subtotal,
        tax_amount=tax,
        total_amount=total_amount,
        _confidence=confidence or {"invoice_number": 0.95, "total_amount": 0.95, "issue_date": 0.95, "vendor_tax_id": 0.95}
    )

def test_rule_vendor_unknown(test_db):
    doc = create_mock_invoice(vendor_name="Unknown Ghost Co", tax_id="US-999999999")
    v = check_vendor_unknown(doc, test_db)
    assert v is not None
    assert v.code == "VENDOR_UNKNOWN"
    assert v.severity == "blocker"

def test_rule_vendor_blocked(test_db):
    # V004: Nexus Office Furniture Co is blocked
    doc = create_mock_invoice(vendor_name="Nexus Office Furniture Co", tax_id="US-554433221")
    v = check_vendor_blocked(doc, test_db)
    assert v is not None
    assert v.code == "VENDOR_BLOCKED"
    assert v.severity == "blocker"

def test_rule_tax_id_mismatch(test_db):
    # TechCore Solutions Inc has tax_id US-882910394, here we pass fake tax_id
    doc = create_mock_invoice(vendor_name="TechCore Solutions Inc", tax_id="US-000000000")
    v = check_tax_id_mismatch(doc, test_db)
    assert v is not None
    assert v.code == "TAX_ID_MISMATCH"
    assert v.severity == "blocker"

def test_rule_po_not_found(test_db):
    doc = create_mock_invoice(po_number="PO-NON-EXISTENT")
    v = check_po_not_found(doc, test_db)
    assert v is not None
    assert v.code == "PO_NOT_FOUND"
    assert v.severity == "blocker"

def test_rule_po_vendor_mismatch(test_db):
    # PO-2026-101 belongs to TechCore Solutions Inc (V001). We pass Apex Logistics (V002)
    doc = create_mock_invoice(vendor_name="Apex Logistics & Supply", tax_id="US-119283745", po_number="PO-2026-101")
    v = check_po_vendor_mismatch(doc, test_db)
    assert v is not None
    assert v.code == "PO_VENDOR_MISMATCH"
    assert v.severity == "blocker"

def test_rule_amount_exceeds_po(test_db):
    # PO-2026-102 total is $4,500. 2% tolerance is $4,590. Here total is $5,000 (> 2%)
    doc = create_mock_invoice(po_number="PO-2026-102", total_amount=5000.0, subtotal=5000.0)
    v = check_amount_exceeds_po(doc, test_db)
    assert v is not None
    assert v.code == "AMOUNT_EXCEEDS_PO"
    assert v.severity == "blocker"

def test_rule_duplicate_invoice(test_db):
    # INV-EXISTING-001 already in DB for TechCore
    doc = create_mock_invoice(invoice_number="INV-EXISTING-001", vendor_name="TechCore Solutions Inc", tax_id="US-882910394")
    v = check_duplicate_invoice(doc, test_db)
    assert v is not None
    assert v.code == "DUPLICATE_INVOICE"
    assert v.severity == "blocker"

def test_rule_low_confidence():
    doc = create_mock_invoice(confidence={"invoice_number": 0.55, "total_amount": 0.95})
    v = check_low_confidence(doc)
    assert v is not None
    assert v.code == "LOW_CONFIDENCE"
    assert v.severity == "warning"

def test_rule_payment_terms_odd(test_db):
    # Apex Logistics (V002) standard is 15 days. Here issue is 2026-02-01, due is 2026-05-01 (90 days)
    doc = create_mock_invoice(
        vendor_name="Apex Logistics & Supply",
        tax_id="US-119283745",
        issue_date="2026-02-01",
        due_date="2026-05-01"
    )
    v = check_payment_terms_odd(doc, test_db)
    assert v is not None
    assert v.code == "PAYMENT_TERMS_ODD"
    assert v.severity == "warning"
