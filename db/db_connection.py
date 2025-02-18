from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Database URL (Update as needed)
DATABASE_URL = "postgresql://postgres:password@localhost:5432/dbname"

# Set up SQLAlchemy Engine and Base
# engine = create_engine(DATABASE_URL)
db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
unix_socket_path = os.environ.get("INSTANCE_UNIX_SOCKET")
create_engine(
        # Equivalent URL:
        # postgresql+pg8000://<db_user>:<db_pass>@/<db_name>
        #                         ?unix_sock=<INSTANCE_UNIX_SOCKET>/.s.PGSQL.5432
        # Note: Some drivers require the `unix_sock` query parameter to use a different key.
        # For example, 'psycopg2' uses the path set to `host` in order to connect successfully.
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=db_user,
            password=db_pass,
            database=db_name,
            query={"unix_sock": f"{unix_socket_path}/.s.PGSQL.5432"},
        ),
        # ...
    )
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Create tables automatically when the module is imported
def init_table():
    """Ensures all tables are created before the app starts."""
    Base.metadata.create_all(engine)
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