import streamlit as st
import pandas as pd
from modules.api import ORATSClient

st.set_page_config(page_title="Calendar Spread Evaluator", layout="wide")

st.title("📅 ORATS Calendar Spread Evaluator (Delayed Data)")
st.write("Scan and score calendar spreads using ORATS delayed-data endpoints.")

# -------------------------------
# INPUTS
# -------------------------------
ticker = st.text_input("Ticker", "SLV")

client = ORATSClient()

run_scan = st.button("🔍 Scan")

exp1 = None
exp2 = None
expirations = []

# -------------------------------
# RUN SCAN → GET EXPIRATIONS
# -------------------------------
if run_scan:
    st.write(f"Fetching strikes for **{ticker}**…")

    data = client.get_strikes(ticker)
    

    if not data:
        st.error("No data returned from ORATS /strikes endpoint.")
        st.stop()

    # Extract available expiration dates
    expirations = sorted(list({row["dte"] for row in data}))

    if len(expirations) < 2:
        st.error("Not enough expirations available to build a calendar spread.")
        st.stop()

    exp1 = st.selectbox("Front Month Expiration", expirations)
    exp2 = st.selectbox("Back Month Expiration", expirations, index=1)

    # Wait for user to choose expirations
    if exp1 and exp2:
        st.success(f"Selected: **{exp1} → {exp2}**")

        # Filter strikes
        front_rows = [r for r in data if r["dte"] == exp1]
        back_rows = [r for r in data if r["dte"] == exp2]

        strikes_front = {r["strike"] for r in front_rows}
        strikes_back = {r["strike"] for r in back_rows}
        matched_strikes = sorted(strikes_front.intersection(strikes_back))

        st.write(f"Matched strikes found: **{len(matched_strikes)}**")

        table = []

        for strike in matched_strikes:
            # Pull core option data
            f = client.get_core(ticker, exp1, strike)
            b = client.get_core(ticker, exp2, strike)

            front_mid = f.get("mid") if f else None
            back_mid  = b.get("mid") if b else None
            front_iv  = f.get("iv") if f else None
            back_iv   = b.get("iv") if b else None
            front_theta = f.get("theta") if f else None
            back_theta  = b.get("theta") if b else None
            front_vega  = f.get("vega") if f else None
            back_vega   = b.get("vega") if b else None

            # Debit
            debit = None
            if front_mid is not None and back_mid is not None:
                debit = back_mid - front_mid

            # Score (very simple version)
            score = None
            if front_iv and back_iv and back_iv > 0:
                score = (back_iv - front_iv) / back_iv

            table.append({
                "Strike": strike,
                "Front Mid": front_mid,
                "Back Mid": back_mid,
                "Debit": debit,
                "Front IV": front_iv,
                "Back IV": back_iv,
                "IV Ratio": (front_iv / back_iv) if front_iv and back_iv else None,
                "Vega Diff": (back_vega - front_vega) if back_vega and front_vega else None,
                "Theta Diff": (back_theta - front_theta) if back_theta and front_theta else None,
                "Score": score,
            })

        df = pd.DataFrame(table)

        st.subheader("📊 Calendar Spread Results")
        st.dataframe(df, use_container_width=True)
