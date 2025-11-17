import requests
import streamlit as st

class ORATSClient:
    def __init__(self):
        """
        Loads credentials from Streamlit secrets.
        """
        self.base_url = st.secrets["orats"]["base_url"]
        self.token = st.secrets["orats"]["api_key"]

    def get_strikes(self, ticker: str):
        """
        Returns full strike list + expiration dates for a ticker.
        NOTE: /strikes does NOT include mid/IV/greeks.
        """
        url = f"{self.base_url}/strikes"
        params = {
            "ticker": ticker,
            "token": self.token
        }
        resp = requests.get(url, params=params)

        if resp.status_code != 200:
            return None

        return resp.json()  # list of rows

    def get_core(self, ticker: str, expiration: str, strike: float):
        """
        Returns option mid, IV, greeks, etc. for a specific expiration + strike.
        """
        url = f"{self.base_url}/core"
        params = {
            "token": self.token,
            "ticker": ticker,
            "dte": expiration,
            "strike": strike
        }
        resp = requests.get(url, params=params)

        if resp.status_code != 200:
            return None

        data = resp.json()
        if not data:
            return None

        return data[0]  # core returns a list

