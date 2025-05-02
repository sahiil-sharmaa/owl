from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from sqlalchemy.exc import SQLAlchemyError
from langchain_openai import ChatOpenAI

from commons import db_dependency, backend_log
from models import Chat
from schema import *
import uuid



from utils.document import vector_store

retriever = vector_store.as_retriever(search_kwargs={"k": 2})

# initiate an output parser
output_parser = StrOutputParser()





# This prompt is used to modify the question by adding context to an uncontextualized_question

prompt_to_contextualize_question = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_question_template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_to_contextualize_question),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )



def get_conversation_prompt_template(persona: str = 'default') -> ChatPromptTemplate:

    if persona == 'default':
        base_prompt = "You are a helpful AI assistant.Use the following context to answer the user's question."

    else:
        base_prompt = ( f" You are a highly experienced {persona}, with years of practical and theoretical expertise. You have the accuracy, detail, and tone of a professional in that field. You are a clear and factual being that doesn't speculate. You are asked a question and provided with some context to answer that question. Answer only if the provided context is related to your personality as {persona} or your field, if its not your forte just reply the question with a simple request to change the question and ask something from your field or ask the user to change your personality settings on configuration page of application and try again with new question.")


    conversation_prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", base_prompt),
            ("system", "Context: {context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ]
    )

    return conversation_prompt_template


def get_rag_chain(model: str = "gpt-4o-mini"):

    # Use Specific model for this conversation
    LLM = ChatOpenAI(model=model)

    conversation_prompt_template = get_conversation_prompt_template()

    # fetches document from retriver based on user input and also use chat history to contextualize 
    history_aware_retriever = create_history_aware_retriever(LLM, retriever, contextualize_question_template)

    # using the conversation prompt template 
    question_answer_chain = create_stuff_documents_chain(LLM, conversation_prompt_template)

    # Chain, chat history, context and current question
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)    
    
    
    return rag_chain




def fetch_history(session_id : uuid.UUID, db: db_dependency):

    try:
        chat_history = db.query(Chat).filter(Chat.session_id == session_id).order_by(Chat.created_at).all()

        messages = []

        for chat in chat_history:
            messages.extend([
                {"role": "human", "content": chat.user_query},
                {"role": "ai", "content": chat.gpt_response}
            ])

        return messages

    except SQLAlchemyError as e:
        backend_log.info(f' Exception while pulling chat history from DB : {e}')
        
        db.rollback()  # Rollback in case of error
        raise Exception(f"Error while Fetching Chat history from DB: {e}")


 
def update_history(chat: ChatHistory, db: db_dependency):

    try:

        # Create a new chat record
        chat_record = Chat(
            session_id = chat.session_id,
            user_query = chat.question,
            gpt_response = chat.response,
            model = chat.model,
            persona = chat.persona,
        )


        # Add and commit to the database
        db.add(chat_record)
        db.commit()
        
        # Refresh the db_doc object with the new data 
        db.refresh(chat_record)
        
        return chat_record
    
    except SQLAlchemyError as e:

        backend_log.info(f' Exception while updating chat history : {e}')

        db.rollback()  # Rollback in case of error
        raise Exception(f"Error while updating chat history: {e}")
