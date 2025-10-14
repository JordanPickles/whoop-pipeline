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

class WhoopDataIngestor():
    def __init__(self, access_token:str):
        self.access_token = access_token
        self.base_url = settings.whoop_api_base_url
        self.cycles_base_url = settings.whoop_api_cycles_base_url
        self.whoop_data_cleaner = WhoopDataCleaner()
        self.whoop_database = WhoopDB()
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

        if endpoint == 'activity/workout':
            records = [r for r in records if r.get("score") is not None ] # drops records with no score. Occurs for things such as stretching activities etc
        
        
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
            print(type(self.model_classes[endpoint_value]))
            while True:
                self.data_quality_validator.assertion_tests(df, self.model_classes[endpoint_value])
                df.to_csv(f"data/{endpoint_key}_data.csv", index=False)

                self.whoop_database.upsert_data(df, endpoint_key)
        

   


if __name__ == '__main__':
    whoop_client = WhoopClient()
    whoop_db = WhoopDB()
    tokens = whoop_client.get_live_access_token()
    whoop_ingestor = WhoopDataIngestor(tokens.get('access_token', 0))
    whoop_db.create_tables()
    start_date = whoop_db.get_max_date() - pd.Timedelta('7 days') # Fetch data from 7 days before the latest date in the database
    
    if pd.isna(start_date):
        start_date = pd.to_datetime('2024-01-01')
    
    start_date = start_date.tz_localize('UTC').strftime('%Y-%m-%dT%H:%M:%S.000Z')

    
    end_date = (pd.to_datetime('now') - pd.Timedelta('1 days')).tz_localize('UTC').strftime('%Y-%m-%dT%H:%M:%S.000Z')
    print(f"Fetching data from {start_date} to {end_date}")

    whoop_ingestor.data_pipeline(start_date, end_date)
   