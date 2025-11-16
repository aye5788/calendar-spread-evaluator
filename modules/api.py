import json
import requests
import streamlit as st


class ORATSClient:
    def __init__(self):
        # token and base_url come from Streamlit secrets
        self.token = st.secrets["orats"]["api_key"]
        self.base = st.secrets["orats"]["base_url"]  # e.g. https://api.orats.io/datav2

    def fetch(self, endpoint, params=None):
        """
        Generic ORATS Delayed Data API caller.
        Always passes ?token=... in the query string.
        """
        if params is None:
            params = {}

        # ORATS delayed API REQUIRES token as query param
        params["token"] = self.token

        url = f"{self.base}/{endpoint}"
        resp = requests.get(url, params=params)
        resp.raise_for_status()

        # Some ORATS responses may be plain JSON, some may nest under "data",
        # some might even be JSON strings. Handle all three safely.
        text = resp.text

        try:
            data = resp.json()
        except ValueError:
            data = json.loads(text)

        # If it's a dict with "data" key, unwrap
        if isinstance(data, dict) and "data" in data:
            inner = data["data"]
            if isinstance(inner, str):
                return json.loads(inner)
            return inner

        # If it's a JSON string, parse
        if isinstance(data, str):
            return json.loads(data)

        return data

    # -------------------------
    # ORATS endpoints we use
    # -------------------------

    def get_summaries(self, ticker: str):
        """
        Delayed summaries: /datav2/summaries?ticker=SLV&token=...
        """
        return self.fetch("summaries", {"ticker": ticker})

    def get_monies(self, ticker: str):
        """
        Monies Implied: /datav2/monies/implied?ticker=SLV&token=...
        """
        return self.fetch("monies/implied", {"ticker": ticker})

    def get_strikes(self, ticker: str, expiry: str | None = None):
        """
        Strikes: /datav2/strikes?ticker=SLV&token=...&expirations=YYYY-MM-DD
        """
        params = {"ticker": ticker}
        if expiry:
            params["expirations"] = expiry
        return self.fetch("strikes", params)

    def get_expirations(self, ticker: str):
        """
        Delayed API has no /expirations endpoint.
        We derive expirations from the strikes data.
        """
        strikes = self.get_strikes(ticker)
        expirations = sorted({item["expiration"] for item in strikes})
        return expirations

