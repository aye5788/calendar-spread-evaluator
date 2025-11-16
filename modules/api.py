import requests
import streamlit as st

class ORATSClient:
    def __init__(self):
        self.token = st.secrets["orats"]["api_key"]
        self.base = st.secrets["orats"]["base_url"]  # https://api.orats.io/datav2

    def fetch(self, endpoint, params=None):
        if params is None:
            params = {}

        # ORATS DELAYED API REQUIRES token AS QUERY PARAM
        params["token"] = self.token

        url = f"{self.base}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    # ---- Endpoints ----

    def get_summaries(self, ticker):
        return self.fetch("summaries", {"ticker": ticker})

    def get_monies(self, ticker):
        return self.fetch("monies/implied", {"ticker": ticker})

    def get_strikes(self, ticker, expiry=None):
        params = {"ticker": ticker}
        if expiry:
            params["expirations"] = expiry
        return self.fetch("strikes", params)

    def get_expirations(self, ticker):
        data = self.get_strikes(ticker)
        expirations = sorted({item["expiration"] for item in data})
        return expirations

