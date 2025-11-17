import requests
import streamlit as st


class ORATSClient:
    def __init__(self):
        cfg = st.secrets["orats"]
        self.base_url = cfg["base_url"]
        self.token = cfg["api_key"]

    def get_strikes(self, ticker: str):
        """Fetch the FULL strike chain list (not nested under 'data')."""
        url = f"{self.base_url}/strikes?ticker={ticker}&token={self.token}"
        resp = requests.get(url)
        resp.raise_for_status()

        raw = resp.json()

        # raw is already the list based on your screenshots
        if isinstance(raw, list):
            return raw

        # fallback if ORATS wraps it in "data" someday
        if "data" in raw:
            return raw["data"]

        return []

