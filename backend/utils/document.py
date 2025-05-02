from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document as LangChainDocument
from langchain_postgres import PGVector
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from pathlib import Path
# import uuid

from commons import db_dependency, backend_log
from models import Document
from schema import *
import os




# initiate Objects 
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
embedder = OpenAIEmbeddings(model=EmbeddingModelName.TXT_EMBDG_3_SMALL)

# fetch db string from env
db_string = os.getenv("DB_STRING", "postgresql+psycopg://postgres:postgres1234@postgres:5432/postgres")    

# Create PgVector instance
vector_store = PGVector(embeddings=embedder, collection_name="document_context", connection=db_string, use_jsonb=True,)






#--------- Upload doc in library --------#
async def insert_in_library(filename: str, db: db_dependency) -> DocResponse:
   
    try:
        # Create a new document record
        db_doc = Document(name=filename)
        
        # Add and commit to the database
        db.add(db_doc)
        db.commit()
        
        # Refresh the db_doc object with the new data 
        db.refresh(db_doc)
        
        return db_doc
    
    except SQLAlchemyError as e:

        db.rollback()  # Rollback in case of error
        raise Exception(f"Error while inserting document: {e}")



#--------- List all docs available in library --------#
async def list_all(db: db_dependency) -> list[DocResponse]:

    try:
        docs = db.query(Document).all()
        return docs

    except SQLAlchemyError as e:

        db.rollback()  # Rollback in case of error
        raise Exception(f"Error while Fetching documents: {e}")



#--------- fetch a doc from library --------#
async def fetch_from_library(doc_id: int, db: db_dependency) -> DocResponse | dict:
    

    try:

        # stmt = select(Document).where(Document.id == doc_id)
        # db_doc = db.execute(stmt).scalar_one_or_none()
        
        db_doc = db.query(Document).filter(Document.id == doc_id).first()
    
        if db_doc:
            return db_doc
        else:
            return {"error": f"Document with ID {doc_id} not found."}

    except SQLAlchemyError as e:
            db.rollback()  # Rollback in case of error
            raise Exception(f"Error while Fetching document: {e}")



#--------- Delete a doc from library --------#
async def delete_from_library(doc_id: int, db: db_dependency) -> DocDeleteResponse:
    
    try:
        db_doc = db.query(Document).filter(Document.id == doc_id).first()
    
        if db_doc:
            # check if current doc being used as context or not.
            if db_doc.is_active:
                response = {"success": False,"filename": db_doc.name, "message": f"Document with ID {doc_id} is currently being used as context, can't delete."}
            
            else:
                db.delete(db_doc)
                db.commit()
                response = {"success": True,"filename": db_doc.name, "message": f"Document with ID {doc_id} has been deleted."}

        else:
            response = {"success": False,"filename": db_doc.name, "message": f"Document with ID {doc_id} not found."}

    except SQLAlchemyError as e:
            db.rollback()  # Rollback in case of error
            raise Exception(f"Error while deleting document: {e}")


    return response



#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX EMBEDDING MANAGEMENT XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#

#--------- Split doc in splits --------#
def load_and_split(file_id: int, file_name: str) -> list[LangChainDocument]:
    
    current_file = Path(__file__).resolve()
    project_root = current_file.parents[1]  # adjust level depending on nesting
    file_path = project_root / "library" / file_name


    backend_log.info(f' current file is : {project_root}')
    backend_log.info(f' project root is : {project_root}')
    backend_log.info(f' File path is : {file_path}')

    doc_splits = []

    if file_path.suffix == '.pdf':
        loader = PyPDFLoader(file_path)

    elif file_path.suffix == '.docx':
        loader = Docx2txtLoader(file_path)

    else:
        return doc_splits
    
    document: LangChainDocument = loader.load()
    doc_splits = splitter.split_documents(document)

    backend_log.info(f'load and splits worked : first doc is {doc_splits[0]}')
    return doc_splits


def embed_and_upload(doc_splits: LangChainDocument) -> DocVectorResponse:

    try:
        
        backend_log.info(f'embed and upload also worked ')
        # vector_db = PGVector.from_documents(embedding=embedder, documents=doc_splits, collection_name=collection, connection_string=db_string, use_jsonb=True)
        vector_store.add_documents(doc_splits)
        
        backend_log.info(f'vectors uploaded ')
        response = DocVectorResponse(success=True, message="Document Vectors uploaded in vector store successfully")

    except Exception as e:
        backend_log.info(f' Exception occurred with vector store : {e}')
        response = DocVectorResponse(success=False, message=f"Exception : {e}")

    return response


# clean vector store
def truncate_langchain_tables(db: db_dependency):
       
    try:
        sql = """
        DO $$
        BEGIN
            IF to_regclass('langchain_pg_embedding') IS NOT NULL THEN
                EXECUTE 'TRUNCATE TABLE langchain_pg_embedding';
            END IF;
        END
        $$;
        """
        db.execute(text(sql))
        db.commit()
        return True

    except SQLAlchemyError as e:
        backend_log.info(f'Exception Occurred during truncating process : {e}')
        return False




#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX DOCUMENT MANAGEMENT DB XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#


#--------- Activate docs in db --------#
async def activate(doc_ids: list[int], db: db_dependency) -> DocActivateResponse:
    
    try:
       
        # Step 1: Update documents with IDs in doc_ids to be active (True)
        db.query(Document).filter(Document.id.in_(doc_ids)).update(
            {Document.is_active: True}, synchronize_session=False
        )

        # Step 2: Update all other documents to be inactive (False)
        db.query(Document).filter(~Document.id.in_(doc_ids)).update(
            {Document.is_active: False}, synchronize_session=False
        )

        # Commit the changes to the database
        db.commit()

        response = DocActivateResponse(success=True, message="Documents activated in db successfully")

    except SQLAlchemyError as e:
        db.rollback()  # Rollback in case of error
        response = DocActivateResponse(success=False, message=f"Exception : {e}")

    return response





# ----- Embed Docs in DB ------- #
async def embed(db: db_dependency) -> DocEmbedResponse:
    
    try:

        # Step 3: Fetch the names of all documents with is_active = True
        activated_docs = db.query(Document).filter(Document.is_active == True).all()
        total_active_docs = len(activated_docs)

        for active_doc in activated_docs:
            backend_log.info(f' active doc is  : {active_doc}')

        # empty the vector store, every time new context needs to built.
        if truncate_langchain_tables(db):
            backend_log.info(f'Vector store cleaned fully ')

        success_count = 0
        for active_doc in activated_docs:

            backend_log.info(f'running time {success_count + 1}')
            doc_splits: LangChainDocument = load_and_split(active_doc.id, active_doc.name)
            doc_vector: DocVectorResponse = embed_and_upload(doc_splits)

            if doc_vector.success:
                success_count += 1

        if success_count == total_active_docs:
            response = DocEmbedResponse(success=True, message="Documents embedded and uploaded in vector store successfully")
        else:
            response = DocEmbedResponse(success=False, message=f"{success_count} Documents were uploaded to vector store")    

    except SQLAlchemyError as e:
        backend_log.info(f'Exception Occurred during embedding and uploading vectors process : {e}')
        response = DocEmbedResponse(success=False, message=f"DataBase Communication error")

    return response


