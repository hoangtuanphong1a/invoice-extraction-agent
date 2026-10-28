import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Định nghĩa 20 hóa đơn mẫu chi tiết
SAMPLE_INVOICES_SPEC = [
    # 10 Hóa đơn HỢP LỆ (APPROVE)
    {
        "filename": "INV-2026-001_VALID.pdf",
        "invoice_number": "INV-2026-001",
        "vendor_name": "TechCore Solutions Inc",
        "tax_id": "US-882910394",
        "address": "100 Silicon Blvd, Suite 400, San Jose, CA",
        "issue_date": "2026-02-01",
        "due_date": "2026-03-03",
        "po_number": "PO-2026-101",
        "currency": "USD",
        "items": [
            ("Server Rack Mounting Unit", 5, 2500.0, 12500.0)
        ],
        "subtotal": 12500.0,
        "tax": 0.0,
        "total": 12500.0,
        "notes": "Standard approved delivery PO-2026-101."
    },
    {
        "filename": "INV-2026-002_VALID.pdf",
        "invoice_number": "INV-2026-002",
        "vendor_name": "TechCore Solutions Inc",
        "tax_id": "US-882910394",
        "address": "100 Silicon Blvd, Suite 400, San Jose, CA",
        "issue_date": "2026-02-05",
        "due_date": "2026-03-07",
        "po_number": "PO-2026-102",
        "currency": "USD",
        "items": [
            ("Network Patch Panel 48-Port", 10, 450.0, 4500.0)
        ],
        "subtotal": 4500.0,
        "tax": 0.0,
        "total": 4500.0,
        "notes": "Network equipment fulfillment."
    },
    {
        "filename": "INV-2026-003_VALID.pdf",
        "invoice_number": "INV-2026-003",
        "vendor_name": "Apex Logistics & Supply",
        "tax_id": "US-119283745",
        "address": "45 Harbor Way, Long Beach, CA",
        "issue_date": "2026-02-10",
        "due_date": "2026-02-25",
        "po_number": "PO-2026-103",
        "currency": "USD",
        "items": [
            ("Freight Shipping Container Handling", 4, 2000.0, 8000.0),
            ("Customs Clearance Filing Fee", 1, 800.0, 800.0)
        ],
        "subtotal": 8800.0,
        "tax": 0.0,
        "total": 8800.0,
        "notes": "Terms: Net 15 days."
    },
    {
        "filename": "INV-2026-004_VALID.pdf",
        "invoice_number": "INV-2026-004",
        "vendor_name": "Global Cloud Services LLC",
        "tax_id": "US-447722119",
        "address": "800 Cloud Vista Park, Seattle, WA",
        "issue_date": "2026-02-12",
        "due_date": "2026-03-29",
        "po_number": "PO-2026-105",
        "currency": "USD",
        "items": [
            ("Enterprise Kubernetes Cluster Tier 1", 1, 14000.0, 14000.0),
            ("24/7 Managed SRE Monitoring Support", 1, 1400.0, 1400.0)
        ],
        "subtotal": 15400.0,
        "tax": 0.0,
        "total": 15400.0,
        "notes": "Cloud infrastructure billing Q1."
    },
    {
        "filename": "INV-2026-005_VALID.pdf",
        "invoice_number": "INV-2026-005",
        "vendor_name": "CyberShield Security Ltd",
        "tax_id": "US-991122334",
        "address": "12 Cyber Fortress Rd, Austin, TX",
        "issue_date": "2026-02-14",
        "due_date": "2026-03-16",
        "po_number": "PO-2026-108",
        "currency": "USD",
        "items": [
            ("Annual Threat Intelligence License", 1, 18500.0, 18500.0)
        ],
        "subtotal": 18500.0,
        "tax": 0.0,
        "total": 18500.0,
        "notes": "Annual cyber defense platform subscription."
    },
    {
        "filename": "INV-2026-006_VALID.pdf",
        "invoice_number": "INV-2026-006",
        "vendor_name": "Pacific Data Equipment",
        "tax_id": "US-667788990",
        "address": "550 Tech Pier Blvd, Portland, OR",
        "issue_date": "2026-02-16",
        "due_date": "2026-03-18",
        "po_number": "PO-2026-110",
        "currency": "USD",
        "items": [
            ("Enterprise Storage Expansion Bay", 2, 7000.0, 14000.0)
        ],
        "subtotal": 14000.0,
        "tax": 0.0,
        "total": 14000.0,
        "notes": "Hardware SAN storage installation."
    },
    {
        "filename": "INV-2026-007_VALID.pdf",
        "invoice_number": "INV-2026-007",
        "vendor_name": "Summit Marketing Agency",
        "tax_id": "US-332211445",
        "address": "77 Madison Ave, New York, NY",
        "issue_date": "2026-02-18",
        "due_date": "2026-03-05",
        "po_number": "PO-2026-112",
        "currency": "USD",
        "items": [
            ("Product Launch PR Campaign", 1, 7500.0, 7500.0)
        ],
        "subtotal": 7500.0,
        "tax": 0.0,
        "total": 7500.0,
        "notes": "Media placement and press release."
    },
    {
        "filename": "INV-2026-008_VALID.pdf",
        "invoice_number": "INV-2026-008",
        "vendor_name": "Quantum Clean Facility Care",
        "tax_id": "US-778899112",
        "address": "900 Industrial Parkway, Chicago, IL",
        "issue_date": "2026-02-20",
        "due_date": "2026-03-22",
        "po_number": "PO-2026-114",
        "currency": "USD",
        "items": [
            ("Data Center Sanitization & Dust Control", 2, 1900.0, 3800.0)
        ],
        "subtotal": 3800.0,
        "tax": 0.0,
        "total": 3800.0,
        "notes": "Cleanroom ISO Class 8 certification maintenance."
    },
    {
        "filename": "INV-2026-009_VALID.pdf",
        "invoice_number": "INV-2026-009",
        "vendor_name": "Vanguard Legal Advisors",
        "tax_id": "US-223344556",
        "address": "1200 K Street NW, Washington, DC",
        "issue_date": "2026-02-22",
        "due_date": "2026-04-23",
        "po_number": "PO-2026-116",
        "currency": "USD",
        "items": [
            ("IP Retainer & Contract Review Services", 1, 25000.0, 25000.0)
        ],
        "subtotal": 25000.0,
        "tax": 0.0,
        "total": 25000.0,
        "notes": "Retainer contract Net 60."
    },
    {
        "filename": "INV-2026-010_VALID.pdf",
        "invoice_number": "INV-2026-010",
        "vendor_name": "TechCore Solutions Inc",
        "tax_id": "US-882910394",
        "address": "100 Silicon Blvd, Suite 400, San Jose, CA",
        "issue_date": "2026-02-24",
        "due_date": "2026-03-26",
        "po_number": "PO-2026-119",
        "currency": "USD",
        "items": [
            ("Cloud Firewall Appliance Setup", 2, 4900.0, 9800.0)
        ],
        "subtotal": 9800.0,
        "tax": 0.0,
        "total": 9800.0,
        "notes": "Deployment in primary zone."
    },

    # 10 Hóa đơn CỐ Ý VI PHẠM (REJECT / REVIEW)
    {
        "filename": "INV-ERR-011_UNKNOWN_VENDOR.pdf",
        "invoice_number": "INV-2026-011",
        "vendor_name": "Ghost Shadow Technologies",
        "tax_id": "US-999999999",  # Chưa đăng ký
        "address": "Unknown Island, Pacific Ocean",
        "issue_date": "2026-02-25",
        "due_date": "2026-03-27",
        "po_number": "PO-2026-101",
        "currency": "USD",
        "items": [
            ("Unverified Software License", 1, 5000.0, 5000.0)
        ],
        "subtotal": 5000.0,
        "tax": 0.0,
        "total": 5000.0,
        "notes": "TEST: Nhà cung cấp lạ không có trong Master Data -> VENDOR_UNKNOWN"
    },
    {
        "filename": "INV-ERR-012_BLOCKED_VENDOR.pdf",
        "invoice_number": "INV-2026-012",
        "vendor_name": "Nexus Office Furniture Co",
        "tax_id": "US-554433221",  # V004 - Status: blocked
        "address": "340 Market St, Denver, CO",
        "issue_date": "2026-02-25",
        "due_date": "2026-03-27",
        "po_number": "PO-2026-107",
        "currency": "USD",
        "items": [
            ("Ergonomic Mesh Chair Alpha", 12, 500.0, 6000.0)
        ],
        "subtotal": 6000.0,
        "tax": 0.0,
        "total": 6000.0,
        "notes": "TEST: Nhà cung cấp đang bị khóa -> VENDOR_BLOCKED"
    },
    {
        "filename": "INV-ERR-013_TAX_MISMATCH.pdf",
        "invoice_number": "INV-2026-013",
        "vendor_name": "TechCore Solutions Inc",
        "tax_id": "US-000011119",  # Sai MST (chuẩn là US-882910394)
        "address": "100 Silicon Blvd, Suite 400, San Jose, CA",
        "issue_date": "2026-02-26",
        "due_date": "2026-03-28",
        "po_number": "PO-2026-101",
        "currency": "USD",
        "items": [
            ("Server Memory Upgrade 64GB", 5, 500.0, 2500.0)
        ],
        "subtotal": 2500.0,
        "tax": 0.0,
        "total": 2500.0,
        "notes": "TEST: Tên đúng nhưng MST sai khác -> TAX_ID_MISMATCH"
    },
    {
        "filename": "INV-ERR-014_PO_NOT_FOUND.pdf",
        "invoice_number": "INV-2026-014",
        "vendor_name": "Apex Logistics & Supply",
        "tax_id": "US-119283745",
        "address": "45 Harbor Way, Long Beach, CA",
        "issue_date": "2026-02-26",
        "due_date": "2026-03-13",
        "po_number": "PO-INVALID-999",  # Không tồn tại
        "currency": "USD",
        "items": [
            ("Express Cargo Overnight", 2, 1000.0, 2000.0)
        ],
        "subtotal": 2000.0,
        "tax": 0.0,
        "total": 2000.0,
        "notes": "TEST: Mã PO không tồn tại trong DB -> PO_NOT_FOUND"
    },
    {
        "filename": "INV-ERR-015_PO_VENDOR_MISMATCH.pdf",
        "invoice_number": "INV-2026-015",
        "vendor_name": "CyberShield Security Ltd",
        "tax_id": "US-991122334",
        "address": "12 Cyber Fortress Rd, Austin, TX",
        "issue_date": "2026-02-27",
        "due_date": "2026-03-29",
        "po_number": "PO-2026-101",  # PO-2026-101 thuộc TechCore Solutions (V001) chứ không phải CyberShield (V005)
        "currency": "USD",
        "items": [
            ("Firewall Configuration Audit", 1, 12500.0, 12500.0)
        ],
        "subtotal": 12500.0,
        "tax": 0.0,
        "total": 12500.0,
        "notes": "TEST: Hóa đơn khai PO của đơn vị khác -> PO_VENDOR_MISMATCH"
    },
    {
        "filename": "INV-ERR-016_AMOUNT_EXCEEDS_PO.pdf",
        "invoice_number": "INV-2026-016",
        "vendor_name": "TechCore Solutions Inc",
        "tax_id": "US-882910394",
        "address": "100 Silicon Blvd, Suite 400, San Jose, CA",
        "issue_date": "2026-02-27",
        "due_date": "2026-03-29",
        "po_number": "PO-2026-102",  # Ngân sách PO là $4,500
        "currency": "USD",
        "items": [
            ("Network Patch Panel 48-Port Premium", 10, 850.0, 8500.0)  # Vượt lên $8,500 (+88%)
        ],
        "subtotal": 8500.0,
        "tax": 0.0,
        "total": 8500.0,
        "notes": "TEST: Số tiền vượt hạn mức PO quá 2% -> AMOUNT_EXCEEDS_PO"
    },
    {
        "filename": "INV-ERR-017_MATH_ERROR.pdf",
        "invoice_number": "INV-2026-017",
        "vendor_name": "Global Cloud Services LLC",
        "tax_id": "US-447722119",
        "address": "800 Cloud Vista Park, Seattle, WA",
        "issue_date": "2026-02-27",
        "due_date": "2026-04-13",
        "po_number": "PO-2026-105",
        "currency": "USD",
        "items": [
            ("Cloud Compute Instance Hours", 10, 100.0, 1000.0)  # 10 * 100 = 1000
        ],
        "subtotal": 1000.0,
        "tax": 100.0,
        "total": 2400.0,  # Sai số học rõ ràng! 1000 + 100 != 2400
        "notes": "TEST: Sai lệch số học cố ý -> MATH_ERROR"
    },
    {
        "filename": "INV-ERR-018_DUPLICATE_INVOICE.pdf",
        "invoice_number": "INV-EXISTING-001",  # Đã có trong DB
        "vendor_name": "TechCore Solutions Inc",
        "tax_id": "US-882910394",
        "address": "100 Silicon Blvd, Suite 400, San Jose, CA",
        "issue_date": "2026-02-28",
        "due_date": "2026-03-30",
        "po_number": "PO-2026-101",
        "currency": "USD",
        "items": [
            ("Duplicate Rack Shipment", 1, 13500.0, 13500.0)
        ],
        "subtotal": 13500.0,
        "tax": 0.0,
        "total": 13500.0,
        "notes": "TEST: Trùng số hóa đơn và vendor đã thanh toán -> DUPLICATE_INVOICE"
    },
    {
        "filename": "INV-WARN-019_PAYMENT_TERMS_ODD.pdf",
        "invoice_number": "INV-2026-019",
        "vendor_name": "Apex Logistics & Supply",
        "tax_id": "US-119283745",  # Hợp đồng chuẩn Net 15
        "address": "45 Harbor Way, Long Beach, CA",
        "issue_date": "2026-02-28",
        "due_date": "2026-06-30",  # Lệch 122 ngày! (quá hạn chuẩn 15 ngày)
        "po_number": "PO-2026-103",
        "currency": "USD",
        "items": [
            ("Freight Handling Expedited", 4, 2200.0, 8800.0)
        ],
        "subtotal": 8800.0,
        "tax": 0.0,
        "total": 8800.0,
        "notes": "TEST: Điều khoản thanh toán lệch quá xa hợp đồng -> PAYMENT_TERMS_ODD (warning)"
    },
    {
        "filename": "INV-WARN-020_LOW_CONFIDENCE.pdf",
        "invoice_number": "INV-2026-020",
        "vendor_name": "Pacific Data Equipment",
        "tax_id": "US-667788990",
        "address": "550 Tech Pier Blvd, Portland, OR",
        "issue_date": "2026-03-01",
        "due_date": "2026-03-31",
        "po_number": "PO-2026-111",
        "currency": "USD",
        "items": [
            ("Fiber Optic Transceivers Batch", 17, 300.0, 5100.0)
        ],
        "subtotal": 5100.0,
        "tax": 0.0,
        "total": 5100.0,
        "simulated_low_confidence": True,
        "notes": "TEST: Mô phỏng tài liệu mờ / OCR confidence thấp -> LOW_CONFIDENCE (warning)"
    }
]

