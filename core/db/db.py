from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.settings import DB_CONNECTOR
from core.db.models import Base

engine = create_engine(DB_CONNECTOR)

Base.metadata.create_all(engine, checkfirst=True)

Session = sessionmaker(bind=engine)

