from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.db_connection import get_db
from db.crud import *
from db.models.skill_assess import Skill_assess, SkillType
from typing import List

router = APIRouter()

@router.post("/upload-skill-assess")
def upload_skill_assess(db: Session = Depends(get_db)):
    records = [
        {
        	"type": "Python",
          "level": "1",
          "questions": "What is the correct file extension for Python files?",
          "options": '{"A": ".py", "B": ".python", "C": ".pt", "D": ".txt"}',
          "answer": "A"
        },
        {
        	"type": "Python",
          "level": "1",
          "questions": "How do you output text in Python?",
          "options": '{"A": "print()", "B": "echo()", "C": "output()", "D": "write()"}',
          "answer": "A"
        },
        {
        	"type": "Python",
          "level": "1",
          "questions": "Which of the following is a valid variable name?",
          "options": '{"A": "1variable", "B": "variable_name", "C": "variable-name", "D": "variable.name"}',
          "answer": "B"
        },
        {
        	"type": "Python",
          "level": "1",
          "questions": "Which data type is used to store True or False values?",
          "options": '{"A": "int", "B": "float", "C": "bool", "D": "str"}',
          "answer": "C"
        },
        {
        	"type": "Python",
          "level": "1",
          "questions": "What is the output of 3 + 2 * 2?",
          "options": '{"A": "10", "B": "7", "C": "8", "D": "9"}',
          "answer": "B"
        },
        {
        	"type": "Python",
          "level": "2",
          "questions": "Which of the following loops is used to iterate over a sequence?",
          "options": '{"A": "for", "B": "while", "C": "do-while", "D": "loop"}',
          "answer": "A"
        },
        {
        	"type": "Python",
          "level": "2",
          "questions": "What is the output of the following code: 'print(2 ** 3)'?",
          "options": '{"A": "6", "B": "8", "C": "9", "D": "None of the above"}',
          "answer": "B"
        },
        {
        	"type": "Python",
          "level": "2",
          "questions": "How do you handle exceptions in Python?",
          "options": '{"A": "try...catch", "B": "try...except", "C": "try...error", "D": "try...finally"}',
          "answer": "B"
        },
        {
        	"type": "Python",
          "level": "3",
          "questions": "Which method is used to add an item to the end of a list?",
          "options": '{"A": "append()", "B": "add()", "C": "insert()", "D": "extend()"}',
          "answer": "A"
        },
        {
	"type": "Javascript",
        "level": "1",
        "questions": "What is the correct way to declare a variable in JavaScript?",
        "options": '{"A": "variable x = 5", "B": "let x = 5", "C": "x = 5", "D": "#x = 5"}',
        "answer": "B"
      },
      {
      	"type": "Javascript",
        "level": "1",
        "questions": "Which operator is used for equality comparison without type checking?",
        "options": '{"A": "===", "B": "==", "C": "=", "D": "!="}',
        "answer": "B"
      },
      {
      	"type": "Javascript",
        "level": "1",
        "questions": "How do you write a comment in JavaScript?",
        "options": '{"A": "<!-- comment -->", "B": "/* comment */", "C": "# comment", "D": "// comment"}',
        "answer": "D"
      },
      {
      	"type": "Javascript",
        "level": "1",
        "questions": "What is the correct way to write 'Hello World' in an alert box?",
        "options": '{"A": "alertBox(\"Hello World\")", "B": "msg(\"Hello World\")", "C": "alert(\"Hello World\")", "D": "msgBox(\"Hello World\")"}',
        "answer": "C"
      },
      {
      	"type": "Javascript",
        "level": "1",
        "questions": "Which method is used to add an element at the end of an array?",
        "options": '{"A": "push()", "B": "add()", "C": "append()", "D": "insert()"}',
        "answer": "A"
      },
      {
      	"type": "Javascript",
        "level": "2",
        "questions": "What is the output of: typeof([1,2,3])?",
        "options": '{"A": "\"array\"", "B": "\"object\"", "C": "\"list\"", "D": "\"number\""}',
        "answer": "B"
      },
      {
      	"type": "Javascript",
        "level": "2",
        "questions": "Which method removes the last element of an array?",
        "options": '{"A": "pop()", "B": "last()", "C": "remove()", "D": "delete()"}',
        "answer": "A"
      },
      {
      	"type": "Javascript",
        "level": "2",
        "questions": "What is the result of 3 + \"3\"?",
        "options": '{"A": "6", "B": "\"33\"", "C": "33", "D": "Error"}',
        "answer": "B"
      },
      {
      	"type": "Javascript",
        "level": "3",
        "questions": "What is the output of: [1,2,3].map(x => x*2)?",
        "options": '{"A": "[1,2,3]", "B": "[2,4,6]", "C": "undefined", "D": "Error"}',
        "answer": "B"
      },
      {
      	"type": "Javascript",
        "level": "3",
        "questions": "What is closure in JavaScript?",
        "options": '{"A": "A way to protect variables", "B": "A function with access to variables in its outer scope", "C": "A method to close browser window", "D": "A way to end loops"}',
        "answer": "B"
      }
    ]

    inserted_records = []
    for record in records:
        inserted_records.append(insert_data(db, Skill_assess, record))

    return "{'ok'}"

@router.post("/modify-table-user")
def modify_table_user(db: Session = Depends(get_db)):    
  add_columns_to_table(db, "users", {
      # "resume": "TEXT"
      # "resume_base64": "TEXT"
      "position": "TEXT",
      "location": "TEXT",
      "experience": "TEXT",
      "education": "TEXT",
      "jobs": "TEXT"
  })