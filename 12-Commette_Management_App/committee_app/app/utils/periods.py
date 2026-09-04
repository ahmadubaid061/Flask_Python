from datetime import date


def current_period_label(frequency: str, on_date: date = None) -> str:
    """Returns the label for 'today's' period.
    Monthly -> "2026-09"
    Weekly  -> "2026-W36" (ISO week number)
    """
    on_date = on_date or date.today()
    if frequency == "weekly":
        iso_year, iso_week, _ = on_date.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"
    return f"{on_date.year}-{on_date.month:02d}"
