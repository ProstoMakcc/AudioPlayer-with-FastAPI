from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///audio_server.db')

Base = declarative_base()

Base.metadata.create_all(engine)
