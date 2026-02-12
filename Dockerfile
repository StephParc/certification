# Dokerfile
FROM apache/airflow:2.7.1-python3.11

COPY requirements-airflow.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt