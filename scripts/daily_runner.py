#!/usr/bin/env python3
"""
daily_runner.py
NorthStar Property Management

The main cron entry point. Run once daily — does everything:
  - Lease expiration checks
  - Rent due reminders
  - Aging work order alerts
  - Vendor insurance expiry warnings

Logs every run with timestamp. Designed for unattended execution.
Schedule: 0 7 * * * python3 /path/to/scripts/daily_runner.py >> /var/log/northstar.log 2>&1
"""

import argparse
from utils.notifier import send_alert
import sys
import traceback
from datetime import datetime
from pathlib import Path

# ── CLI Arguments ───────────────────────────────────────────────
parser = argparse.ArgumentParser(description="NorthStar Daily Checks")
parser.add_argument(
    "--test-email",
    action="store_true",
    help="Send a test email to verify SMTP configuration and exit."
)
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Run checks without sending alerts."
)
args = parser.parse_args()

sys.path.append(str(Path(__file__).parent.parent / "src"))

from tenant.tenant_registry import check_lease_expirations, check_rent_due
from maintenance.maintenance_tracker import check_aging_work_orders
from vendors.vendor_roster import check_insurance_expirations
from utils.notifier import send_alert


def run_daily_checks(dry_run: bool = False) -> dict:
    timestamp = datetime.now().isoformat()
    print(f"\n[{timestamp}] NorthStar Daily Runner starting...")

    results = {
        "timestamp": timestamp,
        "lease_alerts": [],
        "rent_alerts": [],
        "maintenance_alerts": [],
        "vendor_alerts": [],
        "errors": [],
    }

    # ── Lease Expirations ─────────────────────────────────────────
    try:
        alerts = check_lease_expirations(dry_run=dry_run)
        results["lease_alerts"] = alerts
        print(f"  Lease checks: {len(alerts)} alert(s) fired.")
    except Exception as e:
        err = f"Lease check failed: {e}"
        results["errors"].append(err)
        print(f"  ❌ {err}")

    # ── Rent Due ──────────────────────────────────────────────────
    try:
        alerts = check_rent_due(dry_run=dry_run)
        results["rent_alerts"] = alerts
        print(f"  Rent checks: {len(alerts)} alert(s) fired.")
    except Exception as e:
        err = f"Rent check failed: {e}"
        results["errors"].append(err)
        print(f"  ❌ {err}")

    # ── Aging Work Orders ─────────────────────────────────────────
    try:
        alerts = check_aging_work_orders(dry_run=dry_run)
        results["maintenance_alerts"] = alerts
        print(f"  Maintenance checks: {len(alerts)} aging work order(s) flagged.")
    except Exception as e:
        err = f"Maintenance check failed: {e}"
        results["errors"].append(err)
        print(f"  ❌ {err}")

    # ── Vendor Insurance ──────────────────────────────────────────
    try:
        expiring = check_insurance_expirations()
        results["vendor_alerts"] = [v.vendor_id for v in expiring]
        if expiring and not dry_run:
            body = "Vendor insurance expiring within 60 days:\n\n" + "\n".join(
                f"  {v.name} — {v.insurance_expiry}" for v in expiring
            )
            send_alert(
                subject=f"⚠️ Vendor insurance expiring — {len(expiring)} vendor(s)",
                body=body
            )
        print(f"  Vendor checks: {len(expiring)} insurance expiration(s) found.")
    except Exception as e:
        err = f"Vendor check failed: {e}"
        results["errors"].append(err)
        print(f"  ❌ {err}")

    # ── Summary ───────────────────────────────────────────────────
    total_alerts = (
        len(results["lease_alerts"])
        + len(results["rent_alerts"])
        + len(results["maintenance_alerts"])
        + len(results["vendor_alerts"])
    )
    status = "✅ OK" if not results["errors"] else f"⚠️  {len(results['errors'])} error(s)"
    print(f"\n  Daily run complete. {total_alerts} alert(s). Status: {status}")
    print(f"  {'[DRY RUN — no alerts sent]' if dry_run else '[Alerts sent]'}\n")

    return results


if __name__ == "__main__":

    # ── Test Email Mode ──────────────────────────────────────────
    if args.test_email:
        send_alert(
            subject="NorthStar Test Email",
            body="This is a test email from the NorthStar Daily Checks workflow. SMTP configuration is working."
        )
        print("Test email sent successfully.")
        sys.exit(0)

    # ── Normal Daily Run ─────────────────────────────────────────
    try:
        run_daily_checks(dry_run=args.dry_run)
    except Exception:
        print("FATAL ERROR in daily runner:")
        traceback.print_exc()
        sys.exit(1)

