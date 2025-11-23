def score_calendar(row):
    """
    Professional calendar scoring model.
    Weighted blend of:
    - debit efficiency
    - vega differential
    - theta differential
    - extrinsic ratio
    - term structure decay
    """

    score = 0

    # 1) Debit sweet spot (cheap calendars score higher)
    if row["Debit"] is not None:
        if row["Debit"] < 0.20:  score += 2
        elif row["Debit"] < 0.40: score += 1

    # 2) Vega advantage
    if row["Vega Diff"] and row["Vega Diff"] > 0:
        score += 2

    # 3) Theta advantage (positive = good)
    if row["Theta Diff"] and row["Theta Diff"] > 0:
        score += 1

    # 4) Extrinsic ratio (back leg > front leg)
    er = row.get("Extrinsic Ratio")
    if er:
        if er > 1.3: score += 1
        if er > 1.6: score += 1

    # 5) Term structure decay (back IV > front IV)
    if row.get("IV Decay") and row["IV Decay"] > 0:
        score += 2

    return score
