import streamlit as st
from modules.api import ORATSClient

st.set_page_config(page_title="Expiration Dropdown Test")

st.title("🔽 ORATS Expiration Dropdown (Delayed Data)")
st.caption("Simple test: Pull expirations for any ticker using /strikes")

client = ORATSClient()

ticker = st.text_input("Ticker", value="SLV").upper().strip()

if ticker:
    try:
        expirations = client.get_expirations(ticker)

        if expirations:
            chosen = st.selectbox("Available Expirations", expirations)
            st.success(f"Selected expiration: {chosen}")
        else:
            st.warning("No expirations found for this ticker.")

    except Exception as e:
        st.error(f"Error: {e}")

