"""
maintenance_tracker.py
NorthStar Property Management

Work order lifecycle: open → dispatched → in-progress → resolved → closed.
Pain it kills: maintenance requests lost in texts, no vendor follow-up,
no history when the same problem recurs, no way to see cost trends.
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.notifier import send_alert

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "maintenance.json"

AGING_ALERT_HOURS = 72   # Alert owner if request unresolved after this many hours
VENDOR_FOLLOWUP_HOURS = 24  # Alert if vendor hasn't responded


@dataclass
class WorkOrder:
    work_order_id: str
    property_address: str
    unit: str
    reported_by: str          # tenant name or "owner"
    reported_date: str        # ISO datetime
    category: str             # plumbing | electrical | hvac | appliance | structural | exterior | other
    priority: str             # urgent | high | normal | low
    description: str
    status: str = "open"      # open | dispatched | in_progress | resolved | closed
    vendor_id: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_contacted_date: Optional[str] = None
    scheduled_date: Optional[str] = None
    resolved_date: Optional[str] = None
    cost: Optional[float] = None
    resolution_notes: str = ""
    photos: list = field(default_factory=list)   # file paths


def load_work_orders() -> list[WorkOrder]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE) as f:
        raw = json.load(f)
    return [WorkOrder(**w) for w in raw]


def save_work_orders(orders: list[WorkOrder]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump([asdict(o) for o in orders], f, indent=2, default=str)


def open_work_order(
    property_address: str,
    unit: str,
    reported_by: str,
    category: str,
    priority: str,
    description: str,
) -> WorkOrder:
    wo = WorkOrder(
        work_order_id=f"WO-{uuid.uuid4().hex[:8].upper()}",
        property_address=property_address,
        unit=unit,
        reported_by=reported_by,
        reported_date=datetime.now().isoformat(),
        category=category,
        priority=priority,
        description=description,
    )
    orders = load_work_orders()
    orders.append(wo)
    save_work_orders(orders)

    # Alert owner immediately on urgent
    if priority == "urgent":
        send_alert(
            subject=f"🚨 URGENT maintenance — {property_address} {unit}",
            body=(
                f"URGENT WORK ORDER OPENED\n\n"
                f"ID: {wo.work_order_id}\n"
                f"Property: {property_address} {unit}\n"
                f"Reported by: {reported_by}\n"
                f"Category: {category}\n"
                f"Description: {description}\n\n"
                f"Assign a vendor immediately."
            )
        )

    print(f"✅ Work order {wo.work_order_id} opened.")
    return wo


def dispatch_vendor(work_order_id: str, vendor_id: str, vendor_name: str) -> None:
    orders = load_work_orders()
    for o in orders:
        if o.work_order_id == work_order_id:
            o.vendor_id = vendor_id
            o.vendor_name = vendor_name
            o.vendor_contacted_date = datetime.now().isoformat()
            o.status = "dispatched"
            save_work_orders(orders)
            print(f"✅ {work_order_id} dispatched to {vendor_name}")
            return
    raise ValueError(f"Work order {work_order_id} not found.")


def resolve_work_order(work_order_id: str, cost: float, notes: str) -> None:
    orders = load_work_orders()
    for o in orders:
        if o.work_order_id == work_order_id:
            o.status = "resolved"
            o.resolved_date = datetime.now().isoformat()
            o.cost = cost
            o.resolution_notes = notes
            save_work_orders(orders)
            print(f"✅ {work_order_id} resolved. Cost: ${cost:,.2f}")
            return
    raise ValueError(f"Work order {work_order_id} not found.")


def check_aging_work_orders(dry_run: bool = False) -> list[dict]:
    """Alert owner on work orders open > AGING_ALERT_HOURS without resolution."""
    orders = load_work_orders()
    now = datetime.now()
    alerts = []

    for o in orders:
        if o.status in ("resolved", "closed"):
            continue
        opened = datetime.fromisoformat(o.reported_date)
        age_hours = (now - opened).total_seconds() / 3600

        if age_hours >= AGING_ALERT_HOURS:
            vendor_status = (
                f"Vendor: {o.vendor_name} (contacted {o.vendor_contacted_date})"
                if o.vendor_name
                else "No vendor assigned yet."
            )
            msg = (
                f"AGING WORK ORDER — {age_hours:.0f} hours open\n\n"
                f"ID: {o.work_order_id}\n"
                f"Property: {o.property_address} {o.unit}\n"
                f"Priority: {o.priority}\n"
                f"Category: {o.category}\n"
                f"Status: {o.status}\n"
                f"{vendor_status}\n\n"
                f"Description: {o.description}"
            )
            alerts.append({"work_order_id": o.work_order_id, "age_hours": age_hours})
            if not dry_run:
                send_alert(
                    subject=f"⏰ Work order aging ({age_hours:.0f}h) — {o.property_address}",
                    body=msg
                )

    return alerts


def get_open_summary() -> str:
    orders = [o for o in load_work_orders() if o.status not in ("resolved", "closed")]
    if not orders:
        return "✅ No open work orders."

    lines = [f"OPEN WORK ORDERS — {datetime.now().strftime('%Y-%m-%d %H:%M')}", "=" * 50]
    priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
    orders.sort(key=lambda o: priority_order.get(o.priority, 9))

    for o in orders:
        opened = datetime.fromisoformat(o.reported_date)
        age_hours = int((datetime.now() - opened).total_seconds() / 3600)
        vendor = o.vendor_name or "⚠️  No vendor"
        lines.append(
            f"\n[{o.priority.upper()}] {o.work_order_id}\n"
            f"  {o.property_address} {o.unit} — {o.category}\n"
            f"  Status: {o.status} | Vendor: {vendor}\n"
            f"  Age: {age_hours}h | {o.description[:80]}"
        )
    return "\n".join(lines)


def cost_by_property(year: int = None) -> dict:
    """Summarize maintenance costs by property address."""
    orders = [o for o in load_work_orders() if o.cost and o.status in ("resolved", "closed")]
    if year:
        orders = [
            o for o in orders
            if o.resolved_date and datetime.fromisoformat(o.resolved_date).year == year
        ]
    summary = {}
    for o in orders:
        summary.setdefault(o.property_address, 0.0)
        summary[o.property_address] += o.cost
    return dict(sorted(summary.items(), key=lambda x: x[1], reverse=True))


if __name__ == "__main__":
    print(get_open_summary())