def build_pdf(spec, output_dir):
    filepath = os.path.join(output_dir, spec["filename"])
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )
    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    bold_style = ParagraphStyle(
        'BoldMeta',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # Header Section
    header_data = [
        [
            Paragraph(f"<b>{spec['vendor_name']}</b><br/>{spec['address']}<br/>Tax ID / MST: <b>{spec['tax_id']}</b>", meta_style),
            Paragraph(f"<b>INVOICE / HÓA ĐƠN</b><br/><font color='#2563EB'>#{spec['invoice_number']}</font>", title_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[3.8 * inch, 3.2 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(header_table)

    story.append(Spacer(1, 10))

    # Details Box
    po_str = spec['po_number'] if spec['po_number'] else "N/A"
    details_data = [
        [
            Paragraph("<b>Issue Date / Ngày lập:</b>", bold_style),
            Paragraph(spec['issue_date'], meta_style),
            Paragraph("<b>Purchase Order (PO):</b>", bold_style),
            Paragraph(f"<font color='#1E40AF'><b>{po_str}</b></font>", meta_style)
        ],
        [
            Paragraph("<b>Due Date / Hạn thanh toán:</b>", bold_style),
            Paragraph(spec['due_date'], meta_style),
            Paragraph("<b>Currency / Tiền tệ:</b>", bold_style),
            Paragraph(spec['currency'], meta_style)
        ]
    ]
    details_table = Table(details_data, colWidths=[1.8 * inch, 1.7 * inch, 1.8 * inch, 1.7 * inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#EDF2F7')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(details_table)

    story.append(Spacer(1, 15))

    # Line Items Table
    table_rows = [
        [
            Paragraph("<b>#</b>", bold_style),
            Paragraph("<b>Item Description / Mô tả hàng hóa</b>", bold_style),
            Paragraph("<b>Qty</b>", bold_style),
            Paragraph("<b>Unit Price</b>", bold_style),
            Paragraph("<b>Amount / Thành tiền</b>", bold_style)
        ]
    ]

    for idx, item in enumerate(spec["items"], start=1):
        desc, qty, price, amt = item
        table_rows.append([
            Paragraph(str(idx), meta_style),
            Paragraph(desc, meta_style),
            Paragraph(str(qty), meta_style),
            Paragraph(f"${price:,.2f}", meta_style),
            Paragraph(f"${amt:,.2f}", bold_style)
        ])

    item_table = Table(table_rows, colWidths=[0.4 * inch, 3.6 * inch, 0.8 * inch, 1.1 * inch, 1.1 * inch])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(item_table)

    story.append(Spacer(1, 10))

    # Financial Summary
    summary_data = [
        [Paragraph("Subtotal / Tiền hàng:", meta_style), Paragraph(f"<b>${spec['subtotal']:,.2f}</b>", meta_style)],
        [Paragraph("Tax / Thuế:", meta_style), Paragraph(f"<b>${spec['tax']:,.2f}</b>", meta_style)],
        [Paragraph("<b>TOTAL DUE / TỔNG CỘNG:</b>", bold_style), Paragraph(f"<font color='#0F766E' size=11><b>${spec['total']:,.2f} {spec['currency']}</b></font>", bold_style)]
    ]
    summary_table = Table(summary_data, colWidths=[1.8 * inch, 1.4 * inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))

    # Wrap summary in layout with notes
    notes_para = Paragraph(f"<b>Ghi chú hóa đơn:</b><br/>{spec['notes']}", meta_style)
    layout_data = [[notes_para, summary_table]]
    layout_table = Table(layout_data, colWidths=[3.8 * inch, 3.2 * inch])
    layout_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (0,0), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (0,0), 8)
    ]))
    story.append(layout_table)

    # Invisible or subtle machine metadata tag for reliable deterministic extractor / verification
    meta_tag = f"[[METADATA: inv={spec['invoice_number']} | vendor={spec['vendor_name']} | tax_id={spec['tax_id']} | po={spec['po_number'] or ''} | issue={spec['issue_date']} | due={spec['due_date']} | curr={spec['currency']} | subtotal={spec['subtotal']} | tax={spec['tax']} | total={spec['total']} | low_conf={'1' if spec.get('simulated_low_confidence') else '0'}]]"
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<font color='#94A3B8' size=6>{meta_tag}</font>", meta_style))

    doc.build(story)
    return filepath

def generate_all_samples(target_dir=None):
    if not target_dir:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_data", "invoices"))
    else:
        base_dir = target_dir

    os.makedirs(base_dir, exist_ok=True)
    created = []
    for spec in SAMPLE_INVOICES_SPEC:
        path = build_pdf(spec, base_dir)
        created.append(path)
    print(f"Generated {len(created)} sample PDF invoices in {base_dir}")
    return created

if __name__ == "__main__":
    generate_all_samples()
