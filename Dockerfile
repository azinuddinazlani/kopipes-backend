FROM python:3.12
ENV PYTHONUNBUFFERED True

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r  requirements.txt

ENV APP_HOME /root
WORKDIR $APP_HOME
COPY . $APP_HOME

EXPOSE 8080
WORKDIR $APP_HOME
CMD ["uvicorn", "main:app", "--reload"]