from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from datetime import datetime

from models import Base


class Document(Base):
    __tablename__ = 'library'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name : Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    uploaded_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False,index=True,server_default=func.now())

