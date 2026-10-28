from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.schema import InvoiceDocument, Violation
from app.models.database import VendorModel, PurchaseOrderModel, ProcessedInvoiceModel

def check_vendor_unknown(doc: InvoiceDocument, db: Session) -> Optional[Violation]:
    """Rule 1: VENDOR_UNKNOWN (blocker) - Nhà cung cấp không có trong master data"""
    tax_id = doc.vendor.tax_id.strip() if doc.vendor and doc.vendor.tax_id else ""
    name = doc.vendor.name.strip().lower() if doc.vendor and doc.vendor.name else ""

    vendor = None
    if tax_id:
        vendor = db.query(VendorModel).filter(VendorModel.tax_id.ilike(tax_id)).first()
    if not vendor and name:
        vendor = db.query(VendorModel).filter(VendorModel.name.ilike(f"%{name}%")).first()

    if not vendor:
        return Violation(
            code="VENDOR_UNKNOWN",
            severity="blocker",
            field="vendor",
            message=f"Nhà cung cấp '{doc.vendor.name}' (MST: {doc.vendor.tax_id}) không tồn tại trong Master Data hệ thống",
            expected="Nhà cung cấp đã được đăng ký và phê duyệt trước trong hệ thống",
            actual=f"{doc.vendor.name} ({doc.vendor.tax_id})"
        )
    return None

def check_vendor_blocked(doc: InvoiceDocument, db: Session) -> Optional[Violation]:
    """Rule 2: VENDOR_BLOCKED (blocker) - Nhà cung cấp đang bị khóa giao dịch"""
    tax_id = doc.vendor.tax_id.strip() if doc.vendor and doc.vendor.tax_id else ""
    vendor = db.query(VendorModel).filter(VendorModel.tax_id.ilike(tax_id)).first()
    if not vendor and doc.vendor and doc.vendor.name:
        vendor = db.query(VendorModel).filter(VendorModel.name.ilike(f"%{doc.vendor.name.strip().lower()}%")).first()

    if vendor and vendor.status == "blocked":
        return Violation(
            code="VENDOR_BLOCKED",
            severity="blocker",
            field="vendor.status",
            message=f"Nhà cung cấp '{vendor.name}' (ID: {vendor.id}) hiện đang trong danh sách BỊ KHÓA / ĐÌNH CHỈ giao dịch",
            expected="active",
            actual="blocked"
        )
    return None

def check_tax_id_mismatch(doc: InvoiceDocument, db: Session) -> Optional[Violation]:
    """Rule 3: TAX_ID_MISMATCH (blocker) - Mã số thuế không khớp với tên nhà cung cấp trong master data"""
    if not doc.vendor or not doc.vendor.name:
        return None

    # Tìm vendor theo tên trước
    vendor_by_name = db.query(VendorModel).filter(VendorModel.name.ilike(f"%{doc.vendor.name.strip()}%")).first()
    if vendor_by_name:
        doc_tax = doc.vendor.tax_id.strip().upper()
        master_tax = vendor_by_name.tax_id.strip().upper()
        if doc_tax != master_tax:
            return Violation(
                code="TAX_ID_MISMATCH",
                severity="blocker",
                field="vendor.tax_id",
                message=f"Mã số thuế trên hóa đơn ({doc.vendor.tax_id}) không khớp với hồ sơ đăng ký của {vendor_by_name.name} ({vendor_by_name.tax_id})",
                expected=vendor_by_name.tax_id,
                actual=doc.vendor.tax_id
            )
    return None

def check_po_not_found(doc: InvoiceDocument, db: Session) -> Optional[Violation]:
    """Rule 4: PO_NOT_FOUND (blocker) - Mã PO không tồn tại trong hệ thống (khi có ghi PO)"""
    if not doc.po_number or not doc.po_number.strip():
        return None  # Không có PO thì bỏ qua rule này

    po = db.query(PurchaseOrderModel).filter(PurchaseOrderModel.po_number.ilike(doc.po_number.strip())).first()
    if not po:
        return Violation(
            code="PO_NOT_FOUND",
            severity="blocker",
            field="po_number",
            message=f"Đơn đặt hàng (PO) '{doc.po_number}' không tồn tại trong hệ thống quản lý mua hàng",
            expected="Mã PO hợp lệ đã được phê duyệt",
            actual=doc.po_number
        )
    return None

