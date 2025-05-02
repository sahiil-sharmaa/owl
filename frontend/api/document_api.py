import requests
import json
import streamlit as st
from urllib.parse import urljoin

URL = "http://backend:8000/document/"


def upload(file):

    try:
        endpoint = 'upload'
        url = urljoin(URL, endpoint)

        files = {"file": (file.name, file, file.type)}
        response = requests.post(url, files=files)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to upload file. Error: {response.status_code} - {json.loads(response.text)['detail']}")
            return None

    except Exception as e:
        st.error(f"An error occurred while uploading the file: {str(e)}")
        return None


def list_all():
    try:
        endpoint = 'list'
        url = urljoin(URL, endpoint)

        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch document list. Error: {response.status_code} - {json.loads(response.text)['detail']}")
            return []

    except Exception as e:
        st.error(f"An error occurred while fetching the document list: {str(e)}")
        return []


def delete(file_id):
    
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    data = {"id": file_id}

    try:
        endpoint = 'delete'
        url = urljoin(URL, endpoint)

        response = requests.post(url=url,headers=headers,json=data)
        if response.status_code == 200:
            return response.json()
        
        else:
            st.error(f"Failed to delete document. Error: {response.status_code} - {json.loads(response.text)['detail']}")
            
    except Exception as e:
        st.error(f"An error occurred while deleting the document: {str(e)}")
    
    return None


def build_context(file_ids: list[str]):
    
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    data = {"ids": file_ids}

    try:
        endpoint = 'build_context'
        url = urljoin(URL, endpoint)

        response = requests.post(url=url,headers=headers,json=data)
        if response.status_code == 200:
            return response.json()
        
        else:
            st.error(f"Failed to build context. Error: {response.status_code} - {json.loads(response.text)['detail']}")
            
    except Exception as e:
        st.error(f"An error occurred while sending file_ids to Server: {str(e)}")
    
    return None