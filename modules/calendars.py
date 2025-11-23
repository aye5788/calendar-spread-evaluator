def normalize_strike(x):
    """Convert strike into a float for consistent matching."""
    try:
        return float(x)
    except:
        return None


def extract_mid_price(row):
    """Compute mid price from call bid/ask."""
    try:
        bid = row.get("callBidPrice")
        ask = row.get("callAskPrice")
        if bid is None or ask is None:
            return None
        return (bid + ask) / 2
    except:
        return None


def extract_iv(row):
    """Use ORATS surface IV (smvVol)."""
    return row.get("smvVol", None)


def build_calendar_pairs(strikes, front_exp, back_exp):
    """
    Build all matching strike (front, back) calendar spreads.
    Returns a list of dictionaries ready to turn into a DataFrame.
    """

    # --- Filter rows for each expiration ---
    front_rows = [row for row in strikes if row["expirDate"] == front_exp]
    back_rows  = [row for row in strikes if row["expirDate"] == back_exp]

    # --- Build dict for fast back-leg lookup ---
    back_dict = {
        normalize_strike(r["strike"]): r
        for r in back_rows
        if normalize_strike(r["strike"]) is not None
    }

    results = []

    for f in front_rows:
        strike = normalize_strike(f["strike"])
        if strike is None:
            continue

        back = back_dict.get(strike)
        if not back:
            continue  # No matching strike → skip

        # Extract mid prices
        fm = extract_mid_price(f)
        bm = extract_mid_price(back)

        # Extract IVs
        fv = extract_iv(f)
        bv = extract_iv(back)

        # Build row
        results.append({
            "Strike": strike,
            "Front Mid": fm,
            "Back Mid": bm,
            "Debit": (bm - fm) if (fm is not None and bm is not None) else None,
            "Front IV": fv,
            "Back IV": bv,
            "IV Ratio": (bv / fv) if (fv and fv > 0 and bv) else None,
            "Vega Diff": (
                back.get("vega") - f.get("vega")
                if (back.get("vega") is not None and f.get("vega") is not None)
                else None
            ),
            "Theta Diff": (
                back.get("theta") - f.get("theta")
                if (back.get("theta") is not None and f.get("theta") is not None)
                else None
            ),
        })

    return results
