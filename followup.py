#!/usr/bin/env python3
"""Who do I need to call today?

Reads leads.csv and prints a prioritized call list. Run it every morning.

    python3 followup.py

Change the numbers in the RULES block below to match how you like to work.
"""

import csv
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

LEADS_FILE = Path(__file__).parent / "leads.csv"

# ---- RULES: how many days before the next touch ------------------------
NEW_LEAD = 0        # call the same day it comes in
AFTER_CONTACT = 2   # talked to them, no appointment yet
AFTER_QUOTE = 3     # quote is out, still deciding
REVISIT_LOST = 180  # circle back next season
GOING_COLD = 60     # flag open leads older than this
# ------------------------------------------------------------------------

OPEN_STATUSES = {"new", "contacted", "appointment_set", "quoted"}


def parse_date(value):
    value = (value or "").strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def money(value):
    try:
        return float(str(value).replace("$", "").replace(",", "").strip() or 0)
    except ValueError:
        return 0.0


def next_touch(lead, today):
    """Return (due_date, why) for the next call, or None if nothing is owed."""
    status = lead.get("status", "").strip().lower()
    last = parse_date(lead.get("last_contact"))
    received = parse_date(lead.get("date_received"))

    scheduled = parse_date(lead.get("next_followup"))
    if scheduled:
        return scheduled, "on the calendar"

    if status == "new":
        return (received or today) + timedelta(days=NEW_LEAD), "brand new, call before someone else does"

    if status == "contacted":
        base = last or received or today
        return base + timedelta(days=AFTER_CONTACT), "spoke to them, no appointment yet"

    if status == "quoted":
        base = last or received or today
        return base + timedelta(days=AFTER_QUOTE), "quote is out, still deciding"

    if status == "lost":
        base = last or received
        if not base:
            return None
        return base + timedelta(days=REVISIT_LOST), "lost a while back, worth another shot"

    # appointment_set with no date, and won, need nothing
    return None


def load_leads():
    if not LEADS_FILE.exists():
        sys.exit(f"Can't find {LEADS_FILE.name}. Is it in the same folder as this script?")
    with LEADS_FILE.open(newline="", encoding="utf-8") as handle:
        return [row for row in csv.DictReader(handle) if (row.get("name") or "").strip()]


def show(heading, rows, today):
    if not rows:
        return
    print(f"\n{heading}")
    print("-" * len(heading))
    for due, lead in rows:
        overdue = (today - due).days
        if overdue > 0:
            timing = f"{overdue} day{'s' if overdue != 1 else ''} late"
        elif overdue == 0:
            timing = "today"
        else:
            timing = f"in {-overdue} day{'s' if overdue != -1 else ''}"
        amount = money(lead.get("quote_amount"))
        tag = f"  ${amount:,.0f}" if amount else ""
        _, why = next_touch(lead, today)
        print(f"  {lead['name']:<18} {lead['phone']:<11} {lead.get('job_type', ''):<8} {timing:<12}{tag}")
        print(f"    {why}. {lead.get('notes', '').strip()}")


def main():
    today = date.today()
    leads = load_leads()

    due_now, upcoming, cold = [], [], []
    for lead in leads:
        result = next_touch(lead, today)
        if not result:
            continue
        due, _ = result
        if due <= today:
            due_now.append((due, lead))
        elif due <= today + timedelta(days=7):
            upcoming.append((due, lead))

    for lead in leads:
        received = parse_date(lead.get("date_received"))
        status = lead.get("status", "").strip().lower()
        if received and status in OPEN_STATUSES and (today - received).days > GOING_COLD:
            cold.append((received, lead))

    due_now.sort(key=lambda pair: pair[0])
    upcoming.sort(key=lambda pair: pair[0])

    print(f"\nFOLLOW-UP LIST for {today:%A, %B %d, %Y}")

    if not due_now:
        print("\nNobody is overdue. Nice work.")
    show(f"CALL TODAY ({len(due_now)})", due_now, today)
    show(f"COMING UP ({len(upcoming)})", upcoming, today)
    show(f"GOING COLD ({len(cold)})", [(d, l) for d, l in cold], today)

    quoted = sum(money(l.get("quote_amount")) for l in leads
                 if l.get("status", "").strip().lower() == "quoted")
    won = sum(money(l.get("quote_amount")) for l in leads
              if l.get("status", "").strip().lower() == "won")
    open_count = sum(1 for l in leads if l.get("status", "").strip().lower() in OPEN_STATUSES)

    print(f"\nPIPELINE")
    print("-" * 8)
    print(f"  Open leads:        {open_count}")
    print(f"  Quotes out:        ${quoted:,.0f}")
    print(f"  Landed (all time): ${won:,.0f}")
    print()


if __name__ == "__main__":
    main()
