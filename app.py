import streamlit as st
from modules.api import ORATSClient

st.set_page_config(page_title="ORATS Expiration Dropdown")

st.title("📅 ORATS Expiration Dropdown (Delayed Data)")
st.write("Simple test: Pull expirations for any ticker using `/strikes` delayed data.\n")

ticker = st.text_input("Ticker", "SLV")

client = ORATSClient()

if ticker:
    try:
        expirations = client.get_expirations(ticker)

        if not expirations:
            st.warning("No expirations found for this ticker.")
        else:
            selected_exp = st.selectbox("Select an expiration:", expirations)
            st.success(f"Selected expiration: **{selected_exp}**")

    except Exception as e:
        st.error(str(e))

