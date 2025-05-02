from commons import backend_log
import streamlit as st
from api import model_api, document_api, chat_api


# Page title and config
st.set_page_config(page_title="FYND - Document Insights", page_icon="🔍",layout="wide")
st.title("🔍 FYND - Document Insights")
st.markdown("<br><br>", unsafe_allow_html=True)


# --- Initialize session state with default values ---
if "model" not in st.session_state:
    model_options = model_api.get_language_models()
    st.session_state.model = model_options[0]  # default to first model

if "embedding_model" not in st.session_state:
    embedding_model_options = model_api.get_embedding_models()
    st.session_state.embedding_model = embedding_model_options[0]

if "persona" not in st.session_state:
    persona_options = model_api.get_model_persona()
    st.session_state.persona = persona_options[0]

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None



backend_log.info(f' Session state is  : {st.session_state}')
backend_log.info(f' Session model is  : {st.session_state.model}')



for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Query:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Generating response..."):
        response = chat_api.send_message(
            st.session_state.session_id,
            prompt,
            st.session_state.model,
            st.session_state.persona,
        )
        
        if response:
            st.session_state.session_id = response.get('session_id')
            st.session_state.messages.append({"role": "assistant", "content": response['answer']})
            
            with st.chat_message("assistant"):
                st.markdown(response['answer'])
                
                with st.expander("Details"):
                    st.subheader("Generated Answer")
                    st.code(response['answer'])
                    st.subheader("Session ID")
                    st.code(response['session_id'])
        else:
            st.error("Failed to get a response from the API. Please try again.")
