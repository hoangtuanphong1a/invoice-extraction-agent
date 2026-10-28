from typing import List, Optional
from datetime import datetime
from app.models.schema import InvoiceDocument, Violation, Decision

def evaluate_decision(
    doc: InvoiceDocument,
    validation_violations: List[Violation],
    rule_violations: List[Violation],
    file_name: Optional[str] = None
) -> Decision:
    """
    Gộp toàn bộ sai lệch từ Validation và Rule Engine.
    Quy tắc quyết định chuẩn:
    - Có ít nhất 1 lỗi mức 'blocker' -> REJECT
    - Không có 'blocker', nhưng có ít nhất 1 lỗi mức 'warning' -> REVIEW
    - Không có bất kỳ lỗi nào -> APPROVE
    """
    all_violations: List[Violation] = []
    all_violations.extend(validation_violations)
    all_violations.extend(rule_violations)

    has_blocker = any(v.severity == "blocker" for v in all_violations)
    has_warning = any(v.severity == "warning" for v in all_violations)

    if has_blocker:
        outcome = "REJECT"
    elif has_warning:
        outcome = "REVIEW"
    else:
        outcome = "APPROVE"

    invoice_summary = {
        "invoice_number": doc.invoice_number,
        "vendor_name": doc.vendor.name if doc.vendor else "",
        "tax_id": doc.vendor.tax_id if doc.vendor else "",
        "po_number": doc.po_number,
        "total_amount": doc.total_amount,
        "currency": doc.currency,
        "issue_date": doc.issue_date,
        "due_date": doc.due_date,
        "items_count": len(doc.line_items)
    }

    return Decision(
        outcome=outcome,
        violations=all_violations,
        processed_at=datetime.utcnow().isoformat(),
        invoice_summary=invoice_summary,
        file_name=file_name
    )
