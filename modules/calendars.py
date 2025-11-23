import numpy as np


def mid_price(row):
    """Compute mid price from bid/ask."""
    bid = row.get("callBidPrice")
    ask = row.get("callAskPrice")
    if bid is None or ask is None:
        return None
    return (bid + ask) / 2


def extract_iv(row):
    """Use ORATS surface IV (smvVol)."""
    return row.get("smvVol")


def moneyness_filter(row, underlying):
    """Return % moneyness."""
    strike = row.get("strike")
    if not strike or not underlying:
        return None
    return strike / underlying


def build_calendar_pairs(strikes, front_exp, back_exp, term_structure):
    """Full professional calendar pairing model."""

    front_rows = [r for r in strikes if r["expirDate"] == front_exp]
    back_rows = [r for r in strikes if r["expirDate"] == back_exp]
    back_map = {r["strike"]: r for r in back_rows}

    # Extract underlying from any strike
    underlying = None
    if strikes:
        underlying = strikes[0].get("spotPrice")

    results = []

    for f in front_rows:
        k = f["strike"]
        b = back_map.get(k)
        if b is None:
            continue

        fm = mid_price(f)
        bm = mid_price(b)

        if fm is None or bm is None:
            continue

        fv = extract_iv(f)
        bv = extract_iv(b)

        # Greeks
        fvga = f.get("vega")
        bvga = b.get("vega")
        fth = f.get("theta")
        bth = b.get("theta")

        vega_diff = (bvga - fvga) if (fvga is not None and bvga is not None) else None
        theta_diff = (bth - fth) if (fth is not None and bth is not None) else None

        # Term structure anchors
        iv_anchor = None
        if term_structure:
            iv_anchor = term_structure.get("iv30d")

        mn = moneyness_filter(f, underlying)

        results.append({
            "Strike": k,
            "Front Mid": fm,
            "Back Mid": bm,
            "Debit": bm - fm,
            "Front IV": fv,
            "Back IV": bv,
            "IV Ratio": (bv / fv) if fv and bv else None,
            "Vega Diff": vega_diff,
            "Theta Diff": theta_diff,
            "Moneyness": mn,
            "IV Anchor": iv_anchor,
        })

    return results
