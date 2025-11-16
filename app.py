import streamlit as st
from modules.api import ORATSClient
from modules.volatility import compute_term_structure, compute_skew
from modules.calendars import build_calendar
from modules.scoring import score_calendar

st.set_page_config(page_title="Calendar Spread Evaluator", layout="centered")
st.title("📈 Calendar Spread Evaluator (ORATS Delayed Data)")


@st.cache_data
def load_expirations(ticker: str):
    client = ORATSClient()
    return client.get_expirations(ticker)


ticker = st.text_input("Ticker", "SLV").upper().strip()

if ticker:
    try:
        expirations = load_expirations(ticker)
    except Exception as e:
        st.error(f"Error fetching expirations: {e}")
        st.stop()

    if not expirations:
        st.error("No expirations found for this ticker.")
        st.stop()

    st.subheader("Choose Expirations")

    front_exp = st.selectbox("Front Expiration", expirations, index=0)

    later_exps = [e for e in expirations if e > front_exp]
    if not later_exps:
        st.error("No back expirations available after selected front expiration.")
        st.stop()

    back_exp = st.selectbox("Back Expiration", later_exps, index=0)
else:
    st.stop()


if st.button("Evaluate"):
    client = ORATSClient()

    try:
        # ---- summaries (term structure) ----
        summaries = client.get_summaries(ticker)
        summary = summaries[0]
        ts = compute_term_structure(summary)

        # ---- monies implied (skew) ----
        monies_list = client.get_monies(ticker)
        monies = monies_list[0]
        skew = compute_skew(monies)

        # ---- strikes for each expiry ----
        front_chain = client.get_strikes(ticker, front_exp)
        back_chain = client.get_strikes(ticker, back_exp)

        # crude ATM = middle element
        front_opt = front_chain[len(front_chain) // 2]
        back_opt = back_chain[len(back_chain) // 2]

        cal = build_calendar(front_opt, back_opt)
        score = score_calendar(ts, skew, cal)

        st.subheader("📊 Calendar Score")
        st.json(score)

        st.subheader("📈 Term Structure Inputs")
        st.json(ts)

        st.subheader("📉 Skew / Vol Surface Inputs")
        st.json(skew)

        st.subheader("⚙️ Calendar Greeks / Pricing")
        st.json(cal)

    except Exception as e:
        st.error(f"Error evaluating calendar spread: {e}")

