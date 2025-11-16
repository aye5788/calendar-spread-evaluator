import requests
import streamlit as st

class ORATSClient:
    def __init__(self):
        self.api_key = st.secrets["orats"]["api_key"]
        self.base = st.secrets["orats"]["base_url"]   # https://api.orats.io/datav2
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def fetch(self, endpoint, params=None):
        """Call ORATS Delayed Data API."""
        url = f"{self.base}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    # ---- Valid Delayed Data Endpoints ----

    def get_summaries(self, ticker):
        return self.fetch("summaries", {"ticker": ticker})

    def get_monies(self, ticker):
        return self.fetch("monies/implied", {"ticker": ticker})

    def get_strikes(self, ticker, expiry=None):
        params = {"ticker": ticker}
        if expiry:
            params["expirations"] = expiry
        return self.fetch("strikes", params)

    # ---- Expirations must be derived from STRIKES ----

    def get_expirations(self, ticker):
        strikes = self.fetch("strikes", {"ticker": ticker})
        expirations = sorted({item["expiration"] for item in strikes})
        return expirations

