import requests
import streamlit as st

class ORATSClient:
    def __init__(self):
        self.api_key = st.secrets["orats"]["api_key"]
        self.base = st.secrets["orats"]["base_url"]
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def fetch(self, endpoint, params=None):
        url = f"{self.base}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_summaries(self, ticker):
        return self.fetch("summaries", {"tickers": ticker})

    def get_monies(self, ticker):
        return self.fetch("monies", {"tickers": ticker})

    def get_strikes(self, ticker, expiry):
        return self.fetch("strikes", {"tickers": ticker, "expirations": expiry})

    def get_expirations(self, ticker):
        return self.fetch("expirations", {"tickers": ticker})
