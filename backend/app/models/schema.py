from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class VendorInfo(BaseModel):
    name: str = Field(..., description="Tên nhà cung cấp")
    tax_id: str = Field(..., description="Mã số thuế")
    address: Optional[str] = Field(None, description="Địa chỉ nhà cung cấp")

class LineItem(BaseModel):
    description: str = Field(..., description="Mô tả hàng hóa / dịch vụ")
    quantity: float = Field(..., description="Số lượng")
    unit_price: float = Field(..., description="Đơn giá")
    amount: float = Field(..., description="Thành tiền = quantity * unit_price")

class InvoiceDocument(BaseModel):
    invoice_number: str = Field(..., description="Số hóa đơn (VD: INV-2026-001)")
    issue_date: str = Field(..., description="Ngày phát hành (YYYY-MM-DD)")
    due_date: Optional[str] = Field(None, description="Hạn thanh toán (YYYY-MM-DD)")
    vendor: VendorInfo
    po_number: Optional[str] = Field(None, description="Mã đơn mua hàng / PO liên kết")
    currency: str = Field(default="USD", description="Đơn vị tiền tệ (USD, VND, EUR)")
    line_items: List[LineItem] = Field(default_factory=list, description="Danh sách các mục hàng")
    subtotal: float = Field(..., description="Tổng tiền trước thuế")
    tax_amount: float = Field(..., description="Tiền thuế")
    total_amount: float = Field(..., description="Tổng thanh toán (subtotal + tax_amount)")
    confidence: Dict[str, float] = Field(default_factory=dict, alias="_confidence", description="Độ tin cậy trích xuất cho từng trường (0.0 đến 1.0)")

    model_config = {
        "populate_by_name": True
    }

class Violation(BaseModel):
    code: str = Field(..., description="Mã lỗi (VD: VENDOR_UNKNOWN, MATH_ERROR...)")
    severity: str = Field(..., description="Mức độ nghiêm trọng: blocker hoặc warning")
    field: Optional[str] = Field(None, description="Trường dữ liệu gây lỗi")
    message: str = Field(..., description="Thông báo mô tả chi tiết lỗi")
    expected: Optional[Any] = Field(None, description="Giá trị kỳ vọng")
    actual: Optional[Any] = Field(None, description="Giá trị thực tế nhận được")

class Decision(BaseModel):
    outcome: str = Field(..., description="Quyết định cuối cùng: APPROVE, REVIEW, hoặc REJECT")
    violations: List[Violation] = Field(default_factory=list, description="Danh sách các sai lệch phát hiện")
    processed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Thời điểm xử lý ISO")
    invoice_summary: Optional[Dict[str, Any]] = Field(None, description="Tóm tắt thông tin hóa đơn")
    file_name: Optional[str] = Field(None, description="Tên file hóa đơn")

class ReviewResponse(BaseModel):
    success: bool
    invoice: InvoiceDocument
    decision: Decision
