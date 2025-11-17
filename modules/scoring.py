def score_calendar(row):
    """
    Score a calendar spread row.
    You can adjust weightings as desired.
    """

    score = 0
    debit = row.get("Debit")
    iv_ratio = row.get("IV Ratio")
    vega_diff = row.get("Vega Diff")
    theta_diff = row.get("Theta Diff")

    # reward lower debit
    if debit is not None:
        score += max(0, 1.0 - debit / 2.0)

    # reward IV ratio > 1.0
    if iv_ratio is not None:
        score += (iv_ratio - 1.0) * 2

    # reward positive vega difference
    if vega_diff is not None:
        score += vega_diff * 0.1

    # reward positive theta difference
    if theta_diff is not None:
        score += theta_diff * 0.1

    return round(score, 4)
