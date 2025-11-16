import streamlit as st
from modules.api import ORATSClient
from modules.volatility import compute_term_structure, compute_skew
from modules.calendars import build_calendar
from modules.scoring import score_calendar

st.title("📈 Calendar Spread Evaluator (ORATS Data)")

# --------------------------
# Load Expirations (Cached)
# --------------------------
@st.cache_data
def load_expirations(ticker):
    client = ORATSClient()
    data = client.get_expirations(ticker)
    # Extract expiration strings
    expirations = sorted([item["expiration"] for item in data])
    return expirations


# --------------------------
# Ticker Input
# --------------------------
ticker = st.text_input("Ticker", "SLV").upper()

# Load expirations only when ticker exists
if ticker:
    expirations = load_expirations(ticker)

    if not expirations:
        st.error("No expirations returned by ORATS for this ticker.")
        st.stop()

    # --------------------------
    # Dropdowns for expirations
    # --------------------------
    st.subheader("Choose Expirations")
    front_exp = st.selectbox("Front Expiration", expirations, index=0)
    # Back month must be AFTER front month
    back_candidates = [e for e in expirations if e > front_exp]
    if not back_candidates:
        st.error("No back expirations available after the selected front expiration.")
        st.stop()
    back_exp = st.selectbox("Back Expiration", back_candidates, index=0)

else:
    st.stop()


# --------------------------
# Evaluate Button
# --------------------------
if st.button("Evaluate"):
    client = ORATSClient()

    # Fetch summary (term structure)
    sum_data = client.get_summaries(ticker)
    if not sum_data:
        st.error("No summary data from ORATS.")
        st.stop()
    summary = sum_data[0]

    ts = compute_term_structure(summary)

    # Fetch surface (monies)
    monies_data = client.get_monies(ticker)
    if not monies_data:
        st.error("No volatility surface (monies) returned by ORATS.")
        st.stop()
    monies = monies_data[0]

    skew = compute_skew(monies)

    # Fetch strike chains
    front_chain_data = client.get_strikes(ticker, front_exp)
    back_chain_data = client.get_strikes(ticker, back_exp)

    if not front_chain_data or not back_chain_data:
        st.error("Strike data missing for one or both expirations.")
        st.stop()

    # Use ATM strike — ORATS returns all strikes; we pick the middle
    front_chain = front_chain_data[len(front_chain_data)//2]
    back_chain = back_chain_data[len(back_chain_data)//2]

    cal = build_calendar(front_chain, back_chain)
    score = score_calendar(ts, skew, cal)

    # --------------------------
    # Output Results
    # --------------------------
    st.subheader("📊 Score Results")
    st.write(score)

    st.subheader("📈 Term Structure")
    st.write(ts)

    st.subheader("📉 Skew / Surface")
    st.write(skew)

    st.subheader("⚙️ Calendar Greeks")
    st.write(cal)


