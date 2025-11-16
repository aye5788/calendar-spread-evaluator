import requests
import streamlit as st

class ORATSClient:
    def __init__(self):
        self.base_url = "https://api.orats.io/datav2"
        self.token = st.secrets["ORATS_TOKEN"]

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


