def extract_option(chain):
    return {
        "mid": (chain["bid"] + chain["ask"]) / 2,
        "vega": chain["vega"],
        "theta": chain["theta"],
        "iv": chain["smvVol"],
    }


def build_calendar(front_chain, back_chain):
    front = extract_option(front_chain)
    back = extract_option(back_chain)

    debit = back["mid"] - front["mid"]
    net_vega = back["vega"] - front["vega"]
    net_theta = back["theta"] + front["theta"]  # both negative

    vtr = None
    if net_theta != 0:
        vtr = net_vega / abs(net_theta)

    return {
        "debit": debit,
        "net_vega": net_vega,
        "net_theta": net_theta,
        "vega_theta_ratio": vtr,
    }
