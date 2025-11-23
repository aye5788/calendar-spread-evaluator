import requests
import streamlit as st

BASE_URL = "https://api.orats.io/datav2"
TOKEN = st.secrets["orats_api_key"]


class ORATSClient:

    def _get(self, endpoint, ticker):
        url = f"{BASE_URL}/{endpoint}?token={TOKEN}&ticker={ticker}"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json().get("data", [])
        return data

    # -------------------------
    # PUBLIC METHODS
    # -------------------------

    def get_strikes(self, ticker):
        return self._get("strikes", ticker)

    def get_cores(self, ticker):
        cores = self._get("cores", ticker)
        return cores[0] if cores else None

    def get_term_structure(self, ticker):
        """
        Pulls term structure info from 'cores' endpoint.
        Maps expirations to iv buckets.
        """
        core = self.get_cores(ticker)
        if not core:
            return None

        buckets = []
        for i in range(1, 5):
            iv_key = f"atmIvM{i}"
            dte_key = f"dtExM{i}"
            if core.get(iv_key) is not None and core.get(dte_key) is not None:
                buckets.append({
                    "iv": core[iv_key],
                    "dte": core[dte_key],
                    "bucket": f"M{i}"
                })

        return {
            "core": core,
            "buckets": buckets
        }

