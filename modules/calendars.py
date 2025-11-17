def extract_mid_price(row):
    """Compute mid price from call bid/ask."""
    try:
        bid = row.get("callBidPrice", None)
        ask = row.get("callAskPrice", None)
        if bid is None or ask is None:
            return None
        return (bid + ask) / 2
    except:
        return None


def extract_iv(row):
    """Use ORATS surface IV."""
    return row.get("smvVol", None)


def build_calendar_pairs(strikes, front_exp, back_exp):
    """
    Build (front, back) calendar spread rows by matching strike.
    Returns a list of dicts ready to turn into a DataFrame.
    """

    front_rows = [row for row in strikes if row["expirDate"] == front_exp]
    back_rows = [row for row in strikes if row["expirDate"] == back_exp]

    # index by strike for fast matching
    back_dict = {r["strike"]: r for r in back_rows}

    results = []
    for f in front_rows:
        strike = f["strike"]
        back = back_dict.get(strike)

        if not back:
            continue

        fm = extract_mid_price(f)
        bm = extract_mid_price(back)

        fv = extract_iv(f)
        bv = extract_iv(back)

        results.append({
            "Strike": strike,
            "Front Mid": fm,
            "Back Mid": bm,
            "Debit": (bm - fm) if (fm is not None and bm is not None) else None,
            "Front IV": fv,
            "Back IV": bv,
            "IV Ratio": (bv / fv) if (fv and fv > 0 and bv) else None,
            "Vega Diff": (back.get("vega") - f.get("vega")) if back.get("vega") and f.get("vega") else None,
            "Theta Diff": (back.get("theta") - f.get("theta")) if back.get("theta") and f.get("theta") else None,
        })

    return results
