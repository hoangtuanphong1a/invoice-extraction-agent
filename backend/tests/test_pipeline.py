import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Base
from app.services.seed_data import seed_database
from app.services.extractor import extract_from_pdf_stream
from app.services.validator import validate_invoice_document
from app.services.rule_engine import run_all_rules
from app.services.decision import evaluate_decision
from scripts.generate_sample_invoices import SAMPLE_INVOICES_SPEC

SAMPLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_data", "invoices"))

@pytest.fixture(scope="module")
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed
    from app.services.seed_data import VENDORS_SEED, POS_SEED
    from app.models.database import VendorModel, PurchaseOrderModel, ProcessedInvoiceModel

    for v in VENDORS_SEED:
        session.add(VendorModel(
            id=v["id"], name=v["name"], tax_id=v["tax_id"],
            status=v["status"], payment_terms_days=v["payment_terms_days"],
            credit_limit=v["credit_limit"]
        ))
    for p in POS_SEED:
        session.add(PurchaseOrderModel(
            po_number=p["po_number"], vendor_id=p["vendor_id"],
            total_amount=p["total_amount"], status=p["status"]
        ))
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

def run_file(filename: str, db):
    path = os.path.join(SAMPLES_DIR, filename)
    with open(path, "rb") as f:
        pdf_bytes = f.read()

    doc = extract_from_pdf_stream(pdf_bytes, filename=filename)
    val_violations = validate_invoice_document(doc)
    rule_violations = run_all_rules(doc, db)
    decision = evaluate_decision(doc, val_violations, rule_violations, file_name=filename)
    return doc, decision

def test_valid_invoices_all_approve(db_session):
    """Kiểm tra 10 hóa đơn chuẩn đều phải được duyệt APPROVE"""
    valid_files = [s["filename"] for s in SAMPLE_INVOICES_SPEC if "VALID" in s["filename"]]
    assert len(valid_files) == 10

    for fname in valid_files:
        doc, decision = run_file(fname, db_session)
        assert decision.outcome == "APPROVE", f"Hóa đơn {fname} bị từ chối với lỗi: {[v.code for v in decision.violations]}"
        assert len(decision.violations) == 0

def test_err_unknown_vendor(db_session):
    doc, decision = run_file("INV-ERR-011_UNKNOWN_VENDOR.pdf", db_session)
    assert decision.outcome == "REJECT"
    codes = [v.code for v in decision.violations]
    assert "VENDOR_UNKNOWN" in codes

def test_err_blocked_vendor(db_session):
    doc, decision = run_file("INV-ERR-012_BLOCKED_VENDOR.pdf", db_session)
    assert decision.outcome == "REJECT"
    codes = [v.code for v in decision.violations]
    assert "VENDOR_BLOCKED" in codes

def test_err_tax_mismatch(db_session):
    doc, decision = run_file("INV-ERR-013_TAX_MISMATCH.pdf", db_session)
    assert decision.outcome == "REJECT"
    codes = [v.code for v in decision.violations]
    assert "TAX_ID_MISMATCH" in codes

def test_err_po_not_found(db_session):
    doc, decision = run_file("INV-ERR-014_PO_NOT_FOUND.pdf", db_session)
    assert decision.outcome == "REJECT"
    codes = [v.code for v in decision.violations]
    assert "PO_NOT_FOUND" in codes

def test_err_po_vendor_mismatch(db_session):
    doc, decision = run_file("INV-ERR-015_PO_VENDOR_MISMATCH.pdf", db_session)
    assert decision.outcome == "REJECT"
    codes = [v.code for v in decision.violations]
    assert "PO_VENDOR_MISMATCH" in codes

def test_err_amount_exceeds_po(db_session):
    doc, decision = run_file("INV-ERR-016_AMOUNT_EXCEEDS_PO.pdf", db_session)
    assert decision.outcome == "REJECT"
    codes = [v.code for v in decision.violations]
    assert "AMOUNT_EXCEEDS_PO" in codes

def test_err_math_error(db_session):
    doc, decision = run_file("INV-ERR-017_MATH_ERROR.pdf", db_session)
    assert decision.outcome == "REJECT"
    codes = [v.code for v in decision.violations]
    assert "MATH_ERROR" in codes

def test_err_duplicate_invoice(db_session):
    doc, decision = run_file("INV-ERR-018_DUPLICATE_INVOICE.pdf", db_session)
    assert decision.outcome == "REJECT"
    codes = [v.code for v in decision.violations]
    assert "DUPLICATE_INVOICE" in codes

def test_warn_payment_terms_odd(db_session):
    doc, decision = run_file("INV-WARN-019_PAYMENT_TERMS_ODD.pdf", db_session)
    assert decision.outcome == "REVIEW"
    codes = [v.code for v in decision.violations]
    assert "PAYMENT_TERMS_ODD" in codes

def test_warn_low_confidence(db_session):
    doc, decision = run_file("INV-WARN-020_LOW_CONFIDENCE.pdf", db_session)
    assert decision.outcome == "REVIEW"
    codes = [v.code for v in decision.violations]
    assert "LOW_CONFIDENCE" in codes
