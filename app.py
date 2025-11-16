import streamlit as st
from modules.api import ORATSClient

st.set_page_config(page_title="ORATS Expiration Dropdown", layout="centered")

st.title("📅 ORATS Expiration Dropdown (Delayed Data)")
st.write("Simple test: Pull expirations for any ticker using `/strikes` delayed data.")

ticker = st.text_input("Ticker", "SLV")

client = ORATSClient()

if ticker:
    try:
        strikes = client.get_strikes(ticker.upper())

        if not strikes:
            st.warning("No data returned from ORATS for this ticker.")
        else:
            # Extract unique expiration dates
            expirations = sorted({item["expiration"] for item in strikes})

            if expirations:
                selected_exp = st.selectbox("Select Expiration", expirations)
                st.success(f"Selected expiration: {selected_exp}")
            else:
                st.warning("No expirations found for this ticker.")

    except Exception as e:
        st.error(f"Error fetching expirations: {e}")
