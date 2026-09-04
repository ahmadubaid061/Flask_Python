from datetime import date, timedelta


def current_period_label(frequency: str, committee_start_date: date = None, on_date: date = None) -> str:
    """Returns the label for 'today's' period counted from committee start date.
    
    frequency: "weekly" or "monthly"
    committee_start_date: when the committee started (e.g., 2026-09-04)
    on_date: the date to calculate for (defaults to today)
    
    Returns:
    - Weekly:  "W1", "W2", "W3" etc (counted from start_date)
    - Monthly: "M1", "M2", "M3" etc (counted from start_date)
    """
    on_date = on_date or date.today()
    
    if committee_start_date is None:
        committee_start_date = on_date
    
    if frequency == "weekly":
        # Calculate number of weeks since committee start
        days_since_start = (on_date - committee_start_date).days
        weeks_since_start = days_since_start // 7
        return f"W{weeks_since_start + 1}"
    
    elif frequency == "monthly":
        # Calculate number of months since committee start
        months_since_start = (on_date.year - committee_start_date.year) * 12
        months_since_start += (on_date.month - committee_start_date.month)
        return f"M{months_since_start + 1}"
    
    # Fallback
    return "P1"