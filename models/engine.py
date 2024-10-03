from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
Base = declarative_base()

engine = create_engine(
    'postgresql://postgres:123@localhost:5432/pandao')
Base.metadata.create_all(engine)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)
dbsession = Session()

# run predefine query

