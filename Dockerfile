FROM python:3.12
ENV PYTHONUNBUFFERED True

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r  requirements.txt

ENV APP_HOME /root
WORKDIR $APP_HOME
COPY . $APP_HOME

RUN apt install wget
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
RUN chmod +x cloud_sql_proxy

EXPOSE 8000
WORKDIR $APP_HOME
CMD ["uvicorn", "main:app", "--reload", "--port", "8000"]