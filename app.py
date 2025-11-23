import streamlit as st
import pandas as pd

from modules.api import ORATSClient
from modules.calendars import build_calendar_pairs
from modules.scoring import score_calendar


st.set_page_config(page_title="ORATS Calendar Spread Evaluator", layout="wide")

st.title("📅 ORATS Calendar Spread Evaluator (Delayed Data)")
st.write("Scan and score calendar spreads using ORATS delayed-data endpoints.")


# ---------------------------------------
# TICKER INPUT
# ---------------------------------------

ticker = st.text_input("Ticker", value="SLV")

if st.button("🔍 Scan"):
    # Load strikes and store them so they persist across reruns
    client = ORATSClient()
    strikes = client.get_strikes(ticker)

    if not strikes:
        st.error("No strike data returned. Check ticker or ORATS token.")
        st.stop()

    st.session_state["strikes"] = strikes
    st.session_state["expirations"] = sorted(list(set([r["expirDate"] for r in strikes])))
    st.session_state["ticker"] = ticker


# ---------------------------------------
# IF WE HAVE STRIKES, SHOW EXPIRATION UI
# ---------------------------------------

if "strikes" in st.session_state:

    st.success(f"Found {len(st.session_state['expirations'])} expiration dates.")

    col1, col2 = st.columns(2)
    with col1:
        front_exp = st.selectbox(
            "Front Expiration",
            st.session_state["expirations"],
            key="front_exp"
        )
    with col2:
        back_exp = st.selectbox(
            "Back Expiration",
            st.session_state["expirations"],
            key="back_exp"
        )

    # ---------------------------------------
    # BUILD CALENDARS BUTTON
    # ---------------------------------------

    if st.button("📈 Build & Score Calendar Spreads"):

        strikes = st.session_state["strikes"]

        calendar_rows = build_calendar_pairs(strikes, front_exp, back_exp)

        if not calendar_rows:
            st.warning("No matching strikes found between chosen expirations.")
            st.stop()

        # Scoring
        for row in calendar_rows:
            row["Score"] = score_calendar(row)

        df = pd.DataFrame(calendar_rows).sort_values("Score", ascending=False)

        st.subheader("📊 Calendar Spread Results")
        st.dataframe(df, use_container_width=True)


