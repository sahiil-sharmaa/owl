import streamlit as st
import api.model_api as model_api, api.document_api as doc_api
from commons import backend_log
from datetime import time


# Page title and config
st.set_page_config(page_title="FYND - Document Insights", page_icon="🔍", layout="wide")
st.title("⚙️ Configuration")
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
        if col1.button("Build Context and wait ...", icon=":material/construction:"):
            build_response = doc_api.build_context(selected_docs)
            if build_response:
                col1.success(f"{build_response["message"]}", icon=":material/check:")
            else:
                col1.error(f"Context Build Failed !", icon=":material/close:")

else:
    col1.error("No Document in Library, Add documents in library first", icon=":material/close:")

















#------------------- SIDE BAR -----------------------------#

st.sidebar.header("Document Upload Info")
st.sidebar.text(f"The first panel displays all the files currently uploaded, and you can click the 'Refresh Files' button to update the list whenever needed.")
st.sidebar.text("")
st.sidebar.text(f"The second panel lets you delete any uploaded file by selecting it from a dropdown and clicking the 'Delete File' button, permanently removing it from the server.")
st.sidebar.text("")
st.sidebar.text(f"The third panel allows you to upload new files by selecting one or multiple files from your device and clicking the 'Upload Files' button to add them to the server.")
