import streamlit as st
import api.document_api as doc_api
import api.model_api as model_api
from commons import backend_log
from datetime import datetime


# Page title and config
st.set_page_config(page_title="FYND - Beautiful Insights", page_icon="🔍", layout="wide")
st.title("📁 Library")
st.markdown("<br>", unsafe_allow_html=True)



#------------------- INITIALIZE SESSION STATE -----------------------------#

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



#------------------- UPLOADED DOCUMENTS -----------------------------#

st.subheader("Uploaded Documents")
st.markdown("<br>", unsafe_allow_html=True)

# check if doc list is present in session
if "documents" not in st.session_state:

    # Fetch doc list from DB
    st.session_state.documents = doc_api.list_all()


# display docs present in library (uploaded docs)
documents = st.session_state.documents
if documents:

    # Append each document in formated_docs matrix
    formated_docs = []

    for doc in documents:

        timestamp = datetime.fromisoformat(doc['uploaded_at'])
        formatted_timestamp = timestamp.strftime("%d %b %Y, %I:%M %p")

        current_doc = {
            'ID': str(doc['id']),
            'Name' : str(doc['name']),
            'Status' : "Embedded" if doc['is_active'] else "Not Embedded",
            'Uploaded' : formatted_timestamp
        }
        formated_docs.append(current_doc)

    st.dataframe(formated_docs,hide_index=True,key='uploaded_files')

else:
    st.info("No Document to show, Upload new Documents from below", icon=":material/exclamation:")

# refresh and fetch docs list again if needed.
if st.button("Refresh Document List",icon=":material/refresh:"):
    with st.spinner("Refreshing..."):
        st.session_state.documents = doc_api.list_all()

# Panel Ended
st.divider() 


#------------------- UPLOAD NEW DOCUMENT -----------------------------#

st.subheader("Upload Document")
added_files = st.file_uploader(
    label="Upload new Documents",
    label_visibility='hidden',
    type=["pdf", "docx"], 
    accept_multiple_files=True,
    key="file_uploader"
)


if added_files:
    if st.button("Upload All"):
        with st.spinner("Uploading documents..."):
            
            success = 0
            for file in added_files:
                upload_response = doc_api.upload(file)
                
                if upload_response:
                    success += 1
                    
            if success == len(added_files):
                st.success(f"All files were uploaded Successfully")
            
            elif success < len(added_files):
                st.error(f"Upload Failed, some files were not uploaded")

            # Refresh document list from backend
            st.session_state.documents = doc_api.list_all()
            st.info("Refresh Document list after uploading new files", icon=":material/exclamation:")

# Panel Ended
st.divider() 

#------------------------ NEW DELETE DOCS ----------------------------#


if documents:
    
    # Document deletion form.

    with st.form("delete_form"):
    
        st.subheader("Delete Document from Library")
        st.markdown("<br>", unsafe_allow_html=True)

        # Create a checkbox for each document
        selected_docs = []
        for doc in documents:

            if doc['is_active'] == False:
                if st.checkbox(label=doc['name'], key=doc['id']):
                    selected_docs.append(doc)

        # Submit button
        delete = st.form_submit_button("🗑️ Delete Selected")

    # Handle deletion
    if delete:
        with st.spinner("Deleting..."):
            
            responses = []
            success = 0 

            for doc in selected_docs:
                delete_response = doc_api.delete(doc['id'])
            
                if delete_response:
                    success += 1    
                    
            if success == len(selected_docs):
                st.success(f"All Documents deleted successfully.")
            
            elif success < len(selected_docs):
                st.error(f"Document deletion failed, some documents were not deleted!")


            # refresh list, and update session list.
            st.session_state.documents = doc_api.list_all() 
            st.info("Refresh file list after delete", icon=":material/exclamation:")
        





#------------------- DELETE DOCUMENT -----------------------------#

# if docs are saved - show option to delete
#! add permission check later 
# if st.session_state.superuser and documents:

# st.subheader("Delete Document from Library")
# st.markdown("<br>", unsafe_allow_html=True)

# if documents:     
#     selected_file_id = st.selectbox(
#         "Select from dropdown",
#         label_visibility="visible",
#         options=[doc['id'] for doc in documents],
#         format_func=lambda x: next(doc['name'] for doc in documents if doc['id'] == x)
#     )

#     if st.button("Delete Selected Document",icon=":material/delete:"):
#         with st.spinner("Deleting..."):            
            
#             delete_response = doc_api.delete(selected_file_id)
            
#             if delete_response:
#                 st.success(f"Document with ID {selected_file_id} deleted successfully.")

#                 # refresh list, and update session list.
#                 st.session_state.documents = doc_api.list_all() 
#             else:
#                 st.error(f"Failed to delete document with ID {selected_file_id}.")
            
#             st.info("Refresh file list after delete", icon=":material/exclamation:")
# else:
#     st.error("No Document to delete.", icon=":material/close:")


#------------------- SIDE BAR -----------------------------#

st.sidebar.header("Document Upload Info")
st.sidebar.text(f"The first panel displays all the files currently uploaded, and you can click the 'Refresh Files' button to update the list whenever needed.")
st.sidebar.text("")
st.sidebar.text(f"The second panel lets you delete any uploaded file by selecting it from a dropdown and clicking the 'Delete File' button, permanently removing it from the server.")
st.sidebar.text("")
st.sidebar.text(f"The third panel allows you to upload new files by selecting one or multiple files from your device and clicking the 'Upload Files' button to add them to the server.")
