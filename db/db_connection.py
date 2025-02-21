from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker, declarative_base
import sqlalchemy
import pg8000
import os, sys
from google.cloud.sql.connector import Connector, IPTypes

# Database URL (Update as needed)


# Set up SQLAlchemy Engine and Base
# engine = create_engine(DATABASE_URL)
db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
unix_socket_path = os.environ.get("INSTANCE_UNIX_SOCKET")
cloud_sql_instance = os.environ.get('CLOUD_SQL_INSTANCE')

DATABASE_URL = "postgresql://{db_user}:{db_pass}@localhost:5432/{db_name}"

def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of Postgres.

    Uses the Cloud SQL Python Connector package.
    """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.

    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    # initialize Cloud SQL Python Connector object
    connector = Connector(refresh_strategy="LAZY")

    print('CLOUD_SQL_CONNECTION_NAME: ', CLOUD_SQL_CONNECTION_NAME)

    def getconn() -> pg8000.dbapi.Connection:
        conn: pg8000.dbapi.Connection = connector.connect(
            cloud_sql_instance,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type,
        )
        return conn

    # The Cloud SQL Python Connector can be used with SQLAlchemy
    # using the 'creator' argument to 'create_engine'
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        # ...
    )
    return pool

dbengine = connect_with_connector()
SessionLocal = sessionmaker(bind=dbengine)
Base = declarative_base()

# Create tables automatically when the module is imported
def init_table():
    """Ensures all tables are created before the app starts."""
    Base.metadata.create_all(dbengine)
    # Base.metadata.drop_all(engine)  # Drops all tables
    # Base.metadata.create_all(engine)  # Creates all tables again


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