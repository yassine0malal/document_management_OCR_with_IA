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

    def register(self, nom, email, password):
        try:
            response = requests.post(
                f"{self.base_url}/register",
                json={"nom": nom, "email": email, "password": password}
            )
            return response.json(), response.status_code
        except Exception as e:
            return {"detail": str(e)}, 500

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

    def upload_document(self, token, file_content, filename, avis_utilisateur=None):
        try:
            files = {"file": (filename, file_content)}  
            data = {"avis_utilisateur": avis_utilisateur} if avis_utilisateur else {}
            response = requests.post(
                f"{self.base_url}/documents/upload",
                headers=self.get_headers(token),
                files=files,
                data=data
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

    def update_document_category(self, token, doc_id, category=None, avis_utilisateur=None):
        try:
            data = {}
            if category: data["categorie"] = category
            if avis_utilisateur is not None: data["avis_utilisateur"] = avis_utilisateur
            
            response = requests.patch(
                f"{self.base_url}/documents/{doc_id}",
                headers=self.get_headers(token),
                json=data
            )
            return response.json(), response.status_code
        except Exception as e:
            return {"detail": str(e)}, 500

    def delete_document(self, token, doc_id):
        try:
            response = requests.delete(
                f"{self.base_url}/documents/{doc_id}",
                headers=self.get_headers(token)
            )
            return response.json(), response.status_code
        except Exception as e:
            return {"detail": str(e)}, 500

api_client = APIClient()
