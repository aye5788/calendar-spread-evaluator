import streamlit as st
import requests

st.set_page_config(page_title="Calendar Spread Evaluator (ORATS)", layout="centered")

# -----------------------------
# SECRETS (matches your secrets.toml exactly)
# -----------------------------
ORATS_TOKEN = st.secrets["orats"]["api_key"]
BASE_URL = st.secrets["orats"]["base_url"]


# -----------------------------
# GET EXPIRATIONS
# -----------------------------
def get_expirations(ticker):
    """
    Pulls /strikes data and extracts unique expirDate fields.
    """
    url = f"{BASE_URL}/strikes"
    params = {"token": ORATS_TOKEN, "ticker": ticker.upper()}
    r = requests.get(url, params=params)
    r.raise_for_status()

    data = r.json()

    if "data" not in data:
        return []

    expirations = sorted({row["expirDate"] for row in data["data"]})
    return expirations


# -----------------------------
# GET STRIKES FOR SPECIFIC EXPIRATION
# -----------------------------
def get_strikes_for_expiry(ticker, expiration):
    """
    Fetch the entire strikes list then filter to the selected expirDate.
    """
    url = f"{BASE_URL}/strikes"
    params = {"token": ORATS_TOKEN, "ticker": ticker.upper()}
    r = requests.get(url, params=params)
    r.raise_for_status()

    data = r.json()

    if "data" not in data:
        return []

    filtered = [row for row in data["data"] if row["expirDate"] == expiration]
    return filtered


# -----------------------------
# UI
# -----------------------------
st.title("📈 Calendar Spread Evaluator (ORATS Delayed Data)")
st.write("Select ticker & expirations, then click **SCAN**.")

ticker = st.text_input("Ticker", "SLV")


# -----------------------------
# EXPIRATION DROPDOWNS
# -----------------------------
if ticker:
    try:
        expirations = get_expirations(ticker)

        if not expirations:
            st.warning("No expirations found for this ticker.")
            st.stop()

        col1, col2 = st.columns(2)

        with col1:
            front_exp = st.selectbox("Front expiration", expirations)

        with col2:
            # Choose next expiry automatically
            if len(expirations) > 1:
                back_default = expirations.index(front_exp) + 1
                back_default = min(back_default, len(expirations) - 1)
            else:
                back_default = 0

            back_exp = st.selectbox("Back expiration", expirations, index=back_default)

        st.info(f"Front: {front_exp}   |   Back: {back_exp}")

    except Exception as e:
        st.error(f"Error fetching expirations: {e}")
        st.stop()


# -----------------------------
# SCAN BUTTON
# -----------------------------
if st.button("SCAN"):
    st.write("Fetching strikes and matching…")

    try:
        front_strikes = get_strikes_for_expiry(ticker, front_exp)
        back_strikes = get_strikes_for_expiry(ticker, back_exp)

        if not front_strikes:
            st.error("No strikes found for the FRONT expiration.")
            st.stop()

        if not back_strikes:
            st.error("No strikes found for the BACK expiration.")
            st.stop()

        # Convert to dict by strike price
        fdict = {row["strike"]: row for row in front_strikes}
        bdict = {row["strike"]: row for row in back_strikes}

        # Match common strikes
        matched_strikes = sorted(set(fdict.keys()).intersection(bdict.keys()))

        if not matched_strikes:
            st.error("No common strikes between the selected expirations.")
            st.stop()

        st.success(f"Matched {len(matched_strikes)} strikes.")

                table = []
        for strike in matched_strikes:
            f = fdict[strike]
            b = bdict[strike]

            front_mid = f.get("mid")
            back_mid = b.get("mid")
            front_iv = f.get("iv")
            back_iv = b.get("iv")
            front_vega = f.get("vega")
            back_vega = b.get("vega")
            front_theta = f.get("theta")
            back_theta = b.get("theta")

            # --- SCORING ---
            debit = None
            iv_ratio = None
            vega_diff = None
            theta_diff = None
            score = None

            if front_mid and back_mid:
                debit = back_mid - front_mid

            if front_iv and back_iv and front_iv > 0:
                iv_ratio = back_iv / front_iv

            if front_vega and back_vega:
                vega_diff = back_vega - front_vega

            if front_theta and back_theta:
                theta_diff = front_theta - back_theta

            # Weighted score (0–100)
            if iv_ratio and debit and vega_diff is not None and theta_diff is not None:
                score = (
                    (iv_ratio * 40) +
                    ((1 / max(debit, 0.01)) * 35) +
                    (max(vega_diff, 0) * 15) +
                    (max(theta_diff, 0) * 10)
                )

            table.append({
                "Strike": strike,
                "Front Mid": front_mid,
                "Back Mid": back_mid,
                "Debit": debit,
                "Front IV": front_iv,
                "Back IV": back_iv,
                "IV Ratio": iv_ratio,
                "Vega Diff": vega_diff,
                "Theta Diff": theta_diff,
                "Score": round(score, 2) if score else None
            })

        # Sort by score
        table_sorted = sorted(
            table,
            key=lambda x: (x["Score"] is not None, x["Score"]),
            reverse=True
        )

        st.subheader("📊 Scored Calendar Spread Candidates")
        st.dataframe(table_sorted)


    except Exception as e:
        st.error(f"SCAN ERROR: {e}")
