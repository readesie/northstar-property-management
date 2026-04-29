"""
vendor_roster.py
NorthStar Property Management

Preferred vendor database with contact info, specialty, work history,
and rating. Kills the "number in my phone" problem.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "vendors.json"


@dataclass
class Vendor:
    vendor_id: str
    name: str                    # Company name
    contact_person: str
    phone: str
    email: str
    specialty: list              # ["plumbing", "hvac", "electrical", ...]
    license_number: str = ""
    insurance_expiry: str = ""   # ISO date
    preferred: bool = True
    rating: float = 0.0          # 1.0–5.0, owner-assigned
    notes: str = ""
    jobs_completed: int = 0
    total_paid: float = 0.0


def load_vendors() -> list[Vendor]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE) as f:
        raw = json.load(f)
    return [Vendor(**v) for v in raw]


def save_vendors(vendors: list[Vendor]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump([asdict(v) for v in vendors], f, indent=2)


def add_vendor(vendor: Vendor) -> None:
    vendors = load_vendors()
    if any(v.vendor_id == vendor.vendor_id for v in vendors):
        raise ValueError(f"Vendor ID {vendor.vendor_id} already exists.")
    vendors.append(vendor)
    save_vendors(vendors)
    print(f"✅ Added vendor: {vendor.name}")


def find_by_specialty(specialty: str) -> list[Vendor]:
    return [
        v for v in load_vendors()
        if specialty.lower() in [s.lower() for s in v.specialty] and v.preferred
    ]


def update_job_stats(vendor_id: str, cost: float) -> None:
    vendors = load_vendors()
    for v in vendors:
        if v.vendor_id == vendor_id:
            v.jobs_completed += 1
            v.total_paid += cost
            save_vendors(vendors)
            return
    raise ValueError(f"Vendor {vendor_id} not found.")


def get_vendor_summary() -> str:
    vendors = load_vendors()
    if not vendors:
        return "No vendors on file."
    lines = ["VENDOR ROSTER", "=" * 50]
    for v in sorted(vendors, key=lambda x: x.rating, reverse=True):
        insurance_note = ""
        if v.insurance_expiry:
            exp = datetime.fromisoformat(v.insurance_expiry).date()
            days_left = (exp - datetime.now().date()).days
            insurance_note = f" | Insurance: {v.insurance_expiry}"
            if days_left < 30:
                insurance_note += " ⚠️ EXPIRING SOON"
        lines.append(
            f"\n⭐ {v.rating:.1f}  {v.name} ({', '.join(v.specialty)})\n"
            f"  Contact: {v.contact_person}  📞 {v.phone}\n"
            f"  Jobs: {v.jobs_completed} | Paid: ${v.total_paid:,.2f}{insurance_note}"
        )
    return "\n".join(lines)


def check_insurance_expirations() -> list[Vendor]:
    """Return vendors whose insurance expires within 60 days."""
    today = datetime.now().date()
    expiring = []
    for v in load_vendors():
        if not v.insurance_expiry:
            continue
        exp = datetime.fromisoformat(v.insurance_expiry).date()
        if (exp - today).days <= 60:
            expiring.append(v)
    return expiring


if __name__ == "__main__":
    print(get_vendor_summary())
