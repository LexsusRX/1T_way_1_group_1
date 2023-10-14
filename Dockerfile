FROM apache/airflow:2.7.0-python3.11.3
COPY requirements.txt .
RUN pip install -r requirements.txt