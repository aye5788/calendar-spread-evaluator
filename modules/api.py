import requests
import streamlit as st

class ORATSClient:
    def __init__(self):
        self.base = st.secrets["orats"]["base_url"]     # https://api.orats.io/datav2
        self.token = st.secrets["orats"]["api_key"]

    def get_strikes(self, ticker: str):
        """Fetch full strikes chain & greeks for the ticker."""
        url = f"{self.base}/strikes"
        params = {
            "ticker": ticker,
            "token": self.token
        }

        r = requests.get(url, params=params)
        r.raise_for_status()
        return r.json()

    def get_expirations(self, ticker: str):
        """
        Extract unique expiration dates from /strikes.
        This is the ONLY valid way in ORATS Delayed Data.
        """
        strikes = self.get_strikes(ticker)

        expirations = {
            row["expirDate"]
            for row in strikes
            if "expirDate" in row
        }

        return sorted(list(expirations))


