import calendar
from datetime import date, datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def add_months(d: date, months: int) -> date:
    idx = d.month - 1 + months
    year, month = d.year + idx // 12, idx % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)
