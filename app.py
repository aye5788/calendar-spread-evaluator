import streamlit as st
import pandas as pd

from modules.api import ORATSClient
from modules.calendars import build_calendar_pairs
from modules.scoring import score_calendar


st.set_page_config(page_title="ORATS Calendar Spread Evaluator", layout="wide")

st.title("📅 ORATS Calendar Spread Evaluator (Delayed Data)")


# -----------------------------
# INPUTS
# -----------------------------
ticker = st.text_input("Ticker", value="SLV")
scan = st.button("🔍 Scan")

client = ORATSClient()

if scan and ticker:
    st.write(f"Fetching strikes for **{ticker}**…")

    strikes = client.get_strikes(ticker)
    if not strikes:
        st.error("No strikes returned. Check ticker or API key.")
        st.stop()

    expirations = sorted(list(set([row["expirDate"] for row in strikes])))

    if len(expirations) < 2:
        st.error("Not enough expirations.")
        st.stop()

    st.success(f"Found {len(expirations)} expiration dates.")

    col1, col2 = st.columns(2)
    with col1:
        front_exp = st.selectbox("Front Expiration", expirations)
    with col2:
        back_exp = st.selectbox("Back Expiration", expirations, index=1)

    if st.button("📈 Build & Score Calendar Spreads"):

        # Pull term structure
        term_structure = client.get_term_structure(ticker)

        calendar_rows = build_calendar_pairs(
            strikes,
            front_exp,
            back_exp,
            term_structure
        )

        if not calendar_rows:
            st.warning("No matching strikes found.")
            st.stop()

        # Score them
        for r in calendar_rows:
            r["Score"] = score_calendar(r)

        df = pd.DataFrame(calendar_rows)
        df = df.sort_values("Score", ascending=False)

        st.subheader("📊 Calendar Spread Results")
        st.dataframe(df, width="stretch")

