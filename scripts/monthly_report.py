#!/usr/bin/env python3
"""
monthly_report.py (script runner)
NorthStar Property Management

Sends the monthly summary report. Run on the 1st of each month.
Schedule: 0 8 1 * * python3 /path/to/scripts/monthly_report.py >> /var/log/northstar.log 2>&1
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent / "src"))
from reports.monthly_report import send_monthly_report

if __name__ == "__main__":
    today = datetime.now()
    # Allow override: python monthly_report.py 2025 3
    year = int(sys.argv[1]) if len(sys.argv) > 1 else today.year
    month = int(sys.argv[2]) if len(sys.argv) > 2 else today.month
    send_monthly_report(month=month, year=year)
