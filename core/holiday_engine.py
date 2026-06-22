import json
from pathlib import Path
from datetime import datetime


# =========================================================
# LOAD DATA
# =========================================================
DATA_PATH = Path("data/holidays_us.json")
HOLIDAYS = json.loads(DATA_PATH.read_text())


# =========================================================
# NORMALIZE
# =========================================================
def _flatten_holidays():

    flat = []

    for month, items in HOLIDAYS.items():
        for item in items:
            flat.append((month, item))

    return flat


# =========================================================
# GET HOLIDAYS BY MONTH
# =========================================================
def get_holidays(month: str):

    items = HOLIDAYS.get(month.lower(), [])

    if not items:
        return f"No holidays found for {month.title()}."

    return f"Holidays in {month.title()}: " + ", ".join(items)


# =========================================================
# NEXT HOLIDAY (SIMPLE HEURISTIC ENGINE)
# =========================================================
def get_next_holiday():

    today = datetime.now()
    current_month = today.strftime("%B").lower()

    flat = _flatten_holidays()

    months_order = list(HOLIDAYS.keys())
    start_index = months_order.index(current_month)

    # search forward first
    for i in range(len(months_order)):

        month = months_order[(start_index + i) % len(months_order)]
        items = HOLIDAYS.get(month, [])

        if items:
            return f"Next holiday period: {items[0]}"

    return "No upcoming holidays found."


# =========================================================
# DAYS UNTIL NEXT HOLIDAY (APPROXIMATE)
# =========================================================
def days_until_next_holiday():

    today = datetime.now()

    # simple placeholder mapping (expandable later)
    holiday_map = {
        "june": 19,
        "july": 4,
        "december": 25
    }

    current_month = today.strftime("%B").lower()

    if current_month in holiday_map:
        target_day = holiday_map[current_month]
        delta = target_day - today.day

        if delta >= 0:
            return f"{delta} days until next major holiday."

    return "Next holiday is later in the year."