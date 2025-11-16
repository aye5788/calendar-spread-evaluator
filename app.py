import streamlit as st
from modules.api import ORATSClient
from modules.volatility import compute_term_structure, compute_skew
from modules.calendars import build_calendar
from modules.scoring import score_calendar

st.title("📈 Calendar Spread Evaluator (ORATS Delayed Data)")


# --------------------------
# Cache expiration loading
# --------------------------
@st.cache_data
def load_expirations(ticker):
    client = ORATSClient()
    return client.get_expirations(ticker)


# --------------------------
# UI Inputs
# --------------------------
ticker = st.text_input("Ticker", "SLV").upper()

if ticker:
    expirations = load_expirations(ticker)

    if not expirations:
        st.error("No expirations found for this ticker.")
        st.stop()

    st.subheader("Choose Expirations")
    front_exp = st.selectbox("Front Expiration", expirations, index=0)
    back_exp = st.selectbox(
        "Back Expiration",
        [e for e in expirations if e > front_exp],
        index=0
    )
else:
    st.stop()


# --------------------------
# RUN EVALUATION
# --------------------------
if st.button("Evaluate"):
    client = ORATSClient()

    # Summaries
    summary_data = client.get_summaries(ticker)
    summary = summary_data[0]
    ts = compute_term_structure(summary)

    # Monies Implied
    monies_data = client.get_monies(ticker)
    monies = monies_data[0]
    skew = compute_skew(monies)

    # Strikes (full chain per expiration)
    front_chain = client.get_strikes(ticker, front_exp)
    back_chain = client.get_strikes(ticker, back_exp)

    # Choose ATM-ish (middle of list)
    front_opt = front_chain[len(front_chain)//2]
    back_opt = back_chain[len(back_chain)//2]

    cal = build_calendar(front_opt, back_opt)
    score = score_calendar(ts, skew, cal)

    # DISPLAY
    st.subheader("📊 Score Results")
    st.write(score)

    st.subheader("📈 Term Structure")
    st.write(ts)

    st.subheader("📉 Skew / Vol Surface")
    st.write(skew)

    st.subheader("⚙️ Calendar Greeks")
    st.write(cal)


