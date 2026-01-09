# WHOOP Data Pipeline ⚫️⚪️
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)
![CI](https://img.shields.io/badge/GitHub%20Actions-Enabled-success)


## 📖 Overview

This project is a data ingestion pipeline for the WHOOP API.  
It securely authenticates with WHOOP, incrementally ingests user health data, and stores it in a PostgreSQL database.

The pipeline is:
- Fully containerised with Docker
- Automated via GitHub Actions
- Configured entirely through environment variables
- Designed to be reusable across environments and databases

The main goal of this project is to create a clean, reliable data foundation that I can actually explore in my own side projects, and use to uncover more meaningful insights about my health than the Whoop app currently provides.

This pipeline is designed for personal use and experimentation, but follows production-style patterns to keep it reliable, observable, and easy to extend.

## 🚀 Quick Facts

- **Language:** Python 3.11  
- **Runtime:** Docker  
- **Auth:** OAuth2 (WHOOP)  
- **Database:** PostgreSQL (tested with Supabase)  
- **Orchestration:** GitHub Actions (scheduled + manual runs)  
- **Use case:** Personal health analytics, experimentation and data upskilling
  
---

## 🧠 What This Pipeline Does

At a high level, the pipeline follows this flow:

1. Authenticates with the WHOOP API using OAuth2
2. Refreshes access tokens automatically when required
3. Pulls WHOOP data incrementally (cycles, sleep, recovery, workouts)
4. Cleans and normalises API responses
5. Upserts data into PostgreSQL fact tables
6. Runs automatically on a schedule via GitHub Actions

---

## ⚙️ Architecture

**Core components:**
- **WHOOP API** – Source of health and activity data
- **Docker** – Runtime environment for the pipeline
- **PostgreSQL (Supabase)** – Persistent data store
- **GitHub Actions** – CI/CD and scheduled execution
- **SQLAlchemy + Pandas** – Data access and transformation
- **Pydantic** – Configuration and environment validation
- **Python logging** – Observability and runtime diagnostics

All secrets (API credentials, database credentials) are injected at runtime via environment variables and are never stored in the codebase.

---

## 🗂️ Data Model

The pipeline creates and maintains the following tables:

- `fact_cycle`
- `fact_activity_sleep`
- `fact_recovery`
- `fact_workout`
- `access_tokens`

Data is upserted using primary keys to ensure:
- Idempotent runs
- Safe incremental loading
- Automatic updates when WHOOP data changes retroactively (pulls back the 7 days prior to the latest date in the table and updates those rows)

---

## 🔐 Authentication

WHOOP authentication is handled using OAuth2.

Key points:
- Running the process triggers a user sign in with the whoop interface
- Following sign-in, an auth code is captured in a redirect URI on a local host
- The code is then used in exchange for an access token and a refresh token 
- The refresh token is stored securely (database)
- Access tokens are refreshed automatically when expired
- Docker and CI environments run non-interactive token refresh flows by printing a URL in the terminal which can be oepned to complete sign-in

---

## ▶️ Running the Pipeline
To run the pipeline via the docker image, the following steps would need to be completed first.
- Setup an account as a developer in the Whoop [here](https://developer-dashboard.whoop.com/).
- Create a new app
- Name the app
- Tick the scope boxes
- Add a redirect, the below will work for this.
```http://localhost:8080/callback```
- Set up a PostgreSQL database which can be accessed by the project
- Ensure you have the docker daemon running
- Run the below code inserting the required environment variables

### Run via Docker (recommended)

```bash
docker pull jpickles/whoop-pipeline:latest

docker run --rm \
  -p 8080:8080 \
  -e WHOOP_CLIENT_ID=<Insert from your Whoop App Details> \
  -e WHOOP_CLIENT_SECRET=<Insert from your Whoop App Details> \
  -e WHOOP_REDIRECT_URI=<Insert from your Whoop App Details> \
  -e WHOOP_AUTH_URL="https://api.prod.whoop.com/oauth/oauth2/auth" \
  -e WHOOP_TOKEN_URL="https://api.prod.whoop.com/oauth/oauth2/token" \
  -e WHOOP_SCOPE="offline read:recovery read:cycles read:sleep read:workout read:profile read:body_measurement" \
  -e WHOOP_API_BASE_URL="https://api.prod.whoop.com/developer/v2/" \
  -e WHOOP_API_CYCLES_BASE_URL=https://api.prod.whoop.com/developer/v1/ \
  -e DB_HOST=<Insert your database host> \
  -e DB_PORT=<Insert your database port> \
  -e DB_NAME=<Insert your database name> \
  -e DB_USER=<Insert your database username> \
  -e DB_PASSWORD=<Insert your database username> \
  jpickles/whoop-pipeline:latest
```

## 📊 Logging & Observability

The pipeline uses Python’s built-in logging module to provide visibility into:
- Authentication and token refresh events
- Data ingestion progress
- Database writes and upserts
- Runtime duration and failures

Additional logging and structured error handling will be added iteratively as the pipeline evolves.

## ⚖️ Design Trade-offs and Project Limitations

This project intentionally avoids heavier orchestration tools (e.g. Airflow, dbt, Spark) to keep the pipeline lightweight and easy to understand.

The focus is on:
- Reliability over scale
- Clarity over abstraction
- Supporting real data exploration rather than building a generic platform

A key limitation for this project is the single user nature in which it is built, meaning that only one user authorisation code can be stored at a single time

## 🔮 Potential Improvements & Next Steps
- Associate access tokens with a user identifier, allowing the pipeline to support multiple WHOOP users.

