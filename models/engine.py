from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
Base = declarative_base()

engine = create_engine(
    'postgresql://pandao_backend_6fnr_user:Nz7wvjeIf30hrc2csqXuu0n006Y1Vg6l@dpg-crvak0pu0jms73anuaq0-a.oregon-postgres.render.com/pandao_backend_6fnr')
Base.metadata.create_all(engine)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)
dbsession = Session()

# run predefine query

