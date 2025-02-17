from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import literal
from sqlalchemy import text, or_, and_, func

# Insert Data
def insert_data(session: Session, model, data: dict):
    """Inserts a new record into the database."""
    try:
        new_record = model(**data)
        session.add(new_record)
        session.commit()
        print(f"Inserted into {model.__tablename__} with ID: {new_record.id}")
        return new_record
    except Exception as e:
        session.rollback()
        print(f"Error inserting into {model.__tablename__}: {e}")
        return {"error": str(e)}

# Update Data
def update_data(session: Session, model, filters: dict, update_values: dict):
    """Updates a record if it exists."""
    try:
        record = session.query(model).filter_by(**filters).first()
        if record:
            for key, value in update_values.items():
                setattr(record, key, value)
            session.commit()
            print(f"Updated {model.__tablename__} where {filters}")
            return record
        else:
            print(f"No record found in {model.__tablename__} matching {filters}")
            return {"error": f"No record found in {model.__tablename__} matching {filters}"}
    except Exception as e:
        session.rollback()
        print(f"Error updating {model.__tablename__}: {e}")
        return None

# Delete Data
def delete_data(session: Session, model, filters: dict):
    """Deletes a record if it exists."""
    try:
        record = session.query(model).filter_by(**filters).first()
        if record:
            session.delete(record)
            session.commit()
            print(f"Deleted from {model.__tablename__} where {filters}")
            return True
        else:
            print(f"No record found in {model.__tablename__} matching {filters}")
            return False
    except Exception as e:
        session.rollback()
        print(f"Error deleting from {model.__tablename__}: {e}")
        return False

def get_data(session: Session, model, filters=None):
    """Fetches records from the database with support for both list and dict filters."""
    try:
        query = session.query(model)
        
        if filters:
            if isinstance(filters, list):  # New format: List of dictionaries
                conditions = [
                    and_(*(getattr(model, key).ilike(f"%{value}%") if isinstance(value, str) else getattr(model, key) == value
                           for key, value in f.items()))
                    for f in filters
                ]
                query = query.filter(or_(*conditions))

            elif isinstance(filters, dict):  # Old format: Single dictionary
                query = query.filter(
                    *(getattr(model, key).ilike(f"%{value}%") if isinstance(value, str) else getattr(model, key) == value
                      for key, value in filters.items())
                )
                
        result = query.all()

        if not result:
            print(f"No record found in {model.__tablename__} matching {filters}")
            return {"error": "No record found"}

        return result

    except Exception as e:
        session.rollback()
        print(f"Error retrieving from {model.__tablename__}: {e}")
        return {"error": str(e)}

# Save Data (Insert if not exists, Update otherwise)
def save_data(session: Session, model, data: dict, filters: dict = None):
    """Inserts a new record if no filter is found, otherwise updates it."""
    if filters:
        existing_record = session.query(model).filter_by(**filters).first()
        if existing_record:
            print(f"Record found in {model.__tablename__}, updating...")
            return update_data(session, model, filters, data)

    print(f"No matching record found in {model.__tablename__}, inserting new record...")
    return insert_data(session, model, data)

# Add Columns to an Existing Table
def add_columns_to_table(session: Session, table_name: str, columns: dict):
    """
    Adds multiple columns to an existing PostgreSQL table.

    :param session: SQLAlchemy Session instance
    :param table_name: Name of the table to modify
    :param columns: Dictionary of column names and their SQL data types (as strings)
    """
    try:
        for column_name, column_type in columns.items():
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_type};"
            session.execute(text(alter_sql))  # Uses session.execute instead of engine.connect()
        session.commit()
        print(f"Columns {', '.join(columns.keys())} added to {table_name} successfully!")
    except Exception as e:
        session.rollback()
        print(f"Error modifying table {table_name}: {e}")