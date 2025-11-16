import numpy as np

def compute_term_structure(summary):
    iv30 = summary["iv30d"]
    iv60 = summary["iv60d"]
    ex30 = summary["exErnIv30d"]
    ex60 = summary["exErnIv60d"]

    return {
        "iv_diff": iv60 - iv30,
        "ex_iv_diff": ex60 - ex30,
        "iv30": iv30,
        "iv60": iv60
    }

def compute_skew(monies):
    vol25 = monies["vol25"]
    vol50 = monies["vol50"]
    vol75 = monies["vol75"]

    return {
        "skew_25_75": vol75 - vol25,
        "atm_vs_wings": vol50 - (vol25 + vol75)/2,
        "curvature": monies["deriv"],
        "slope": monies["slope"]
    }
