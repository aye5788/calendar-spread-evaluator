import streamlit as st
import requests

st.set_page_config(page_title="ORATS Expiration Dropdown (Delayed Data)")

# --- Load secrets ---
ORATS_TOKEN = st.secrets["orats"]["api_key"]
BASE_URL = st.secrets["orats"]["base_url"]

# --- Function to get expiration dates ---
def get_expirations(ticker: str):
    url = f"{BASE_URL}/strikes?token={ORATS_TOKEN}&ticker={ticker}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        # ORATS returns {"data": [ { "expirDate": "YYYY-MM-DD", ... }, ... ]}
        expirations = sorted({item["expirDate"] for item in data["data"]})
        return expirations

    except Exception as e:
        st.error(f"Error fetching expirations: {e}")
        return []


# =============================
#           UI
# =============================

st.title("📅 ORATS Expiration Dropdown (Delayed Data)")
st.write("Select two expirations for calendar spread evaluation.")

ticker = st.text_input("Ticker", "SLV")

if ticker:
    expirations = get_expirations(ticker)

    if not expirations:
        st.warning("No expirations found for this ticker.")
    else:
        # 🔥 FIRST DROPDOWN (FRONT)
        front_exp = st.selectbox(
            "Front expiration:",
            expirations,
            key="front"
        )

        # 🔥 SECOND DROPDOWN (BACK)
        # Only show back expirations AFTER the front one
        valid_back_exps = [e for e in expirations if e > front_exp]

        if not valid_back_exps:
            st.warning("No later expirations available for a back leg.")
        else:
            back_exp = st.selectbox(
                "Back expiration:",
                valid_back_exps,
                key="back"
            )

            # Display chosen expirations
            st.success(f"Front: {front_exp} | Back: {back_exp}")
