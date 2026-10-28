from typing import List
from app.models.schema import InvoiceDocument, Violation

def validate_invoice_document(doc: InvoiceDocument) -> List[Violation]:
    """
    Kiểm tra hình thức, trường bắt buộc và tính đúng đắn số học của hóa đơn.
    Trả về danh sách các Violation nếu có lỗi.
    """
    violations: List[Violation] = []

    # 1. Kiểm tra trường bắt buộc
    if not doc.invoice_number or not doc.invoice_number.strip():
        violations.append(Violation(
            code="MISSING_INVOICE_NUMBER",
            severity="blocker",
            field="invoice_number",
            message="Số hóa đơn không được để trống",
            expected="Chuỗi ký tự số hóa đơn hợp lệ",
            actual=doc.invoice_number
        ))

    if not doc.issue_date or not doc.issue_date.strip():
        violations.append(Violation(
            code="MISSING_ISSUE_DATE",
            severity="blocker",
            field="issue_date",
            message="Ngày phát hành không được để trống",
            expected="Định dạng YYYY-MM-DD",
            actual=doc.issue_date
        ))

    if not doc.vendor or not doc.vendor.name or not doc.vendor.name.strip():
        violations.append(Violation(
            code="MISSING_VENDOR_NAME",
            severity="blocker",
            field="vendor.name",
            message="Tên nhà cung cấp không được để trống",
            expected="Tên công ty / nhà cung cấp",
            actual=getattr(doc.vendor, "name", None)
        ))

    if not doc.vendor or not doc.vendor.tax_id or not doc.vendor.tax_id.strip():
        violations.append(Violation(
            code="MISSING_TAX_ID",
            severity="blocker",
            field="vendor.tax_id",
            message="Mã số thuế nhà cung cấp không được để trống",
            expected="Mã số thuế hợp lệ",
            actual=getattr(doc.vendor, "tax_id", None)
        ))

    # 2. Kiểm tra danh sách line items
    if not doc.line_items:
        violations.append(Violation(
            code="EMPTY_LINE_ITEMS",
            severity="blocker",
            field="line_items",
            message="Hóa đơn phải có ít nhất 1 dòng chi tiết hàng hóa / dịch vụ",
            expected=">= 1 line item",
            actual="0 line items"
        ))
    else:
        # Kiểm tra số học từng line item: quantity * unit_price = amount
        sum_line_items = 0.0
        line_item_math_errors = []
        for idx, item in enumerate(doc.line_items):
            calc_amount = round(item.quantity * item.unit_price, 2)
            actual_amount = round(item.amount, 2)
            if abs(calc_amount - actual_amount) > 0.05:
                line_item_math_errors.append(f"Dòng {idx + 1} ({item.description}): {item.quantity} * {item.unit_price} = {calc_amount} != {actual_amount}")
            sum_line_items += actual_amount

        if line_item_math_errors:
            violations.append(Violation(
                code="MATH_ERROR",
                severity="blocker",
                field="line_items",
                message=f"Sai lệch phép tính trên từng dòng sản phẩm: {'; '.join(line_item_math_errors)}",
                expected="quantity * unit_price == amount",
                actual=line_item_math_errors
            ))

        # Kiểm tra tổng các line item so với subtotal
        rounded_sum = round(sum_line_items, 2)
        rounded_subtotal = round(doc.subtotal, 2)
        if abs(rounded_sum - rounded_subtotal) > 0.10:
            violations.append(Violation(
                code="MATH_ERROR",
                severity="blocker",
                field="subtotal",
                message=f"Tổng thành tiền các line item ({rounded_sum}) không khớp với Subtotal ({rounded_subtotal})",
                expected=rounded_sum,
                actual=rounded_subtotal
            ))

    # 3. Kiểm tra subtotal + tax_amount == total_amount
    expected_total = round(doc.subtotal + doc.tax_amount, 2)
    actual_total = round(doc.total_amount, 2)
    if abs(expected_total - actual_total) > 0.10:
        violations.append(Violation(
            code="MATH_ERROR",
            severity="blocker",
            field="total_amount",
            message=f"Tổng tiền thanh toán ({actual_total}) không khớp với Subtotal + Tax ({expected_total})",
            expected=expected_total,
            actual=actual_total
        ))

    return violations
