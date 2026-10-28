import pytest
from app.models.schema import InvoiceDocument, VendorInfo, LineItem
from app.services.validator import validate_invoice_document

def test_validator_valid_document():
    doc = InvoiceDocument(
        invoice_number="INV-2026-001",
        issue_date="2026-02-01",
        due_date="2026-03-03",
        vendor=VendorInfo(name="Valid Vendor", tax_id="TAX-12345"),
        currency="USD",
        line_items=[
            LineItem(description="Item A", quantity=2, unit_price=100.0, amount=200.0),
            LineItem(description="Item B", quantity=1, unit_price=50.0, amount=50.0)
        ],
        subtotal=250.0,
        tax_amount=25.0,
        total_amount=275.0
    )
    violations = validate_invoice_document(doc)
    assert len(violations) == 0

def test_validator_math_error_subtotal_tax():
    # Subtotal 250 + Tax 25 = 275, but total is given as 300!
    doc = InvoiceDocument(
        invoice_number="INV-2026-001",
        issue_date="2026-02-01",
        vendor=VendorInfo(name="Valid Vendor", tax_id="TAX-12345"),
        currency="USD",
        line_items=[
            LineItem(description="Item A", quantity=1, unit_price=250.0, amount=250.0)
        ],
        subtotal=250.0,
        tax_amount=25.0,
        total_amount=300.0
    )
    violations = validate_invoice_document(doc)
    math_errors = [v for v in violations if v.code == "MATH_ERROR"]
    assert len(math_errors) >= 1
    assert any(v.field == "total_amount" for v in math_errors)

def test_validator_math_error_line_item():
    # Quantity 3 * 50 should be 150, but given 200
    doc = InvoiceDocument(
        invoice_number="INV-2026-001",
        issue_date="2026-02-01",
        vendor=VendorInfo(name="Valid Vendor", tax_id="TAX-12345"),
        currency="USD",
        line_items=[
            LineItem(description="Item Error", quantity=3, unit_price=50.0, amount=200.0)
        ],
        subtotal=200.0,
        tax_amount=0.0,
        total_amount=200.0
    )
    violations = validate_invoice_document(doc)
    math_errors = [v for v in violations if v.code == "MATH_ERROR"]
    assert len(math_errors) >= 1
    assert any(v.field == "line_items" for v in math_errors)

def test_validator_missing_required_fields():
    doc = InvoiceDocument(
        invoice_number="",
        issue_date="",
        vendor=VendorInfo(name="", tax_id=""),
        currency="USD",
        line_items=[],
        subtotal=0.0,
        tax_amount=0.0,
        total_amount=0.0
    )
    violations = validate_invoice_document(doc)
    codes = [v.code for v in violations]
    assert "MISSING_INVOICE_NUMBER" in codes
    assert "MISSING_ISSUE_DATE" in codes
    assert "MISSING_VENDOR_NAME" in codes
    assert "MISSING_TAX_ID" in codes
    assert "EMPTY_LINE_ITEMS" in codes
