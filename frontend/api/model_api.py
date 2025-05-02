import requests
import streamlit as st
from urllib.parse import urljoin

URL = "http://backend:8000/model/"

def get_language_models() -> list[str]:
    
    try:
        endpoint = 'version'
        url = urljoin(URL, endpoint)
        
        # fetch available models from backend
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch available language models. Error: {response.status_code} - {response.text}")
            return []

    except Exception as e:
        st.error(f"An error occurred while fetching the language model list: {str(e)}")
        return []


def get_embedding_models() -> list[str]:
    
    try:
        endpoint = 'embedding/version'
        url = urljoin(URL, endpoint)
        
        # fetch available models from backend
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch available embedding model versions. Error: {response.status_code} - {response.text}")
            return []

    except Exception as e:
        st.error(f"An error occurred while fetching the embedding model version list: {str(e)}")
        return []


def get_model_persona() -> list[str]:
    
    try:
        endpoint = 'persona'
        url = urljoin(URL, endpoint)
        
        # fetch available models from backend
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch available persona. Error: {response.status_code} - {response.text}")
            return []

    except Exception as e:
        st.error(f"An error occurred while fetching the persona list: {str(e)}")
        return []


