# Whoop Data Pipeline

## Overview
This project is a data ingestion pipeline which extracts data from the Whoop API, transforms and validates the data before loading into a cloud based postgreSQL database hosted on Supabase.

The pipeline is fully automated to run daily on GitHub actions whilst being containerised in Docker with CI/CD on pull request and merge to main to test the code before merging and rebuilding the docker image hosted on Docker Hub.

This project now provides a valid, reliable, regularly-updated and easily accessible set of data tables containing whoop data which can be used to gain further understanding into my health trends as well as buidling out further data side projects with.


## Architecture

The pipeline is composed of the following components:

- **WHOOP API** – Source of health, recovery, sleep, workout, and cycle data
- **Authentication Layer** – Handles OAuth authorisation and token refresh
- **Data Ingestion Layer** – Fetches raw API data for defined time windows
- **Data Cleaning & Validation** – Normalises schemas, enforces data quality rules, and validates primary keys
- **Database Layer** – Upserts data into PostgreSQL 
- **Orchestration & Automation** – Docker + GitHub Actions for execution and scheduling


## Data Flow

1. The pipeline authenticates with the WHOOP API using OAuth (First time running)
2. Access tokens are refreshed automatically if expired (through checks on expiry timestamp recieved on the latest request)
4. Data is requested incrementally from each of the API endpoints
5. Raw JSON responses are normalised into tabular form
6. Data is validated for schema consistency and data quality
7. Database Shcema defined (on initial run)
8. Records are upserted into PostgreSQL tables
9. Logs are emitted for observability and debugging


## Authentication
## Data Quality & Validation
## Running the Pipeline
## Automation
## Tech Stack
## Project Status & Next Steps
