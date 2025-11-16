def normalize(value, low, high):
    if value is None:
        return 0
    return max(0, min(1, (value - low) / (high - low)))


def score_calendar(ts, skew, cal):
    iv_score = normalize(ts["iv_diff"], -2, 8)
    ex_score = normalize(ts["ex_iv_diff"], -2, 8)
    skew_score = normalize(skew["slope"], -0.1, 0.1)
    vtr_score = normalize(cal["vega_theta_ratio"], 0, 4)
    debit_score = normalize(-cal["debit"], -5, 0)  # cheaper is better

    final = (
        0.25 * iv_score +
        0.20 * ex_score +
        0.15 * skew_score +
        0.20 * vtr_score +
        0.20 * debit_score
    )

    return {
        "iv_score": iv_score,
        "ex_score": ex_score,
        "skew_score": skew_score,
        "vtr_score": vtr_score,
        "debit_score": debit_score,
        "final": final,
    }
