import streamlit as st
import pandas as pd

from modules.api import ORATSClient
from modules.calendars import build_calendar_pairs
from modules.scoring import score_calendar


st.set_page_config(page_title="ORATS Calendar Spread Evaluator", layout="wide")

st.title("📅 ORATS Calendar Spread Evaluator (Delayed Data)")
st.write("Scan and score calendar spreads using ORATS delayed-data endpoints.")


# -------------------------------
# INPUT AREA
# -------------------------------
ticker = st.text_input("Ticker", value="SLV")
scan = st.button("🔍 Scan")


if scan and ticker:
    st.write(f"Fetching strikes for **{ticker}**…")

    client = ORATSClient()
    strikes = client.get_strikes(ticker)

    if not strikes:
        st.error("No strike data returned. Check ticker or ORATS token.")
        st.stop()

    # ---------------------------
    # Pull available expirations
    # ---------------------------
    expirations = sorted(list(set([row["expirDate"] for row in strikes])))

    if len(expirations) < 2:
        st.error("Not enough expirations to build calendars.")
        st.stop()

    st.success(f"Found {len(expirations)} expiration dates.")

    # ---------------------------
    # Select expirations
    # ---------------------------
    col1, col2 = st.columns(2)
    with col1:
        front_exp = st.selectbox("Front Expiration", expirations, index=0)
    with col2:
        back_exp = st.selectbox("Back Expiration", expirations, index=1)

    if st.button("📈 Build & Score Calendar Spreads"):
        calendar_rows = build_calendar_pairs(strikes, front_exp, back_exp)

        if not calendar_rows:
            st.warning("No matching strikes found between chosen expirations.")
            st.stop()

        # Add score column
        for row in calendar_rows:
            row["Score"] = score_calendar(row)

        # Convert to DataFrame
        df = pd.DataFrame(calendar_rows)
        df = df.sort_values("Score", ascending=False)

        st.subheader("📊 Calendar Spread Results")
        st.dataframe(df, use_container_width=True)


