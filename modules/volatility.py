def compute_term_structure(summary):
    iv30 = summary.get("iv30d")
    iv60 = summary.get("iv60d")
    ex30 = summary.get("exErnIv30d")
    ex60 = summary.get("exErnIv60d")

    return {
        "iv_diff": (iv60 - iv30) if iv60 and iv30 else None,
        "ex_iv_diff": (ex60 - ex30) if ex60 and ex30 else None,
        "iv30": iv30,
        "iv60": iv60,
    }


def compute_skew(monies):
    vol25 = monies.get("vol25")
    vol50 = monies.get("vol50")
    vol75 = monies.get("vol75")

    return {
        "skew_25_75": (vol75 - vol25) if vol25 and vol75 else None,
        "atm_vs_wings": (
            vol50 - (vol25 + vol75) / 2 if vol25 and vol50 and vol75 else None
        ),
        "curvature": monies.get("deriv"),
        "slope": monies.get("slope"),
    }

