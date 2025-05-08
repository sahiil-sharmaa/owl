import streamlit as st
import api.model_api as model_api, api.document_api as doc_api
from commons import backend_log
from datetime import time


# Page title and config
st.set_page_config(page_title="FYND - Document Insights", page_icon="🔍", layout="wide")
st.title("⚙️ Preferences")
st.markdown("<br><br>", unsafe_allow_html=True)


#------------------- INITIALIZE SESSION STATE -----------------------------#

if "model" not in st.session_state:
    model_options = model_api.get_language_models()
    st.session_state.model = model_options[0]  # default to first model
else:
    model_options = model_api.get_language_models()

if "embedding_model" not in st.session_state:
    embedding_model_options = model_api.get_embedding_models()
    st.session_state.embedding_model = embedding_model_options[0]
else:
    embedding_model_options = model_api.get_embedding_models()

if "persona" not in st.session_state:
    persona_options = model_api.get_model_persona()
    persona_options = model_api.get_model_persona()
    st.session_state.persona = persona_options[0]
else:
    persona_options = model_api.get_model_persona()


if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None


#------- Define callback functions ---------#

def update_model():
    st.session_state.model = st.session_state["model_select"]

def update_embedding_model():
    st.session_state.embedding_model = st.session_state["embedding_model_select"]

def update_persona():
    st.session_state.persona = st.session_state["persona_select"]


# SET COLUMNS
col1, col2 = st.columns([2,1])

#------------------- Model Preferences -----------------------------#
col2.subheader("Model Preferences ")
col2.text("")

col2.selectbox(
    "Select Language Model",
    options=model_options,
    index=model_options.index(st.session_state.model),
    key="model_select",
    on_change=update_model
)
col2.text("")
col2.divider() 


#------------------- Embedding Model Preferences -----------------------------#
col2.subheader("Embedding Model Preferences ")
col2.text("")

col2.selectbox(
    "Select Embedding Model",
    options=embedding_model_options,
    index=embedding_model_options.index(st.session_state.embedding_model),
    key="embedding_model_select",
    on_change=update_embedding_model
)
col2.text("")
col2.divider() 

#------------------- Model Persona Preferences -----------------------------#
col2.subheader("Model Persona Preferences ")
col2.text("")

col2.selectbox(
    "Select Model Persona",
    options=persona_options,
    index=persona_options.index(st.session_state.persona),
    key="persona_select",
    on_change=update_persona
)

col2.divider() 


#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#

#------------------- EMBEDDED DOCUMENTS -----------------------------#

col1.subheader("Embedded Documents")
col1.text("")

# Fetch doc list from DB
documents = doc_api.list_all()
if documents:

    selected_docs = col1.multiselect(
        "Select Documents to build context",
        options=[doc['id'] for doc in documents],
        format_func=lambda x: next(doc['name'] for doc in documents if doc['id'] == x),
        default=[doc['id'] for doc in documents if doc['is_active'] == True],
        )

    col1.markdown("<br>", unsafe_allow_html=True)
    col1.divider()

    col1.text("Selected Documents")
    if selected_docs:
        for doc_id in selected_docs:
            doc_name = next(doc['name'] for doc in documents if doc['id'] == doc_id)
            col1.write(f"- {doc_name}")

    else:
        col1.error("No Document is selected, select atleast 1 document.",icon=":material/close:")

    if selected_docs:
        # build context from selected documents
        col1.info("Building context takes time, please wait after clicking build context button.", icon=":material/exclamation:")
        
        if col1.button("Build Context", icon=":material/construction:"):
            build_response = doc_api.build_context(selected_docs)
            if build_response:
                col1.success(f"{build_response["message"]}", icon=":material/check:")
            else:
                col1.error(f"Context Build Failed !", icon=":material/close:")

else:
    col1.error("No Document in Library, Add documents in library first", icon=":material/close:")






#------------------- SIDE BAR -----------------------------#

st.sidebar.header("Configuration Info")
st.sidebar.text(f"You can select which documents to embed by selecting from Embedded documents selector, The docs already uploaded in library will be visible here. You can add or remove embedded documents from here.")
st.sidebar.text("")
st.sidebar.text(f"Based on your requirements or how the AI is behaving you can select which model to use for conversation from model preferences.")
st.sidebar.text("")
st.sidebar.text(f"While embedding a set of documents, you can also select which embedding model to use, because certain language models work better with some specific embedding models. Currently only one embedding model is available.")
st.sidebar.text("")
st.sidebar.text(f"If you want your language model to behave in a certain way, you can also do that by selecting the persona of the model from model persona preferences.")
