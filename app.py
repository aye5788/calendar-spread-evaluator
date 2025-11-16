import streamlit as st
from modules.api import ORATSClient

st.set_page_config(page_title="Calendar Spread Evaluator", layout="wide")

st.title("📉 Calendar Spread Evaluator\n(ORATS Delayed Data)")

ticker = st.text_input("Ticker", value="SLV")

client = ORATSClient()

@st.cache_data
def load_expirations(ticker):
    data = client.get_expirations(ticker)
    # API returns list like [{"expiration": "2025-01-17"}, ...]
    try:
        return sorted([item["expiration"] for item in data])
    except Exception:
        return []

expirations = []
if ticker:
    try:
        expirations = load_expirations(ticker)
    except Exception as e:
        st.error(f"Error fetching expirations: {e}")

if expirations:
    front_exp = st.selectbox("Front Expiration", expirations)
    back_exp = st.selectbox("Back Expiration", expirations)
else:
    st.warning("No expirations returned for this ticker.")
    st.stop()

if st.button("Evaluate"):
    st.subheader("Raw Strike Data (Delayed)")

    try:
        strikes = client.get_strikes(ticker, front_exp)
        st.write(strikes)
    except Exception as e:
        st.error(f"Error loading strike data: {e}")


