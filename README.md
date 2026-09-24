# Lead Follow-Up

A dead-simple system for making sure no lead goes cold.

Two files:

- **leads.csv** — every lead, one row each. Opens in Excel or Google Sheets.
- **followup.py** — reads that file and tells you who to call today.

## Using it

You don't have to run anything yourself. With Claude Code open in this
folder, just ask:

> who do I need to call today?

If you'd rather run it directly:

    python3 followup.py

## The columns

| Column | What goes in it |
| --- | --- |
| `date_received` | When the lead came in (`2026-09-14` format) |
| `name` / `phone` / `address` | The basics |
| `source` | Where it came from — referral, google, facebook, yard_sign, door_knock |
| `job_type` | roof, siding, gutters, windows, deck, paint |
| `status` | new → contacted → appointment_set → quoted → won or lost |
| `quote_amount` | Dollar figure once you've quoted. Leave blank until then |
| `last_contact` | Last time you actually reached out |
| `next_followup` | Only if you promised a specific date. Otherwise leave blank |
| `notes` | Anything you'd want to remember before dialing |

The only field you have to stay on top of is `last_contact`. Everything
else is calculated from it.

## When it tells you to call

| Status | Next touch |
| --- | --- |
| `new` | Same day. Speed matters more than anything else here |
| `contacted` | Every 2 days until you get an appointment |
| `appointment_set` | Nothing — it's on the calendar |
| `quoted` | Every 3 days while they're deciding |
| `won` | Nothing. Go ask for the referral |
| `lost` | Circle back in 6 months |

Any open lead older than 60 days gets flagged as going cold — time to
either push it or kill it.

To change any of those intervals, edit the `RULES` block near the top of
`followup.py`, or just ask Claude to change them.
