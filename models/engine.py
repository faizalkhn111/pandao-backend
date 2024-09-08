from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
Base = declarative_base()

engine = create_engine(
    'postgresql://pandao_backend_i7sr_user:0QEjA2SdXtOYEHeloXVn71jFNWQV9zJL@dpg-crel5fqj1k6c73de1mug-a.oregon-postgres.render.com/pandao_backend_i7sr')
Base.metadata.create_all(engine)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)
dbsession = Session()

# run predefine query

