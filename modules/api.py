import json
import requests
import streamlit as st

class ORATSClient:
    def __init__(self):
        self.token = st.secrets["orats"]["api_key"]
        self.base = st.secrets["orats"]["base_url"]

    def fetch(self, endpoint, params=None):
        if params is None:
            params = {}

        params["token"] = self.token
        url = f"{self.base}/{endpoint}"

        response = requests.get(url, params=params)
        response.raise_for_status()

        # ORATS sometimes returns a JSON STRING; we must parse it manually.
        try:
            parsed = response.json()
        except ValueError:
            # Raw string → must load manually
            parsed = json.loads(response.text)

        # Some endpoints wrap data under "data": "..."
        if isinstance(parsed, dict) and "data" in parsed:
            # data may again be a JSON string
            raw = parsed["data"]
            if isinstance(raw, str):
                return json.loads(raw)
            else:
                return raw

        # If parsed is already a list/dict → return as is
        return parsed

