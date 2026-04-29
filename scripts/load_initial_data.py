#!/usr/bin/env python3
"""
load_initial_data.py
NorthStar Property Management

Bootstrap script — run once to load sample data for all modules.
Replace everything below the "SAMPLE DATA" headers with your real properties.

Usage: python scripts/load_initial_data.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime, date, timedelta

sys.path.append(str(Path(__file__).parent.parent / "src"))

from tenant.tenant_registry import add_tenant, Tenant, DATA_FILE as TENANT_FILE
from vendors.vendor_roster import add_vendor, Vendor, DATA_FILE as VENDOR_FILE
from maintenance.maintenance_tracker import WorkOrder, DATA_FILE as MAINT_FILE
from leases.lease_index import LeaseRecord, DATA_FILE as LEASE_FILE

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────────────────────
# SAMPLE TENANTS
# Five realistic tenants across four properties.
# ─────────────────────────────────────────────────────────────
SAMPLE_TENANTS = [
    Tenant(
        tenant_id="T-001",
        name="Jane Smith",
        property_address="123 Maple St",
        unit="",
        phone="555-555-0101",
        email="jane.smith@example.com",
        lease_start="2024-06-01",
        lease_end="2026-05-31",
        monthly_rent=1250.00,
        security_deposit=1250.00,
        status="active",
        notes="Excellent tenant, pays early, no issues in 2 years.",
        emergency_contact_name="Tom Smith (husband)",
        emergency_contact_phone="555-555-0111",
    ),
    Tenant(
        tenant_id="T-002",
        name="Carlos Reyes",
        property_address="456 Oak Ave",
        unit="Unit A",
        phone="555-555-0202",
        email="carlos.reyes@example.com",
        lease_start="2024-09-01",
        lease_end="2026-08-31",
        monthly_rent=975.00,
        security_deposit=975.00,
        status="active",
        notes="Has one dog (approved). Quiet, no complaints from neighbors.",
        emergency_contact_name="Maria Reyes (sister)",
        emergency_contact_phone="555-555-0212",
    ),
    Tenant(
        tenant_id="T-003",
        name="DeShawn & Keisha Williams",
        property_address="456 Oak Ave",
        unit="Unit B",
        phone="555-555-0303",
        email="dkwilliams@example.com",
        lease_start="2025-02-01",
        lease_end="2026-01-31",
        monthly_rent=1050.00,
        security_deposit=1050.00,
        status="active",
        notes="New tenants as of Feb 2025. Lease expires soon — renewal conversation needed.",
        emergency_contact_name="Brenda Williams (mother)",
        emergency_contact_phone="555-555-0313",
    ),
    Tenant(
        tenant_id="T-004",
        name="Patricia Nguyen",
        property_address="789 Birch Ln",
        unit="",
        phone="555-555-0404",
        email="pat.nguyen@example.com",
        lease_start="2023-11-01",
        lease_end="2026-10-31",
        monthly_rent=1400.00,
        security_deposit=1400.00,
        status="active",
        notes="Long-term tenant, 3+ years. Handles minor landscaping voluntarily.",
        emergency_contact_name="Kevin Nguyen (son)",
        emergency_contact_phone="555-555-0414",
    ),
    Tenant(
        tenant_id="T-005",
        name="Marcus Webb",
        property_address="1010 Elm Ct",
        unit="",
        phone="555-555-0505",
        email="marcus.webb@example.com",
        lease_start="2025-08-01",
        lease_end="2026-07-31",
        monthly_rent=1100.00,
        security_deposit=1100.00,
        status="active",
        notes="First rental, references checked out. No issues so far.",
        emergency_contact_name="Sandra Webb (mother)",
        emergency_contact_phone="555-555-0515",
    ),
]


# ─────────────────────────────────────────────────────────────
# SAMPLE VENDORS
# ─────────────────────────────────────────────────────────────
SAMPLE_VENDORS = [
    Vendor(
        vendor_id="V-001",
        name="Ace Plumbing & Drain",
        contact_person="Mike Torres",
        phone="555-555-0301",
        email="mike@aceplumbing.example.com",
        specialty=["plumbing"],
        license_number="PL-12345",
        insurance_expiry="2026-09-15",
        preferred=True,
        rating=4.8,
        notes="24hr emergency line. Fast response, fair pricing. First call for any plumbing.",
        jobs_completed=7,
        total_paid=3240.00,
    ),
    Vendor(
        vendor_id="V-002",
        name="ProHeat HVAC",
        contact_person="Sandra Liu",
        phone="555-555-0302",
        email="sandra@proheat.example.com",
        specialty=["hvac", "heating", "cooling"],
        license_number="HVAC-77321",
        insurance_expiry="2026-06-28",
        preferred=True,
        rating=4.5,
        notes="Annual service contracts available. Seasonal tune-ups in April and October.",
        jobs_completed=4,
        total_paid=1875.00,
    ),
    Vendor(
        vendor_id="V-003",
        name="All-Around Electric",
        contact_person="Dave Kowalski",
        phone="555-555-0303",
        email="dave@allaroundelectric.example.com",
        specialty=["electrical"],
        license_number="EL-98765",
        insurance_expiry="2026-03-01",
        preferred=True,
        rating=4.7,
        notes="Licensed master electrician. Good for panel work and outlet upgrades.",
        jobs_completed=3,
        total_paid=1120.00,
    ),
    Vendor(
        vendor_id="V-004",
        name="Handy Brothers Repair",
        contact_person="Rick Handy",
        phone="555-555-0304",
        email="rick@handybrothers.example.com",
        specialty=["appliance", "drywall", "carpentry", "general"],
        insurance_expiry="2026-11-30",
        preferred=True,
        rating=4.3,
        notes="General handyman for smaller jobs. Not licensed for plumbing/electric.",
        jobs_completed=11,
        total_paid=2650.00,
    ),
    Vendor(
        vendor_id="V-005",
        name="GreenThumb Lawn & Snow",
        contact_person="Jorge Medina",
        phone="555-555-0305",
        email="jorge@greenthumb.example.com",
        specialty=["lawn", "landscaping", "snow removal"],
        insurance_expiry="2026-08-01",
        preferred=True,
        rating=4.6,
        notes="Seasonal contracts. Snow removal available Nov–Mar. Handles 3 properties.",
        jobs_completed=18,
        total_paid=4100.00,
    ),
]


# ─────────────────────────────────────────────────────────────
# SAMPLE MAINTENANCE WORK ORDERS
# Mix of resolved historical and currently open items.
# ─────────────────────────────────────────────────────────────
def _dt(days_ago: int) -> str:
    return (datetime.now() - timedelta(days=days_ago)).isoformat()

SAMPLE_WORK_ORDERS = [
    # ── Resolved historical items ──────────────────────────────
    WorkOrder(
        work_order_id="WO-A1B2C3D4",
        property_address="123 Maple St",
        unit="",
        reported_by="Jane Smith",
        reported_date=_dt(120),
        category="plumbing",
        priority="high",
        description="Kitchen sink drain clogged, backing up into cabinet.",
        status="closed",
        vendor_id="V-001",
        vendor_name="Ace Plumbing & Drain",
        vendor_contacted_date=_dt(120),
        scheduled_date=_dt(119),
        resolved_date=_dt(118),
        cost=285.00,
        resolution_notes="Snaked drain, cleared grease blockage. Recommended strainer.",
    ),
    WorkOrder(
        work_order_id="WO-E5F6G7H8",
        property_address="789 Birch Ln",
        unit="",
        reported_by="Patricia Nguyen",
        reported_date=_dt(90),
        category="hvac",
        priority="normal",
        description="AC not cooling — blowing warm air.",
        status="closed",
        vendor_id="V-002",
        vendor_name="ProHeat HVAC",
        vendor_contacted_date=_dt(90),
        scheduled_date=_dt(88),
        resolved_date=_dt(87),
        cost=420.00,
        resolution_notes="Low on refrigerant. Recharged R-410A, checked coils. Running well.",
    ),
    WorkOrder(
        work_order_id="WO-I9J0K1L2",
        property_address="456 Oak Ave",
        unit="Unit A",
        reported_by="Carlos Reyes",
        reported_date=_dt(60),
        category="appliance",
        priority="normal",
        description="Dishwasher not draining, standing water after cycle.",
        status="closed",
        vendor_id="V-004",
        vendor_name="Handy Brothers Repair",
        vendor_contacted_date=_dt(59),
        scheduled_date=_dt(57),
        resolved_date=_dt(56),
        cost=175.00,
        resolution_notes="Cleared drain hose kink and filter. Full cycle tested OK.",
    ),
    WorkOrder(
        work_order_id="WO-M3N4O5P6",
        property_address="1010 Elm Ct",
        unit="",
        reported_by="Marcus Webb",
        reported_date=_dt(30),
        category="electrical",
        priority="high",
        description="GFCI outlet in bathroom tripping repeatedly, won't reset.",
        status="closed",
        vendor_id="V-003",
        vendor_name="All-Around Electric",
        vendor_contacted_date=_dt(30),
        scheduled_date=_dt(28),
        resolved_date=_dt(27),
        cost=210.00,
        resolution_notes="Replaced faulty GFCI outlet. Tested all bathroom circuit loads.",
    ),
    # ── Currently open items ───────────────────────────────────
    WorkOrder(
        work_order_id="WO-Q7R8S9T0",
        property_address="456 Oak Ave",
        unit="Unit B",
        reported_by="DeShawn Williams",
        reported_date=_dt(5),
        category="plumbing",
        priority="normal",
        description="Bathroom faucet dripping constantly. Hot side, slow drip.",
        status="dispatched",
        vendor_id="V-001",
        vendor_name="Ace Plumbing & Drain",
        vendor_contacted_date=_dt(4),
        scheduled_date=(date.today() + timedelta(days=2)).isoformat(),
        resolution_notes="",
    ),
    WorkOrder(
        work_order_id="WO-U1V2W3X4",
        property_address="789 Birch Ln",
        unit="",
        reported_by="Patricia Nguyen",
        reported_date=_dt(2),
        category="structural",
        priority="high",
        description="Back deck board cracked and split — safety concern, one board sunken.",
        status="open",
        resolution_notes="",
    ),
]


# ─────────────────────────────────────────────────────────────
# SAMPLE LEASE RECORDS
# ─────────────────────────────────────────────────────────────
SAMPLE_LEASES = [
    LeaseRecord(
        lease_id="L-001",
        tenant_id="T-001",
        tenant_name="Jane Smith",
        property_address="123 Maple St",
        unit="",
        lease_start="2024-06-01",
        lease_end="2026-05-31",
        monthly_rent=1250.00,
        security_deposit=1250.00,
        document_path="data/leases/L-001_Jane_Smith_123Maple.pdf",
        renewal_status="none",
        rent_increase_clause=True,
        pet_allowed=False,
        notes="Standard 2-year lease. Includes 3% annual rent increase clause.",
    ),
    LeaseRecord(
        lease_id="L-002",
        tenant_id="T-002",
        tenant_name="Carlos Reyes",
        property_address="456 Oak Ave",
        unit="Unit A",
        lease_start="2024-09-01",
        lease_end="2026-08-31",
        monthly_rent=975.00,
        security_deposit=975.00,
        document_path="data/leases/L-002_Carlos_Reyes_456Oak_UnitA.pdf",
        renewal_status="none",
        rent_increase_clause=False,
        pet_allowed=True,
        notes="Pet addendum signed — one dog up to 50 lbs. $200 pet deposit collected.",
    ),
    LeaseRecord(
        lease_id="L-003",
        tenant_id="T-003",
        tenant_name="DeShawn & Keisha Williams",
        property_address="456 Oak Ave",
        unit="Unit B",
        lease_start="2025-02-01",
        lease_end="2026-01-31",
        monthly_rent=1050.00,
        security_deposit=1050.00,
        document_path="data/leases/L-003_Williams_456Oak_UnitB.pdf",
        renewal_status="none",
        rent_increase_clause=False,
        pet_allowed=False,
        notes="⚠️ Lease expires Jan 31 2026 — begin renewal conversation by Nov 2025.",
    ),
    LeaseRecord(
        lease_id="L-004",
        tenant_id="T-004",
        tenant_name="Patricia Nguyen",
        property_address="789 Birch Ln",
        unit="",
        lease_start="2023-11-01",
        lease_end="2026-10-31",
        monthly_rent=1400.00,
        security_deposit=1400.00,
        document_path="data/leases/L-004_Patricia_Nguyen_789Birch.pdf",
        renewal_status="none",
        rent_increase_clause=True,
        pet_allowed=False,
        notes="Third consecutive lease with Patricia. Reliable long-term tenant.",
    ),
    LeaseRecord(
        lease_id="L-005",
        tenant_id="T-005",
        tenant_name="Marcus Webb",
        property_address="1010 Elm Ct",
        unit="",
        lease_start="2025-08-01",
        lease_end="2026-07-31",
        monthly_rent=1100.00,
        security_deposit=1100.00,
        document_path="data/leases/L-005_Marcus_Webb_1010Elm.pdf",
        renewal_status="none",
        rent_increase_clause=False,
        pet_allowed=False,
        notes="First-time renter. Move-in inspection completed and signed.",
    ),
]


# ─────────────────────────────────────────────────────────────
# LOADER
# ─────────────────────────────────────────────────────────────
def main():
    print("NorthStar — Loading sample data...\n")

    print("📋 Loading tenants:")
    for t in SAMPLE_TENANTS:
        try:
            add_tenant(t)
        except ValueError as e:
            print(f"  Skipped: {e}")

    print("\n👷 Loading vendors:")
    for v in SAMPLE_VENDORS:
        try:
            add_vendor(v)
        except ValueError as e:
            print(f"  Skipped: {e}")

    print("\n🔧 Loading maintenance work orders:")
    existing = []
    if MAINT_FILE.exists():
        with open(MAINT_FILE) as f:
            existing = json.load(f)
    existing_ids = {w["work_order_id"] for w in existing}
    new_orders = [w for w in SAMPLE_WORK_ORDERS if w.work_order_id not in existing_ids]
    from dataclasses import asdict
    all_orders = existing + [asdict(w) for w in new_orders]
    MAINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MAINT_FILE, "w") as f:
        json.dump(all_orders, f, indent=2, default=str)
    print(f"  Loaded {len(new_orders)} work orders ({len(SAMPLE_WORK_ORDERS) - len(new_orders)} skipped as duplicates).")

    print("\n📄 Loading lease records:")
    existing_leases = []
    if LEASE_FILE.exists():
        with open(LEASE_FILE) as f:
            existing_leases = json.load(f)
    existing_lease_ids = {r["lease_id"] for r in existing_leases}
    new_leases = [r for r in SAMPLE_LEASES if r.lease_id not in existing_lease_ids]
    all_leases = existing_leases + [asdict(r) for r in new_leases]
    LEASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LEASE_FILE, "w") as f:
        json.dump(all_leases, f, indent=2)
    print(f"  Loaded {len(new_leases)} lease records.")

    print("\n✅ All sample data loaded.")
    print("   Edit the SAMPLE_* lists in this file to replace with your real data.")
    print("   Then run: python scripts/daily_runner.py --dry-run\n")


if __name__ == "__main__":
    main()
