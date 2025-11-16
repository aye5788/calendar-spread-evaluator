import requests
import streamlit as st

class ORATSClient:
    def __init__(self):
        self.base_url = "https://api.orats.io/datav2"
        self.token = st.secrets["orats"]["api_key"]

    def get_expirations(self, ticker: str):
        """
        Pull all expirations using /strikes.
        We extract unique 'expirDate' entries.
        """
        url = f"{self.base_url}/strikes"
        params = {
            "token": self.token,
            "ticker": ticker.upper()
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise Exception(f"ORATS error {response.status_code}: {response.text}")

        data = response.json()

        if "data" not in data:
            return []

        expirations = sorted({item["expirDate"] for item in data["data"]})
        return expirations


