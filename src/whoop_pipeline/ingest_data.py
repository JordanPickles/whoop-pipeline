
import logging
import requests
import json
from whoop_pipeline.config import settings
from whoop_pipeline.auth import WhoopClient
from whoop_pipeline.database import WhoopDB
from whoop_pipeline.data_cleaning import WhoopDataCleaner
from whoop_pipeline.test_data_quality import DataValidationTests
import whoop_pipeline.models as WhoopModels
import pandas as pd
import time
from datetime import date, timedelta, datetime as dt
from whoop_pipeline.logging_config import setup_logging
from contextlib import contextmanager
import logging


setup_logging()

logger = logging.getLogger(__name__)

@contextmanager
def step_timer(name: str):
    t0 = time.perf_counter()
    logger.info("Step started: %s", name)
    try:
        yield
        logger.info("Step finished: %s (%.2fs)", name, time.perf_counter() - t0)
    except Exception:
        logger.exception("Step failed: %s (%.2fs)", name, time.perf_counter() - t0)
        raise


class WhoopDataIngestor():
    def __init__(self, access_token:str, whoop_database=None):
        self.access_token = access_token
        self.base_url = settings.whoop_api_base_url
        self.cycles_base_url = settings.whoop_api_cycles_base_url
        self.whoop_data_cleaner = WhoopDataCleaner()
        self.whoop_database = whoop_database or WhoopDB()
        self.data_quality_validator = DataValidationTests()
        self.model_classes = {'cycle': WhoopModels.Cycle,
                'activity/sleep': WhoopModels.Sleep, 
                'recovery': WhoopModels.Recovery,
                'activity/workout': WhoopModels.Workout
                } # returns the table schema from models.py based on endpoint

    def get_json(self, base_url:str, base_cycles_url:str, endpoint:str, params:dict) -> dict:
        """Fetches JSON data from the Whoop API."""

        if endpoint == 'cycle': 
            base_url = self.cycles_base_url 
        else: base_url = self.base_url
        
        url = f"{base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
            , "Accept": "application/json"
        }  
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        response_json = response.json()
        
        return response_json
    
    def paginator(self, json_data: dict, endpoint: str, limit:int , start:str, end:str) -> pd.DataFrame:
        """Handles pagination for Whoop API responses."""
        data = json_data.get("records")
        response_json_list = []
        response_json_list.extend(data)
        next_access_token = json_data.get("next_token")

        if endpoint == 'cycle': 
            base_url = self.cycles_base_url 
        else: base_url = self.base_url

        while next_access_token is not None:
            
            url = f"{base_url}{endpoint}"
        
            headers = {
                "Authorization": f"Bearer {self.access_token}"
                , "Accept": "application/json"
            }   
            params = {'nextToken': next_access_token,
                'start': start,
                'end': end,
                'limit': limit}
        
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            response_json = response.json()
            records = response_json.get("records")
            response_json_list.extend(records)
            next_access_token = response_json.get("next_token")
        
        df =  pd.json_normalize(response_json_list)
        
        return df
    

    def data_pipeline(self, start_date:str, end_date:str):
        """Retrieves data from Whoop API and saves to CSV files."""
 
        endpoints = {'fact_cycle': 'cycle',
                      'fact_activity_sleep':'activity/sleep',
                        'fact_recovery':'recovery',
                          'fact_workout':'activity/workout'}  
        
        
        params = {'limit': 25, 'start': start_date, 'end': end_date}

        for endpoint_key, endpoint_value in endpoints.items(): 
            json_data = self.get_json(self.base_url, self.cycles_base_url, endpoint_value, params) 
            df = self.paginator(json_data, endpoint_value, params['limit'] , params['start'], params['end'])    
            df = self.whoop_data_cleaner.clean_data(df, endpoint_value, self.model_classes[endpoint_value])

            if not df.empty:
                if df[df.columns[0]].count() > 28:
                    df_sample = df.sample(n=28, random_state=42) # ensures only 28 rows of data are validated to ensure the pipeline runs in a reasonable time
                    self.data_quality_validator.assertion_tests(df_sample, self.model_classes[endpoint_value])
                    
                else: 
                    self.data_quality_validator.assertion_tests(df, self.model_classes[endpoint_value])
                logger.info(f"Data for {endpoint_key} passed all validation tests.")

            table, primary_key, table_cols = self.whoop_database.get_model_class_data(self.model_classes[endpoint_value])
            rows = self.whoop_database.process_dataframe(df, table_cols)
            self.whoop_database.upsert_data(table, primary_key, table_cols, rows, session=None)


if __name__ == '__main__':

    t0_total = time.perf_counter()
    logger.info("Starting Whoop Data Ingestion Pipeline")

    try:
        with step_timer("init clients"):
            whoop_client = WhoopClient()
            whoop_db = WhoopDB()

        with step_timer("get live access token"):
            tokens = whoop_client.get_live_access_token()

        with step_timer("init ingestor"):
            whoop_ingestor = WhoopDataIngestor(
                tokens.get("access_token", ""),
                whoop_database=whoop_db
            )

        with step_timer("create tables"):
            whoop_db.create_tables()

        with step_timer("compute date window"):
            max_date = whoop_db.get_max_date()
            if pd.isna(max_date):
                start_date = pd.to_datetime("2024-01-01", utc=True)
            else:
                # max_date converted to UTC
                start_date = pd.to_datetime(max_date, utc=True) - pd.Timedelta(days=7)

            end_date = pd.Timestamp.now(tz="Europe/London")

            start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")

            logger.info("Ingest window: %s -> %s", start_date, end_date)

        with step_timer("run data pipeline"):
            whoop_ingestor.data_pipeline(start_date, end_date)

        logger.info(
            "Whoop Data Ingestion Pipeline completed successfully in %.2fs",
            time.perf_counter() - t0_total
        )

    except Exception:
        logger.exception(
            "Whoop Data Ingestion Pipeline failed after %.2fs",
            time.perf_counter() - t0_total
        )
        raise