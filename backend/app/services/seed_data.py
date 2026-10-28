import json
from app.models.database import SessionLocal, VendorModel, PurchaseOrderModel, ProcessedInvoiceModel

VENDORS_SEED = [
    {
        "id": "V001",
        "name": "TechCore Solutions Inc",
        "tax_id": "US-882910394",
        "status": "active",
        "payment_terms_days": 30,
        "credit_limit": 150000.0
    },
    {
        "id": "V002",
        "name": "Apex Logistics & Supply",
        "tax_id": "US-119283745",
        "status": "active",
        "payment_terms_days": 15,
        "credit_limit": 80000.0
    },
    {
        "id": "V003",
        "name": "Global Cloud Services LLC",
        "tax_id": "US-447722119",
        "status": "active",
        "payment_terms_days": 45,
        "credit_limit": 300000.0
    },
    {
        "id": "V004",
        "name": "Nexus Office Furniture Co",
        "tax_id": "US-554433221",
        "status": "blocked",
        "payment_terms_days": 30,
        "credit_limit": 50000.0
    },
    {
        "id": "V005",
        "name": "CyberShield Security Ltd",
        "tax_id": "US-991122334",
        "status": "active",
        "payment_terms_days": 30,
        "credit_limit": 120000.0
    },
    {
        "id": "V006",
        "name": "Pacific Data Equipment",
        "tax_id": "US-667788990",
        "status": "active",
        "payment_terms_days": 30,
        "credit_limit": 90000.0
    },
    {
        "id": "V007",
        "name": "Summit Marketing Agency",
        "tax_id": "US-332211445",
        "status": "active",
        "payment_terms_days": 15,
        "credit_limit": 60000.0
    },
    {
        "id": "V008",
        "name": "Quantum Clean Facility Care",
        "tax_id": "US-778899112",
        "status": "active",
        "payment_terms_days": 30,
        "credit_limit": 40000.0
    },
    {
        "id": "V009",
        "name": "Vanguard Legal Advisors",
        "tax_id": "US-223344556",
        "status": "active",
        "payment_terms_days": 60,
        "credit_limit": 200000.0
    },
    {
        "id": "V010",
        "name": "Horizon HR & Payroll Systems",
        "tax_id": "US-889900112",
        "status": "blocked",
        "payment_terms_days": 30,
        "credit_limit": 75000.0
    }
]

