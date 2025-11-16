import requests
import streamlit as st

@st.cache_data
def get_orats_base():
    return st.secrets["orats"]["base_url"]

@st.cache_data
def get_orats_token():
    return st.secrets["orats"]["api_key"]


class ORATSClient:
    def __init__(self):
        self.base = get_orats_base()
        self.token = get_orats_token()

    def fetch(self, endpoint, params=None):
        if params is None:
            params = {}

        # ALL delayed ORATS endpoints require token as query param
        params["token"] = self.token

        url = f"{self.base}/{endpoint}"

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_expirations(self, ticker):
        # Delayed API: /datav2/expirations?ticker=SLV&token=XXX
        return self.fetch("expirations", {"ticker": ticker})

    def get_summary(self, ticker):
        # Delayed API: /datav2/summaries?ticker=SLV&token=XXX
        data = self.fetch("summaries", {"ticker": ticker})
        return data[0] if isinstance(data, list) and data else None

    def get_strikes(self, ticker, expiry):
        # need dte from summary
        summary = self.get_summary(ticker)
        if not summary:
            return None

        dte = summary.get("dte")
        if dte is None:
            return None

        # Delayed strikes endpoint requires: ticker, dte, fields
        params = {
            "ticker": ticker,
            "dte": dte,
            "fields": "strike,callBid,callAsk,putBid,putAsk"
        }

        return self.fetch("strikes", params)

