import requests
import streamlit as st

class ORATSClient:
    def __init__(self):
        self.base = st.secrets["orats"]["base_url"]
        self.token = st.secrets["orats"]["api_key"]

    # -----------------------------
    # VALID DELAYED ENDPOINT: /strikes
    # -----------------------------
    def get_strikes(self, ticker: str):
        url = f"{self.base}/strikes"
        params = {
            "ticker": ticker,
            "token": self.token
        }
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()

    # -----------------------------
    # VALID DELAYED ENDPOINT: /summaries
    # -----------------------------
    def get_summary(self, ticker: str, expiration: str):
        url = f"{self.base}/summaries"
        params = {
            "ticker": ticker,
            "token": self.token
        }
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        # filter summary for the expiration
        summaries = [d for d in data if d.get("expirDate") == expiration]

        if not summaries:
            return None

        return summaries[0]

