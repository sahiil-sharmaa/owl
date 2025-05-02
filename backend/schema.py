from pydantic import Field, ConfigDict, BaseModel as PydanticBaseModel
from enum import Enum
from datetime import datetime

# Create a custom base model which can be integrated with ORM models
class CustomBaseModel(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)


#--------- Model Configuration schemas --------#
class ModelName(str, Enum):
    GPT4_1_NANO = "gpt-4.1-nano"
    GPT4_O_MINI = "gpt-4o-mini"

class EmbeddingModelName(str, Enum):
    TXT_EMBDG_3_SMALL = "text-embedding-3-small"
    
class ModelPersona(str, Enum):
    DEF = "Default"
    DOC = "Medical Professional"
    FIN = "Financial Consultant"
    LAW = "Legal Advisor"



#--------- Chat schemas --------#
class QueryInput(PydanticBaseModel):
    question: str
    session_id: str | None = None
    model: str | None = ModelName.GPT4_1_NANO
    persona: str | None = ModelPersona.DEF

class QueryResponse(PydanticBaseModel):
    answer: str
    session_id: str

class ChatHistory(PydanticBaseModel):
    session_id: str | None = None
    question: str
    response: str
    model: str | None = ModelName.GPT4_1_NANO
    persona: str | None = ModelPersona.DEF


#--------- Document schemas --------#
class DocRequest(CustomBaseModel):
    id: int
    name: str
    is_active:bool
    uploaded_at: datetime

class DocResponse(DocRequest):
    pass




# Document embedding Schema
class DocContextRequest(PydanticBaseModel):
    ids: list[int]
    embedding_model: str | None = EmbeddingModelName.TXT_EMBDG_3_SMALL
    
class DocContextResponse(PydanticBaseModel):
    success: bool
    message: str


class DocActivateRequest(DocContextRequest):
    pass
class DocActivateResponse(DocContextResponse):
    pass


class DocEmbedRequest(PydanticBaseModel):
    pass
class DocEmbedResponse(DocContextResponse):
    pass


class DocVectorRequest(PydanticBaseModel):
    pass
class DocVectorResponse(DocContextResponse):
    pass






# Document Delete Schema
class DocDeleteRequest(PydanticBaseModel):
    id: int

class DocDeleteResponse(PydanticBaseModel):
    success: bool
    filename: str
    message: str
    