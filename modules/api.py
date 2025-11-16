import requests
import streamlit as st

class ORATSClient:
    def __init__(self):
        self.base_url = st.secrets["orats"]["base_url"]
        self.token = st.secrets["orats"]["api_key"]


    def get_strikes(self, ticker: str):
        """Pull delayed-data strikes, which include expiration dates."""
        url = f"{self.base_url}/strikes"
        params = {"ticker": ticker, "token": self.token}

        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise Exception(
                f"ORATS error {response.status_code}: {response.text}"
            )

        return response.json()


