import streamlit as st
from modules.api import ORATSClient
from modules.volatility import compute_term_structure, compute_skew
from modules.calendars import build_calendar
from modules.scoring import score_calendar

st.title("📈 Calendar Spread Evaluator (ORATS Data)")

ticker = st.text_input("Ticker", "SLV")
front_exp = st.text_input("Front Expiration (YYYY-MM-DD)")
back_exp = st.text_input("Back Expiration (YYYY-MM-DD)")

if st.button("Evaluate"):
    client = ORATSClient()

    summaries = client.get_summaries(ticker)[0]
    ts = compute_term_structure(summaries)

    monies = client.get_monies(ticker)[0]
    skew = compute_skew(monies)

    front_chain = client.get_strikes(ticker, front_exp)[0]
    back_chain = client.get_strikes(ticker, back_exp)[0]
    cal = build_calendar(front_chain, back_chain)

    score = score_calendar(ts, skew, cal)

    st.subheader("Score Results")
    st.write(score)

    st.subheader("Term Structure")
    st.write(ts)

    st.subheader("Skew / Surface")
    st.write(skew)

    st.subheader("Calendar Greeks")
    st.write(cal)