def check_po_vendor_mismatch(doc: InvoiceDocument, db: Session) -> Optional[Violation]:
    """Rule 5: PO_VENDOR_MISMATCH (blocker) - PO thuộc nhà cung cấp khác"""
    if not doc.po_number or not doc.po_number.strip():
        return None

    po = db.query(PurchaseOrderModel).filter(PurchaseOrderModel.po_number.ilike(doc.po_number.strip())).first()
    if not po:
        return None  # Đã bắt ở PO_NOT_FOUND

    # Tìm vendor của hóa đơn
    tax_id = doc.vendor.tax_id.strip() if doc.vendor and doc.vendor.tax_id else ""
    vendor = db.query(VendorModel).filter(VendorModel.tax_id.ilike(tax_id)).first()

    if vendor and po.vendor_id != vendor.id:
        expected_vendor = db.query(VendorModel).filter(VendorModel.id == po.vendor_id).first()
        expected_name = expected_vendor.name if expected_vendor else po.vendor_id
        return Violation(
            code="PO_VENDOR_MISMATCH",
            severity="blocker",
            field="po_number",
            message=f"Đơn đặt hàng {po.po_number} được tạo cho nhà cung cấp '{expected_name}' ({po.vendor_id}), không phải '{vendor.name}' ({vendor.id})",
            expected=f"Vendor {po.vendor_id} ({expected_name})",
            actual=f"Vendor {vendor.id} ({vendor.name})"
        )
    return None

def check_amount_exceeds_po(doc: InvoiceDocument, db: Session) -> Optional[Violation]:
    """Rule 6: AMOUNT_EXCEEDS_PO (blocker) - Tổng tiền vượt giá trị PO quá dung sai 2%"""
    if not doc.po_number or not doc.po_number.strip():
        return None

    po = db.query(PurchaseOrderModel).filter(PurchaseOrderModel.po_number.ilike(doc.po_number.strip())).first()
    if not po:
        return None

    tolerance_threshold = round(po.total_amount * 1.02, 2)
    if doc.total_amount > tolerance_threshold:
        diff_pct = round(((doc.total_amount - po.total_amount) / po.total_amount) * 100, 2)
        return Violation(
            code="AMOUNT_EXCEEDS_PO",
            severity="blocker",
            field="total_amount",
            message=f"Tổng tiền hóa đơn ({doc.total_amount:,.2f}) vượt giá trị PO ({po.total_amount:,.2f}) quá ngưỡng dung sai 2% (vượt +{diff_pct}%)",
            expected=f"<= {tolerance_threshold:,.2f} (PO: {po.total_amount:,.2f} + 2% tolerance)",
            actual=f"{doc.total_amount:,.2f}"
        )
    return None

def check_duplicate_invoice(doc: InvoiceDocument, db: Session) -> Optional[Violation]:
    """Rule 7: DUPLICATE_INVOICE (blocker) - Đã tồn tại hóa đơn cùng vendor + số hóa đơn"""
    tax_id = doc.vendor.tax_id.strip() if doc.vendor and doc.vendor.tax_id else ""
    inv_num = doc.invoice_number.strip() if doc.invoice_number else ""

    if not tax_id or not inv_num:
        return None

    existing = db.query(ProcessedInvoiceModel).filter(
        ProcessedInvoiceModel.invoice_number.ilike(inv_num),
        ProcessedInvoiceModel.vendor_tax_id.ilike(tax_id)
    ).first()

    if existing:
        return Violation(
            code="DUPLICATE_INVOICE",
            severity="blocker",
            field="invoice_number",
            message=f"Hóa đơn số '{inv_num}' từ nhà cung cấp MST '{tax_id}' đã từng được xử lý trong hệ thống ngày {existing.processed_at.strftime('%Y-%m-%d')}",
            expected="Số hóa đơn mới chưa từng thanh toán",
            actual=f"Trùng hóa đơn ID #{existing.id} đã xử lý"
        )
    return None

