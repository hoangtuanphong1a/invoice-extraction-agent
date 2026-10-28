import os
import json
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.models.schema import InvoiceDocument, Decision, ReviewResponse, Violation
from app.models.database import get_db, VendorModel, PurchaseOrderModel, ProcessedInvoiceModel
from app.services.extractor import extract_from_pdf_stream
from app.services.validator import validate_invoice_document
from app.services.rule_engine import run_all_rules
from app.services.decision import evaluate_decision
from scripts.generate_sample_invoices import SAMPLE_INVOICES_SPEC

router = APIRouter()

SAMPLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_data", "invoices"))

@router.post("/extract", response_model=InvoiceDocument)
async def extract_invoice(file: UploadFile = File(...)):
    """
    Endpoint M1: Nhận file PDF / Ảnh hóa đơn -> Trả JSON có cấu trúc theo đúng schema InvoiceDocument
    kèm độ tin cậy (_confidence) cho từng trường.
    """
    if not file.filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file định dạng PDF hoặc Ảnh (PNG, JPG)")

    contents = await file.read()
    try:
        doc = extract_from_pdf_stream(contents, filename=file.filename)
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi trích xuất dữ liệu: {str(e)}")

@router.post("/review", response_model=ReviewResponse)
async def review_invoice(
    file: Optional[UploadFile] = File(None),
    invoice_json: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Endpoint M3: Nhận hóa đơn -> Ingest -> Extract -> Validate -> Rule Engine -> Decision
    Trả về quyết định phê duyệt (APPROVE | REVIEW | REJECT) kèm danh sách Violation và chi tiết trường lỗi.
    """
    doc: Optional[InvoiceDocument] = None
    file_name = "direct_input.json"

    if file:
        file_name = file.filename
        contents = await file.read()
        try:
            doc = extract_from_pdf_stream(contents, filename=file.filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi khi trích xuất tài liệu: {str(e)}")
    elif invoice_json:
        try:
            data = json.loads(invoice_json)
            doc = InvoiceDocument(**data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Dữ liệu JSON hóa đơn không hợp lệ: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp file PDF hóa đơn hoặc invoice_json")

    # 1. Validation kiểm tra hình thức và số học
    validation_violations = validate_invoice_document(doc)

    # 2. Rule Engine đối chiếu Master Data và Chính sách
    rule_violations = run_all_rules(doc, db)

    # 3. Decision Maker
    decision = evaluate_decision(doc, validation_violations, rule_violations, file_name=file_name)

    # 4. Ghi nhận vào ProcessedInvoices Audit Log
    try:
        processed_record = ProcessedInvoiceModel(
            invoice_number=doc.invoice_number,
            vendor_tax_id=doc.vendor.tax_id if doc.vendor else "",
            vendor_name=doc.vendor.name if doc.vendor else "",
            po_number=doc.po_number,
            issue_date=doc.issue_date,
            total_amount=doc.total_amount,
            outcome=decision.outcome,
            raw_document_json=doc.model_dump_json(),
            violations_json=json.dumps([v.model_dump() for v in decision.violations])
        )
        db.add(processed_record)
        db.commit()
    except Exception as e:
        print(f"Warning: Could not save processed invoice log: {e}")
        db.rollback()

    return ReviewResponse(
        success=True,
        invoice=doc,
        decision=decision
    )

@router.get("/samples")
def get_sample_invoices():
    """Danh sách 20 hóa đơn mẫu có sẵn để người dùng click kiểm tra nhanh trên UI"""
    results = []
    for spec in SAMPLE_INVOICES_SPEC:
        fname = spec["filename"]
        # Phân loại expected outcome
        if "VALID" in fname:
            expected = "APPROVE"
            tag_color = "emerald"
        elif "WARN" in fname:
            expected = "REVIEW"
            tag_color = "amber"
        else:
            expected = "REJECT"
            tag_color = "rose"

        results.append({
            "filename": fname,
            "invoice_number": spec["invoice_number"],
            "vendor_name": spec["vendor_name"],
            "tax_id": spec["tax_id"],
            "po_number": spec["po_number"],
            "total": spec["total"],
            "currency": spec["currency"],
            "notes": spec["notes"],
            "expected_outcome": expected,
            "tag_color": tag_color
        })
    return results

@router.get("/samples/{filename}/download")
def download_sample_pdf(filename: str):
    """Tải hoặc xem trực tiếp file PDF hóa đơn mẫu"""
    path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Không tìm thấy file mẫu")
    return FileResponse(path, media_type="application/pdf", filename=filename)

@router.post("/samples/{filename}/run", response_model=ReviewResponse)
async def run_sample_invoice(filename: str, db: Session = Depends(get_db)):
    """Chạy quy trình thẩm định trực tiếp trên một hóa đơn mẫu"""
    path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Không tìm thấy file mẫu")

    with open(path, "rb") as f:
        contents = f.read()

    doc = extract_from_pdf_stream(contents, filename=filename)
    validation_violations = validate_invoice_document(doc)
    rule_violations = run_all_rules(doc, db)
    decision = evaluate_decision(doc, validation_violations, rule_violations, file_name=filename)

    return ReviewResponse(
        success=True,
        invoice=doc,
        decision=decision
    )

@router.get("/vendors")
def list_vendors(db: Session = Depends(get_db)):
    """Xem danh sách Master Data nhà cung cấp"""
    vendors = db.query(VendorModel).all()
    return [
        {
            "id": v.id,
            "name": v.name,
            "tax_id": v.tax_id,
            "status": v.status,
            "payment_terms_days": v.payment_terms_days,
            "credit_limit": v.credit_limit
        }
        for v in vendors
    ]

@router.get("/pos")
def list_pos(db: Session = Depends(get_db)):
    """Xem danh sách Đơn đặt hàng (PO) trong hệ thống"""
    pos = db.query(PurchaseOrderModel).all()
    return [
        {
            "po_number": p.po_number,
            "vendor_id": p.vendor_id,
            "total_amount": p.total_amount,
            "status": p.status,
            "lines": json.loads(p.lines_json) if p.lines_json else []
        }
        for p in pos
    ]

@router.get("/history")
def list_history(db: Session = Depends(get_db)):
    """Xem lịch sử các hóa đơn đã được thẩm định"""
    records = db.query(ProcessedInvoiceModel).order_by(ProcessedInvoiceModel.id.desc()).limit(50).all()
    return [
        {
            "id": r.id,
            "invoice_number": r.invoice_number,
            "vendor_name": r.vendor_name,
            "tax_id": r.vendor_tax_id,
            "po_number": r.po_number,
            "total_amount": r.total_amount,
            "outcome": r.outcome,
            "violations": json.loads(r.violations_json) if r.violations_json else [],
            "processed_at": r.processed_at.isoformat() if r.processed_at else ""
        }
        for r in records
    ]
