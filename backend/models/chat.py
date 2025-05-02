from sqlalchemy import Integer, String, DateTime, Text, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from datetime import datetime

from models import Base

class Chat(Base):
    __tablename__ = 'history'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id : Mapped[str] = mapped_column(String(100), nullable=False)
    user_query : Mapped[str] = mapped_column(Text, nullable=False)
    gpt_response : Mapped[str] = mapped_column(Text, nullable=False)
    model : Mapped[str] = mapped_column(String(100), nullable=False)
    persona : Mapped[str] = mapped_column(String(100), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False,index=True,server_default=func.now())




