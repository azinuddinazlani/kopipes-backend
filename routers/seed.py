from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.db_connection import get_db
from db.crud import *
from db.models.skill_assess import Skill_assess, SkillType
from db.models.employer import Employer, EmployerJobs
from typing import List

router = APIRouter()

@router.post("/upload-company-info")
def upload_company_info(db: Session = Depends(get_db)):
  records = [
    {
      "name": "Gamuda Group",
      "info": "Backed by a creative and innovative workforce, Gamuda has grown since 1976 into Malaysia’s leading contractor and property developer. We deliver world-class products and solutions that connect people and cities and create sustainable transformation for an enhanced quality of life. Our expertise in creating significant infrastructure and homes of the future have resulted in award-winning projects and townships and elevated industry standards. With growing national and international market presence in the Asia-Pacific region, namely Taiwan, Australia, Singapore, and Vietnam, Gamuda is poised to become a global player as we shift our focus towards sustainable townships and smart cities, digitalized construction ecosystems, and innovative building solutions in line with the rapid changes brought about by the Fourth Industrial Revolution. In addition to an inclusive and diverse workforce, we also invest in talent growth and continuous development to create an environment that nurtures an all-rounded, competitive, and self-driven workforce.",
      "logo": "https://image-service-cdn.seek.com.au/18e7d6b6668a4a0102c8cd7e9cedec836b922791"
    },
    {
      "name": "Google",
      "info": "Google is not a conventional company, and we don’t intend to become one. True, we share attributes with the world’s most successful organizations – a focus on innovation and smart business practices comes to mind – but even as we continue to grow, we’re committed to retaining a small-company feel. At Google, we know that every employee has something important to say, and that every employee is integral to our success. We provide individually tailored compensation packages that can be comprised of competitive salary, bonus, and equity components, along with the opportunity to earn further financial bonuses and rewards. Googlers thrive in small, focused teams and high-energy environments, believe in the ability of technology to change the world, and are as passionate about their lives as they are about their work. At Google, we don’t just accept difference - we celebrate it, we support it, and we thrive on it for the benefit of our employees, our products, and our community. Google is proud to be an equal opportunity workplace.",
      "logo": "https://image-service-cdn.seek.com.au/3a3c4de8b2850c8f6c5c3da4e2355e7136da7657"
    },
    {
      "name": "Popular Book Company",
      "info": "Founded in 1924, we are an established brand with a wide network and strong market share in the Malaysia retail scene. Our core businesses are in retailing, publishing, and distribution, and we are now moving into a new business segment, i.e., e-learning. Our global operations span across Singapore, Malaysia, Hong Kong, Macau, China, Taiwan, and Canada. We have maintained our competitive edge by continually striving towards better business practices and strengthening our commitment to serving our customers in the best possible way. In line with our rapid expansion needs, we are now seeking bright minds and trendsetters to join our growing team in Malaysia.",
      "logo": "https://image-service-cdn.seek.com.au/3143dd9aeddc7072f47c6c5261069721199bdcb3"
    }
  ]

  inserted_records = []
  for record in records:
      inserted_records.append(insert_data(db, Employer, record))

  return "{'ok'}"


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

@router.post("/modify-table")
def modify_table(db: Session = Depends(get_db)):    
  # add_columns_to_table(db, "users", {
  #     "position": "TEXT",
  #     "location": "TEXT",
  #     "experience": "TEXT",
  #     "education": "TEXT",
  #     "jobs": "TEXT"
  # })
  # add_columns_to_table(db, "employers", {
  #     "info": "TEXT",
  #     "logo": "TEXT"
  # })
  add_columns_to_table(db, "employer_jobs", {
      "description": "TEXT",
      "desc_json": "TEXT"
  })
  add_columns_to_table(db, "user_employer_jobs", {
      "match_json": "TEXT"
  })