POS_SEED = [
    {"po_number": "PO-2026-101", "vendor_id": "V001", "total_amount": 12500.00, "status": "open", "lines": [{"item": "Server Rack Mounting Unit", "qty": 5, "price": 2500.0}]},
    {"po_number": "PO-2026-102", "vendor_id": "V001", "total_amount": 4500.00, "status": "open", "lines": [{"item": "Network Patch Panel 48-Port", "qty": 10, "price": 450.0}]},
    {"po_number": "PO-2026-103", "vendor_id": "V002", "total_amount": 8800.00, "status": "open", "lines": [{"item": "Freight Shipping Container Handling", "qty": 4, "price": 2200.0}]},
    {"po_number": "PO-2026-104", "vendor_id": "V002", "total_amount": 3200.00, "status": "closed", "lines": [{"item": "Regional Courier Delivery Q1", "qty": 1, "price": 3200.0}]},
    {"po_number": "PO-2026-105", "vendor_id": "V003", "total_amount": 15400.00, "status": "open", "lines": [{"item": "Enterprise Kubernetes Cluster Tier 1", "qty": 1, "price": 15400.0}]},
    {"po_number": "PO-2026-106", "vendor_id": "V003", "total_amount": 28000.00, "status": "open", "lines": [{"item": "Dedicated Object Storage 50TB", "qty": 1, "price": 28000.0}]},
    {"po_number": "PO-2026-107", "vendor_id": "V004", "total_amount": 6000.00, "status": "open", "lines": [{"item": "Ergonomic Mesh Chair Alpha", "qty": 12, "price": 500.0}]},
    {"po_number": "PO-2026-108", "vendor_id": "V005", "total_amount": 18500.00, "status": "open", "lines": [{"item": "Annual Threat Intelligence License", "qty": 1, "price": 18500.0}]},
    {"po_number": "PO-2026-109", "vendor_id": "V005", "total_amount": 9200.00, "status": "open", "lines": [{"item": "SOC Endpoint Security Agent 100-Pack", "qty": 1, "price": 9200.0}]},
    {"po_number": "PO-2026-110", "vendor_id": "V006", "total_amount": 14000.00, "status": "open", "lines": [{"item": "Enterprise Storage Expansion Bay", "qty": 2, "price": 7000.0}]},
    {"po_number": "PO-2026-111", "vendor_id": "V006", "total_amount": 5100.00, "status": "open", "lines": [{"item": "High Speed Fiber Optic Tranceivers", "qty": 17, "price": 300.0}]},
    {"po_number": "PO-2026-112", "vendor_id": "V007", "total_amount": 7500.00, "status": "open", "lines": [{"item": "Product Launch PR Campaign", "qty": 1, "price": 7500.0}]},
    {"po_number": "PO-2026-113", "vendor_id": "V007", "total_amount": 11000.00, "status": "open", "lines": [{"item": "Quarterly Performance Ad Management", "qty": 1, "price": 11000.0}]},
    {"po_number": "PO-2026-114", "vendor_id": "V008", "total_amount": 3800.00, "status": "open", "lines": [{"item": "Data Center Sanitization & Dust Control", "qty": 2, "price": 1900.0}]},
    {"po_number": "PO-2026-115", "vendor_id": "V008", "total_amount": 2200.00, "status": "open", "lines": [{"item": "Office Deep Clean Protocol Tier 2", "qty": 1, "price": 2200.0}]},
    {"po_number": "PO-2026-116", "vendor_id": "V009", "total_amount": 25000.00, "status": "open", "lines": [{"item": "IP Retainer & Contract Review Services", "qty": 1, "price": 25000.0}]},
    {"po_number": "PO-2026-117", "vendor_id": "V009", "total_amount": 16000.00, "status": "open", "lines": [{"item": "Merger Compliance Consulting", "qty": 1, "price": 16000.0}]},
    {"po_number": "PO-2026-118", "vendor_id": "V010", "total_amount": 8500.00, "status": "closed", "lines": [{"item": "HRIS Subscription Q1", "qty": 1, "price": 8500.0}]},
    {"po_number": "PO-2026-119", "vendor_id": "V001", "total_amount": 9800.00, "status": "open", "lines": [{"item": "Cloud Firewall Appliance Setup", "qty": 2, "price": 4900.0}]},
    {"po_number": "PO-2026-120", "vendor_id": "V003", "total_amount": 5200.00, "status": "open", "lines": [{"item": "Managed Backup Snapshot Reserve", "qty": 1, "price": 5200.0}]}
]

def seed_database():
    db = SessionLocal()
    try:
        # Seed Vendors
        for v in VENDORS_SEED:
            existing = db.query(VendorModel).filter(VendorModel.id == v["id"]).first()
            if not existing:
                vendor = VendorModel(
                    id=v["id"],
                    name=v["name"],
                    tax_id=v["tax_id"],
                    status=v["status"],
                    payment_terms_days=v["payment_terms_days"],
                    credit_limit=v["credit_limit"]
                )
                db.add(vendor)
            else:
                existing.name = v["name"]
                existing.tax_id = v["tax_id"]
                existing.status = v["status"]
                existing.payment_terms_days = v["payment_terms_days"]
                existing.credit_limit = v["credit_limit"]

        # Seed Purchase Orders
        for p in POS_SEED:
            existing_po = db.query(PurchaseOrderModel).filter(PurchaseOrderModel.po_number == p["po_number"]).first()
            if not existing_po:
                po = PurchaseOrderModel(
                    po_number=p["po_number"],
                    vendor_id=p["vendor_id"],
                    total_amount=p["total_amount"],
                    status=p["status"],
                    lines_json=json.dumps(p["lines"])
                )
                db.add(po)
            else:
                existing_po.vendor_id = p["vendor_id"]
                existing_po.total_amount = p["total_amount"]
                existing_po.status = p["status"]
                existing_po.lines_json = json.dumps(p["lines"])

        # Seed one existing processed invoice for DUPLICATE_INVOICE check test:
        # e.g., INV-EXISTING-001 by TechCore Solutions Inc (tax_id US-882910394)
        dup_test_num = "INV-EXISTING-001"
        existing_inv = db.query(ProcessedInvoiceModel).filter(ProcessedInvoiceModel.invoice_number == dup_test_num).first()
        if not existing_inv:
            inv = ProcessedInvoiceModel(
                invoice_number=dup_test_num,
                vendor_tax_id="US-882910394",
                vendor_name="TechCore Solutions Inc",
                po_number="PO-2026-101",
                issue_date="2026-01-15",
                total_amount=13500.0,
                outcome="APPROVE",
                raw_document_json="{}",
                violations_json="[]"
            )
            db.add(inv)

        db.commit()
        print("Database successfully seeded with 10 vendors and 20 POs!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    from app.models.database import init_db
    init_db()
    seed_database()
