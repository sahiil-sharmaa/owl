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

# Refresh document list if needed
if "documents" not in st.session_state:
    st.session_state.documents = doc_api.list_all()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None

#------------------- INITIALIZE SESSION STATE -----------------------------#









#------------------- UPLOADED DOCUMENTS -----------------------------#

documents = st.session_state.documents

with st.container(border= True):

    st.subheader("Uploaded Documents")
    # st.markdown("<br>", unsafe_allow_html=True)

    if documents:
        # Append each document in formatted_docs matrix
        formatted_docs = []

        for doc in documents:

            timestamp = datetime.fromisoformat(doc['uploaded_at'])
            formatted_timestamp = timestamp.strftime("%d %b %Y, %I:%M %p")

            current_doc = {
                'ID': str(doc['id']),
                'Name' : str(doc['name']),
                'Status' : "Embedded" if doc['is_active'] else "Not Embedded",
                'Uploaded' : formatted_timestamp
            }
            formatted_docs.append(current_doc)

        st.dataframe(formatted_docs,hide_index=True,key='uploaded_files')

    else:
        st.info('Library is empty, Uploaded documents will be shown here.', icon = ":material/error:")








#------------------- UPLOAD NEW DOCUMENT -----------------------------#


with st.container(border=True):

    st.subheader("Upload Document")

    added_files = st.file_uploader(
        label="Upload new Documents",
        label_visibility='hidden',
        type=["pdf", "docx"], 
        accept_multiple_files=True,
        key="file_uploader"
    )

    # add upload button
    upload_btn = st.button("Upload",icon = ":material/database_upload:")

    if upload_btn:  
        if added_files:
            with st.spinner("Uploading documents..."):
                
                success = 0
                for file in added_files:
                    upload_response = doc_api.upload(file)
                    
                    if upload_response:
                        success += 1
                        
                if success == len(added_files):
                    st.toast("All files were uploaded Successfully", icon=":material/check:")

                elif success < len(added_files):
                    st.toast("Upload Failed, some files were not uploaded", icon=":material/error:")

            # update session state with latest document list
            st.session_state.documents = doc_api.list_all()
                    
        else:
            st.toast("Minimum 1 file is needed to Upload", icon=":material/exclamation:")




#------------------------ NEW DELETE DOCS ----------------------------#

documents = st.session_state.documents 

if documents:
    
    # Document deletion form.

    with st.container(border=True):
    
        st.subheader("Delete Document from Library")
        st.markdown("<br>", unsafe_allow_html=True)

        # Create a checkbox for each document
        selected_docs = []
        for doc in documents:

            if doc['is_active'] == False:
                if st.checkbox(label=doc['name'], key=doc['id']):
                    selected_docs.append(doc)

        # Submit button
        delete = st.button("🗑️ Delete Selected")

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
