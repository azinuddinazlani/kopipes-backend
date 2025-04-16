# from sqlalchemy import create_engine, engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# import sqlalchemy
# import pg8000
# import os, sys
# from google.cloud.sql.connector import Connector, IPTypes
# from dotenv import load_dotenv

# load_dotenv()
# # Database URL (Update as needed)


# # Set up SQLAlchemy Engine and Base
# # engine = create_engine(DATABASE_URL)
# db_user = os.environ.get("DB_USER")
# db_pass = os.environ.get("DB_PASS")
# db_name = os.environ.get("DB_NAME")
# db_port = os.environ.get("DB_PORT")
# db_host = os.environ.get("DB_HOST")
# unix_socket_path = os.environ.get("INSTANCE_UNIX_SOCKET")
# cloud_sql_instance = os.environ.get('CLOUD_SQL_INSTANCE')

# def connect_with_connector() -> sqlalchemy.engine.base.Engine:
#     """
#     Initializes a connection pool for a Cloud SQL instance of Postgres.

#     Uses the Cloud SQL Python Connector package.
#     """
#     # Note: Saving credentials in environment variables is convenient, but not
#     # secure - consider a more secure solution such as
#     # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
#     # keep secrets safe.

#     ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

#     # initialize Cloud SQL Python Connector object
#     connector = Connector(refresh_strategy="LAZY")

#     def getconn() -> pg8000.dbapi.Connection:
#         conn: pg8000.dbapi.Connection = connector.connect(
#             cloud_sql_instance,
#             "pg8000",
#             user=db_user,
#             password=db_pass,
#             db=db_name,
#             ip_type=ip_type,
#         )
#         return conn

#     # The Cloud SQL Python Connector can be used with SQLAlchemy
#     # using the 'creator' argument to 'create_engine'
#     pool = sqlalchemy.create_engine(
#         "postgresql+pg8000://",
#         creator=getconn,
#         # ...
#     )
#     return pool


# def connect_to_local_postgres() -> sqlalchemy.engine.base.Engine:
#     """
#     Initializes a connection pool for a local instance of Postgres.
#     """
#     local_db_url = "postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}".format(
#         db_user=db_user,
#         db_pass=db_pass,
#         db_host=db_host,
#         db_port=db_port,
#         db_name=db_name
#     )
#     local_engine = sqlalchemy.create_engine(local_db_url)
#     return local_engine

# # Example usage
# dbengine = connect_to_local_postgres() if os.getenv('DEV') else connect_with_connector()
# SessionLocal = sessionmaker(bind=dbengine)
# Base = declarative_base()

# # Create tables automatically when the module is imported
# def init_table():
#     """Ensures all tables are created before the app starts."""
#     Base.metadata.create_all(dbengine)
#     # Base.metadata.drop_all(engine)  # Drops all tables
#     # Base.metadata.create_all(engine)  # Creates all tables again


# # Function to get a database session
# def get_db():
#     """Provides a new session instance."""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
        
        
# if __name__ == '__main__':
#     if len(sys.argv) > 1:
#         globals()[sys.argv[1]]()

# Connect to supabase

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import sqlalchemy
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase database connection parameters
db_user = os.environ.get("SUPABASE_DB_USER")
db_pass = os.environ.get("SUPABASE_DB_PASS")
db_name = os.environ.get("SUPABASE_DB_NAME")
db_port = os.environ.get("SUPABASE_DB_PORT", "5432")
db_host = os.environ.get("SUPABASE_DB_HOST")

def connect_to_supabase() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection to Supabase PostgreSQL database.
    """
    db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine = sqlalchemy.create_engine(db_url)
    return engine

# Use local connection for development, Supabase for production
dbengine = connect_to_local_postgres() if os.getenv('DEV') else connect_to_supabase()
SessionLocal = sessionmaker(bind=dbengine)
Base = declarative_base()

# Create tables automatically when the module is imported
def init_table():
    """Ensures all tables are created before the app starts."""
    Base.metadata.create_all(dbengine)

# Function to get a database session
def get_db():
    """Provides a new session instance."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        globals()[sys.argv[1]]()