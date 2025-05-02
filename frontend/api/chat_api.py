import requests, json, streamlit as st
from commons import backend_log


URL = "http://backend:8000/conversation/"


def send_message(session_id, question, model, persona):
    
    headers = {'accept': 'application/json','Content-Type': 'application/json'}

    data = {
        "question": question,
        "model": model,
        "persona" : persona
    }

    if session_id:
        data["session_id"] = session_id


    backend_log.info(f'The Payload for conversation is : {data}')

    try:
        
        response = requests.post(URL, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        
        else:
            backend_log.info(f'Chat API failed : {response.status_code} | {json.loads(response.text)['detail']}')
            st.error(f"API request failed with status code {response.status_code}: {json.loads(response.text)['detail']}")
            return None

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None
