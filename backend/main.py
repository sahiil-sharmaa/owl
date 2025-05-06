from fastapi import FastAPI, File, UploadFile, HTTPException
from schema import *

import os
import uuid
import shutil

from utils import document, chat
from commons import db_dependency, Base, engine, backend_log

# initiate App
app = FastAPI()

# Create Tables in PostgresDB if they already dont exist
Base.metadata.create_all(bind=engine)



@app.get("/model/version", response_model=list[str])
def get_model_names():

    return [model.value for model in ModelName]

@app.get("/model/embedding/version", response_model=list[str])
def get_model_names():
    return [model.value for model in EmbeddingModelName]

@app.get("/model/persona", response_model=list[str])
def get_persona():
    return [persona.value for persona in ModelPersona]






@app.post("/conversation", response_model=QueryResponse)
def conversation(request: QueryInput, db : db_dependency):
    
    backend_log.info(f"Request intercepted : Session ID: {request.session_id}, User Query: {request.question}, Model: {request.model}")
    
    
    session_id: uuid.UUID | None = request.session_id

    if not session_id:

        # New session 
        session_id = str(uuid.uuid4())

    # can be an empty list
    chat_history: list = chat.fetch_history(session_id, db)
    rag_chain = chat.get_rag_chain(request.model)

    answer = rag_chain.invoke({
        "input": request.question,
        "chat_history": chat_history
    })['answer']
    

    chat_history = ChatHistory(
        session_id = session_id,
        question = request.question,
        response = answer,
        model = request.model,
        persona = request.persona
    )

    backend_log.info(f'Session: {session_id} | AI Response {answer}')
 
    # Update chat history in DB
    chat.update_history(chat_history, db)
       
    return QueryResponse(answer=answer, session_id=session_id)




#? ------------------------------UPLOAD DOCUMENT-------------------------#
@app.post("/document/upload")
async def upload_document(db: db_dependency, file: UploadFile = File(...), ):

    allowed_extensions = ['.pdf', '.docx',]
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    # File type validation
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}")
    
    # File path validation
    file_storage_path = f"library/{file.filename}"
    if os.path.exists(file_storage_path):
        raise HTTPException(status_code=400, detail=f"File With Same Name {file.filename}, Already present in library !")

    # Save the uploaded file to a directory
    with open(file_storage_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # record document in DB
    saved_doc = await document.insert_in_library(file.filename, db)
    
    # success = index_document_to_chroma(temp_file_path, file_id)
    
    if os.path.exists(file_storage_path):
        return {"message": f"File {file.filename} has been successfully uploaded with id : {saved_doc.id }"}


        

#* ---------------- GET DOCUMENT LIST---------------------------------#
@app.get("/document/list", response_model=list[DocResponse])
async def list_documents(db:db_dependency):
    return await document.list_all(db)


#! ---------------- DELETE DOCUMENT ---------------------------------#
@app.post("/document/delete")
async def delete_document(request: DocDeleteRequest, db: db_dependency):
   
    
    # First remove file from DB if the file is not in use!
    doc_delete = await document.delete_from_library(request.id, db)
    
    if doc_delete['success']:

        # If doc record has been successfully removed, now remove file from disk
        filepath = f'library/{doc_delete['filename']}'

        backend_log.info(f'filepath is : {filepath}')
        if os.path.exists(filepath):
            backend_log.info(f'filepath exists ! Removing file')
            os.remove(filepath)
        else:
            backend_log.info(f"filepath not found, couldn't remove !")

        response = {"message": f"Successfully deleted document with file_id {request.id} from the library."}

    else:
        raise HTTPException(status_code=400, detail=f"{doc_delete["message"]}")

    return response







# ---------------- BUILD CONTEXT---------------------------------#
@app.post("/document/build_context")
async def build_context(request: DocContextRequest, db: db_dependency) -> DocContextResponse:
    
    # First activate docs in DB
    activation: DocActivateResponse = await document.activate(request.ids, db)
    
    if activation.success:
        
        backend_log.info(f"Docs were activated in DB !")

        embedding_process: DocEmbedResponse = await document.embed(db)

        response = DocContextResponse(success=embedding_process.success, message=embedding_process.message)

    else:
        raise HTTPException(status_code=400, detail=f"{activation.message}")

    return response



