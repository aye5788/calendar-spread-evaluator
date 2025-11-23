import requests
import streamlit as st

# Read from secrets
TOKEN = st.secrets["orats"]["api_key"]
BASE_URL = st.secrets["orats"]["base_url"]


class ORATSClient:
    """ORATS delayed-data REST client."""

    def _get(self, endpoint, ticker):
        """Internal GET wrapper that handles ORATS formats."""
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

    # ------------------------
    # PUBLIC ENDPOINT CALLS
    # ------------------------

    def get_strikes(self, ticker):
        """Strike chain."""
        return self._get("strikes", ticker)

    def get_cores(self, ticker):
        """Core data for term structure and overall vols."""
        data = self._get("cores", ticker)
        return data[0] if data else None

    def get_term_structure(self, ticker):
        """Extract term structure IVs from cores endpoint."""
        core = self.get_cores(ticker)
        if not core:
            return None

        return {
            "iv20d": core.get("iv20d"),
            "iv30d": core.get("iv30d"),
            "iv60d": core.get("iv60d"),
            "iv90d": core.get("iv90d"),
            "atmIvM1": core.get("atmIvM1"),
            "atmIvM2": core.get("atmIvM2"),
            "atmIvM3": core.get("atmIvM3"),
            "atmIvM4": core.get("atmIvM4"),
        }
