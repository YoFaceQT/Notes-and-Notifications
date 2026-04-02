from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings


sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
)

session_base = sessionmaker(sync_engine)
