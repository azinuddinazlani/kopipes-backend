### install

1. python3 -m venv <folder>
2. source <folder>/bin/activate
3. ~~pip3 install sqlalchemy psycopg2 fastapi uvicorn pydantic email_validator~~
4. pip3 install -r requirements.txt

### run uvicorn

to start uvicorn:
uvicorn main:app --reload

if uvicorn doesn't start, try <folder>/bin/python -m uvicorn main:app --reload

### fastapi routers

1. create inside routers/<filename>.py
2. include inside main.py

### declare table and pydantic

db/models/

### Modify column in table

1. make changes inside db/migrations.py
2. run `python3 db/migrations.py`

### insert data into table

seeds/

run from the root folder

```
python3 -m seeds.<filename>
```
