import requests
import streamlit as st

# --- READ SECRETS PROPERLY ---
TOKEN = st.secrets["orats"]["api_key"]
BASE_URL = st.secrets["orats"]["base_url"]


class ORATSClient:
    """Simple ORATS delayed-data client"""

    def _get(self, endpoint, ticker):
        """Internal fetch method"""
        url = f"{BASE_URL}/{endpoint}?token={TOKEN}&ticker={ticker}"
        r = requests.get(url)
        r.raise_for_status()
        raw = r.json()

        # ORATS sometimes returns list, sometimes {"data": [...]}
        if isinstance(raw, list):
            return raw
        if "data" in raw:
            return raw["data"]

        return []

    # ---------------------
    # PUBLIC METHODS
    # ---------------------

    def get_strikes(self, ticker):
        """Fetch strikes chain"""
        return self._get("strikes", ticker)

    def get_cores(self, ticker):
        """Fetch core data (term structure & vols)"""
        data = self._get("cores", ticker)
        return data[0] if data else None

    def get_term_structure(self, ticker):
        """Alias – extracted from cores"""
        core = self.get_cores(ticker)
        if not core:
            return None
        return {
            "iv20d": core.get("iv20d"),
            "iv30d": core.get("iv30d"),
            "iv60d": core.get("iv60d"),
            "iv90d": core.get("iv90d"),
        }

