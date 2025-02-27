from db_connection import SessionLocal
from crud import add_columns_to_table

# Get a session
session = SessionLocal()

# Modify table
add_columns_to_table(session, "users", {
    # "resume": "TEXT"
    # "resume_base64": "TEXT"
    "position": "TEXT",
    "location": "TEXT",
    "experience": "TEXT",
    "education": "TEXT",
    "jobs": "TEXT"
})

# add_columns_to_table(session, "skill_assess", {
#     "level": "TEXT"
# })

# Close session
session.close()