def check_low_confidence(doc: InvoiceDocument) -> Optional[Violation]:
    """Rule 8: LOW_CONFIDENCE (warning) - Có field bắt buộc confidence < 0.7"""
    conf = getattr(doc, "confidence", None) or getattr(doc, "_confidence", {}) or {}
    key_fields = ["invoice_number", "total_amount", "issue_date", "vendor_tax_id", "subtotal"]
    low_fields = []

    for field in key_fields:
        c = conf.get(field, 1.0)
        if c < 0.70:
            low_fields.append(f"{field} (confidence: {c:.2f})")

    if low_fields:
        return Violation(
            code="LOW_CONFIDENCE",
            severity="warning",
            field="_confidence",
            message=f"Độ tin cậy trích xuất một số trường chính dưới ngưỡng an toàn 70%: {', '.join(low_fields)}. Cần nhân sự kế toán đối chiếu mắt thường.",
            expected=">= 0.70 confidence cho mọi trường quan trọng",
            actual=low_fields
        )
    return None

def check_payment_terms_odd(doc: InvoiceDocument, db: Session) -> Optional[Violation]:
    """Rule 9: PAYMENT_TERMS_ODD (warning) - Hạn thanh toán lệch điều khoản chuẩn của vendor"""
    if not doc.issue_date or not doc.due_date:
        return None

    tax_id = doc.vendor.tax_id.strip() if doc.vendor and doc.vendor.tax_id else ""
    vendor = db.query(VendorModel).filter(VendorModel.tax_id.ilike(tax_id)).first()
    if not vendor:
        return None

    try:
        issue = datetime.strptime(doc.issue_date, "%Y-%m-%d")
        due = datetime.strptime(doc.due_date, "%Y-%m-%d")
        days = (due - issue).days
        expected_days = vendor.payment_terms_days

        # Nếu hạn thanh toán trước ngày phát hành hoặc lệch quá 10 ngày so với quy định chuẩn của vendor
        if days < 0:
            return Violation(
                code="PAYMENT_TERMS_ODD",
                severity="warning",
                field="due_date",
                message=f"Hạn thanh toán ({doc.due_date}) trước ngày phát hành hóa đơn ({doc.issue_date})",
                expected=f">= {doc.issue_date}",
                actual=doc.due_date
            )
        elif abs(days - expected_days) > 10:
            return Violation(
                code="PAYMENT_TERMS_ODD",
                severity="warning",
                field="due_date",
                message=f"Thời hạn thanh toán trên hóa đơn ({days} ngày) sai khác đáng kể so với hợp đồng chuẩn của vendor ({expected_days} ngày)",
                expected=f"Khoảng {expected_days} ngày (dao động ±10 ngày)",
                actual=f"{days} ngày (kỳ hạn {doc.issue_date} đến {doc.due_date})"
            )
    except ValueError:
        pass
    return None

def run_all_rules(doc: InvoiceDocument, db: Session) -> List[Violation]:
    """
    Chạy toàn bộ 10 rule kế toán đối chiếu với Master Data.
    Mỗi rule là một hàm độc lập trả Violation | None.
    """
    violations: List[Violation] = []

    # Danh sách các hàm rule
    rules = [
        check_vendor_unknown,
        check_vendor_blocked,
        check_tax_id_mismatch,
        check_po_not_found,
        check_po_vendor_mismatch,
        check_amount_exceeds_po,
        check_duplicate_invoice,
        lambda d, db_s: check_low_confidence(d),
        check_payment_terms_odd,
    ]

    for rule_fn in rules:
        try:
            violation = rule_fn(doc, db)
            if violation:
                violations.append(violation)
        except Exception as e:
            print(f"Lỗi khi thực thi rule {rule_fn.__name__}: {e}")

    return violations
