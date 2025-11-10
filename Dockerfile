
FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

EXPOSE 8080

ENV PYTHONPATH=/code/src

ENTRYPOINT ["python", "-m", "whoop_pipeline.ingest_data"]