import numpy as np


def score_calendar(row):
    """Composite scoring for calendars."""

    score = 0

    # 1. IV Ratio weighting
    ivr = row.get("IV Ratio")
    if ivr:
        if ivr >= 1.10:
            score += 3
        elif ivr >= 1.05:
            score += 2
        elif ivr >= 1.00:
            score += 1

    # 2. Debit favorability
    debit = row.get("Debit")
    if debit is not None:
        if debit < 0.10:
            score += 2
        elif debit < 0.20:
            score += 1

    # 3. Vega exposure
    vega = row.get("Vega Diff")
    if vega is not None and vega > 0:
        score += 1

    # 4. Theta exposure
    theta = row.get("Theta Diff")
    if theta is not None and theta > 0:
        score += 1

    # 5. Moneyness
    mn = row.get("Moneyness")
    if mn:
        if 0.98 <= mn <= 1.02:
            score += 2
        elif 0.95 <= mn <= 1.05:
            score += 1

    return score

