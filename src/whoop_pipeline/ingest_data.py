import requests
import json
from whoop_pipeline.config import settings
from whoop_pipeline.auth import WhoopClient
from whoop_pipeline.database import WhoopDB
from whoop_pipeline.data_cleaning import WhoopDataCleaner
import pandas as pd
import time


class WhoopDataIngestor():
    def __init__(self, access_token:str):
        self.access_token = access_token
        self.base_url = settings.whoop_api_base_url
        self.whoop_data_cleaner = WhoopDataCleaner()
        self.whoop_database = WhoopDB()

    def get_json(self, base_url:str, endpoint:str, params:dict) -> dict:
        """Fetches JSON data from the Whoop API."""

        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
            , "Accept": "application/json"
        }  
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        response_json = response.json()
        
        return response_json
    
    def paginator(self, json_data: dict, endpoint: str, start:str, end:str) -> pd.DataFrame:
        """Handles pagination for Whoop API responses."""
        data = json_data.get("records")
        response_json_list = []
        response_json_list.extend(data)
        next_access_token = json_data.get("next_token")

        while next_access_token is not None:
            
            
            # print("Fetching next page of data with token:", next_access_token)
            url = f"{self.base_url}{endpoint}"
        
            headers = {
                "Authorization": f"Bearer {self.access_token}"
                , "Accept": "application/json"
            }   
            params = {'nextToken': next_access_token,
                'start': start,
                'end': end}
        
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            response_json = response.json()
            records = response_json.get("records")
            response_json_list.extend(records)

            next_access_token = response_json.get("next_token")

        df =  pd.json_normalize(response_json_list)
        
        return df


    def data_pipeline(self, start:str, end:str):
        """Retrieves data from Whoop API and saves to CSV files."""
 
        endpoints = {'fact_cycle': 'cycle', 'fact_activity_sleep':'activity/sleep', 'fact_recovery':'recovery', 'fact_workout':'activity/workout'}  
        params = {'start': start, 'end': end}

        for endpoint_key, endpoint_value in endpoints.items(): 
            json_data = self.get_json(self.base_url, endpoint_value, params)   
            df = self.paginator(json_data, endpoint_value, params['start'], params['end'])
            if endpoint_value == 'activity/sleep':
                df = self.whoop_data_cleaner.clean_sleep_data(df)
            elif endpoint_value == 'activity/workout':
                df = self.whoop_data_cleaner.clean_workout_data(df)
            elif endpoint_value == 'recovery':
                df = self.whoop_data_cleaner.clean_recovery_data(df)
            else: 
                df = self.whoop_data_cleaner.clean_cycle_data(df)
                

            df.to_csv(f"data/{endpoint_key}_data.csv", index=False)
            self.whoop_database.upsert_data(df, endpoint_key)
        

   


if __name__ == '__main__':
    whoop_client = WhoopClient()
    whoop_db = WhoopDB()

    tokens = whoop_client.load_tokens()

    if tokens.get("expires_at", 0) <= int(time.time()):
        tokens = whoop_client.authorisation()
        tokens = whoop_client.load_tokens()


    whoop_ingestor = WhoopDataIngestor(tokens.get('access_token', 0))

    whoop_db.create_tables()
    sleep_data = whoop_ingestor.data_pipeline('2025-01-01T00:00:00.000Z', '2025-09-11T00:00:00.000Z')
   