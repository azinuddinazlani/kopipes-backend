from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URL (Update as needed)
DATABASE_URL = "postgresql://postgres:password@localhost:5432/dbname"

# Set up SQLAlchemy Engine and Base
engine = create_engine(DATABASE_URL)
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