"""
monthly_report.py
NorthStar Property Management

Generates a plain-text monthly summary email to the owner covering:
  - Rent roll status
  - Open/resolved maintenance
  - Cost-per-property breakdown
  - Upcoming lease expirations
  - Vendor insurance checks

This is the "C-level summary report" pattern applied to property management —
same concept used across a decade of enterprise platform reporting.
"""

from datetime import date, datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from tenant.tenant_registry import load_tenants
from maintenance.maintenance_tracker import load_work_orders, cost_by_property
from vendors.vendor_roster import load_vendors, check_insurance_expirations
from utils.notifier import send_alert


def generate_monthly_report(month: int = None, year: int = None) -> str:
    today = date.today()
    month = month or today.month
    year = year or today.year
    month_label = datetime(year, month, 1).strftime("%B %Y")

    sections = [
        f"NORTHSTAR PROPERTY MANAGEMENT — MONTHLY REPORT",
        f"Period: {month_label}",
        f"Generated: {today.isoformat()}",
        "=" * 60,
    ]

    # ── RENT ROLL ────────────────────────────────────────────────
    tenants = [t for t in load_tenants() if t.status == "active"]
    total_rent = sum(t.monthly_rent for t in tenants)
    sections.append(f"\n📋 RENT ROLL — {len(tenants)} active tenants")
    sections.append(f"   Total monthly income: ${total_rent:,.2f}")

    # Lease expiry warnings
    expiring_soon = []
    for t in tenants:
        lease_end = date.fromisoformat(t.lease_end)
        days = (lease_end - today).days
        if days <= 90:
            expiring_soon.append((t, days))

    if expiring_soon:
        sections.append(f"\n   ⚠️  Leases expiring within 90 days:")
        for t, days in sorted(expiring_soon, key=lambda x: x[1]):
            sections.append(f"      {t.name} @ {t.property_address} — {days} days ({t.lease_end})")
    else:
        sections.append("   ✅ No leases expiring within 90 days.")

    # ── MAINTENANCE ──────────────────────────────────────────────
    all_orders = load_work_orders()
    month_orders = [
        o for o in all_orders
        if o.reported_date and datetime.fromisoformat(o.reported_date).month == month
        and datetime.fromisoformat(o.reported_date).year == year
    ]
    resolved = [o for o in month_orders if o.status in ("resolved", "closed")]
    still_open = [o for o in all_orders if o.status not in ("resolved", "closed")]
    month_cost = sum(o.cost for o in resolved if o.cost)

    sections.append(f"\n🔧 MAINTENANCE — {month_label}")
    sections.append(f"   New work orders this month: {len(month_orders)}")
    sections.append(f"   Resolved: {len(resolved)}")
    sections.append(f"   Currently open: {len(still_open)}")
    sections.append(f"   Maintenance spend this month: ${month_cost:,.2f}")

    if still_open:
        sections.append(f"\n   Open items:")
        for o in sorted(still_open, key=lambda x: x.priority):
            sections.append(
                f"      [{o.priority.upper()}] {o.work_order_id} — {o.property_address} — {o.category}"
            )

    # ── COST BY PROPERTY ─────────────────────────────────────────
    ytd_costs = cost_by_property(year=year)
    if ytd_costs:
        sections.append(f"\n💰 MAINTENANCE COST BY PROPERTY (YTD {year})")
        for addr, total in ytd_costs.items():
            sections.append(f"   {addr}: ${total:,.2f}")
    else:
        sections.append(f"\n💰 No maintenance costs recorded YTD {year}.")

    # ── VENDOR ALERTS ─────────────────────────────────────────────
    expiring_insurance = check_insurance_expirations()
    if expiring_insurance:
        sections.append(f"\n⚠️  VENDOR INSURANCE EXPIRING SOON:")
        for v in expiring_insurance:
            sections.append(f"   {v.name} — expires {v.insurance_expiry}")
    else:
        sections.append("\n✅ All vendor insurance current.")

    # ── FOOTER ────────────────────────────────────────────────────
    sections.append("\n" + "=" * 60)
    sections.append("NorthStar Property Management ⭐")
    sections.append("Automated report — reply to owner address with any corrections.")

    return "\n".join(sections)


def send_monthly_report(month: int = None, year: int = None) -> None:
    report = generate_monthly_report(month=month, year=year)
    today = date.today()
    send_alert(
        subject=f"📊 NorthStar Monthly Report — {datetime(year or today.year, month or today.month, 1).strftime('%B %Y')}",
        body=report
    )
    print("✅ Monthly report sent.")
    print(report)


if __name__ == "__main__":
    print(generate_monthly_report())
