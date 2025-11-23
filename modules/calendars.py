import numpy as np


def normalize_strike(x):
    try:
        return float(x)
    except:
        return None


def extract_mid(row):
    try:
        bid = row.get("callBidPrice")
        ask = row.get("callAskPrice")
        if bid is None or ask is None:
            return None
        return (bid + ask) / 2
    except:
        return None


def extrinsic_value(row):
    """(Mid − intrinsic for CALL)"""
    mid = extract_mid(row)
    if mid is None:
        return None

    spot = row.get("stockPrice")
    strike = row.get("strike")
    if spot is None or strike is None:
        return None

    intrinsic = max(spot - strike, 0)
    return max(mid - intrinsic, 0)


def map_expiration_to_iv(exp_dte, term_structure):
    """
    Match expiration DTE to closest ORATS IV bucket.
    (Core-level ATM implied vol)
    """
    buckets = term_structure["buckets"]
    if not buckets:
        return None

    best = min(
        buckets,
        key=lambda b: abs(b["dte"] - exp_dte)
    )
    return best["iv"]


def build_calendar_pairs(strikes, front_exp, back_exp, term_structure):
    """
    Professional calendar model:
    - moneyness filter
    - greek differentials
    - extrinsic
    - debit
    - term-structure IV
    - IV decay advantage
    """

    # Spot price
    spot_candidates = [r["stockPrice"] for r in strikes if r.get("stockPrice") is not None]
    if not spot_candidates:
        return []
    spot = float(spot_candidates[0])

    # Filter rows by expiration
    front_rows = [r for r in strikes if r["expirDate"] == front_exp]
    back_rows  = [r for r in strikes if r["expirDate"] == back_exp]

    # Map expiration DTE to core IV bucket
    front_dte = front_rows[0]["dte"]
    back_dte  = back_rows[0]["dte"]

    front_iv_term = map_expiration_to_iv(front_dte, term_structure)
    back_iv_term  = map_expiration_to_iv(back_dte, term_structure)

    # Build lookup for back expiration
    back_map = {
        normalize_strike(r["strike"]): r
        for r in back_rows
    }

    results = []

    for f in front_rows:

        strike = normalize_strike(f["strike"])
        if strike is None:
            continue

        # -------------------------
        # Moneyness filter (±15%)
        # -------------------------
        m = strike / spot
        if not (0.85 <= m <= 1.15):
            continue

        # Back leg
        back = back_map.get(strike)
        if not back:
            continue

        # Mid prices
        fm = extract_mid(f)
        bm = extract_mid(back)

        # Extrinsic
        fe = extrinsic_value(f)
        be = extrinsic_value(back)

        # Debit cost
        debit = bm - fm if fm is not None and bm is not None else None

        # Greeks
        vega_diff  = back.get("vega", 0)  - f.get("vega", 0)
        theta_diff = back.get("theta", 0) - f.get("theta", 0)
        gamma_diff = back.get("gamma", 0) - f.get("gamma", 0)

        # IV decay advantage
        iv_decay = None
        if front_iv_term and back_iv_term:
            iv_decay = back_iv_term - front_iv_term

        results.append({
            "Strike": strike,
            "Front Mid": fm,
            "Back Mid": bm,
            "Debit": debit,
            "Front Extrinsic": fe,
            "Back Extrinsic": be,
            "Extrinsic Ratio": (be / fe) if (fe and be) else None,
            "Vega Diff": vega_diff,
            "Theta Diff": theta_diff,
            "Gamma Diff": gamma_diff,
            "Front Term IV": front_iv_term,
            "Back Term IV": back_iv_term,
            "IV Decay": iv_decay,
        })

    return results

