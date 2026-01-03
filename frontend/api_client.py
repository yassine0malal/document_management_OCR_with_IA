import requests
import streamlit as st

class APIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def get_headers(self, token=None):
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def login(self, username, password):
        try:
            response = requests.post(
                f"{self.base_url}/login",
                data={"username": username, "password": password}
            )
            try:
                return response.json(), response.status_code
            except Exception as json_err:
                print(f"DEBUG: JSON decode error. Response text: {response.text}")
                return {"detail": f"Invalid JSON response: {response.text[:100]}"}, response.status_code
        except Exception as e:
            return {"detail": str(e)}, 500

    def get_me(self, token):
        try:
            response = requests.get(
                f"{self.base_url}/me",
                headers=self.get_headers(token)
            )
            return response.json(), response.status_code
        except Exception as e:
            return {"detail": str(e)}, 500

    def upload_document(self, token, file_content, filename):
        try:
            files = {"file": (filename, file_content)}
            response = requests.post(
                f"{self.base_url}/documents/upload",
                headers=self.get_headers(token),
                files=files
            )
            return response.json(), response.status_code
        except Exception as e:
            return {"detail": str(e)}, 500

    def get_documents(self, token):
        try:
            response = requests.get(
                f"{self.base_url}/documents",
                headers=self.get_headers(token)
            )
            return response.json(), response.status_code
        except Exception as e:
            return {"detail": str(e)}, 500

    def get_stats(self, token):
        try:
            response = requests.get(
                f"{self.base_url}/documents/stats",
                headers=self.get_headers(token)
            )
            return response.json(), response.status_code
        except Exception as e:
            return {"detail": str(e)}, 500

api_client = APIClient()
