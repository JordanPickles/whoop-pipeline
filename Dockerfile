
FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

ENV SSL_CERT_FILE=/usr/local/lib/python3.11/site-packages/certifi/cacert.pem
ENV PYTHONPATH=/code/src

ENTRYPOINT ["python", "-m", "whoop_pipeline.ingest_data"]