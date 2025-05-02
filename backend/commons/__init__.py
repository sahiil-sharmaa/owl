from .logger import configure_logger
from .database import engine, SessionLocal, Base, db_dependency

backend_log = configure_logger()