from sqlalchemy.orm import Session
from db.db_connection import get_db
from db.crud import *
from db.models.skill_assess import Skill_assess

db = next(get_db())

records = [
    {
        "type": "JS",
        "questions": "What is the correct way to declare a variable in JavaScript?",
        "options": '["variable x = 5", "let x = 5", "x = 5", "#x = 5"]',
        "answer": "let x = 5",
        "level": "1"
    },
    {
        "type": "Python",
        "questions": "Which keyword is used to define a function in Python?",
        "options": '["def", "function", "define", "fn"]',
        "answer": "def",
        "level": "1"
    },
    {
        "type": "SQL",
        "questions": "Which SQL command is used to retrieve data from a database?",
        "options": '["GET", "FETCH", "SELECT", "RETRIEVE"]',
        "answer": "SELECT",
        "level": "1"
    }
]

inserted_records = []
for record in records:
    inserted_records.append(insert_data(db, Skill_assess, record))

# print(inserted_records)

db.close()