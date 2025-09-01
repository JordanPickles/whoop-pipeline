import requests
import json
from whoop_pipeline.config import settings
from whoop_pipeline.auth import WhoopClient
import pandas as pd
import time


class WhoopDataIngestor():
    def __init__(self, access_token:str):
        self.access_token = access_token
        self.base_url = settings.whoop_api_base_url
        

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
    
    def paginator(self, json_data: dict, endpoint: str, start:str, end:str, ) -> pd.DataFrame:
        """Handles pagination for Whoop API responses."""

        data = json_data["records"]
        response_json_list = [data]
        next_access_token = json_data.get("next_token")

        while next_access_token is not None:
            
            
            print("Fetching next page of data with token:", next_access_token)
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
            records = response_json["records"]
            response_json_list.extend(records)

            next_access_token = response_json.get("next_token")
        
        df =  pd.json_normalize(response_json_list[0])
        return df


    def data_retrieval(self, start:str, end:str):
        """Retrieves data from Whoop API and saves to CSV files."""

        endpoints = {'recovery': 'recovery', 'sleep':'activity/sleep', 'workout': 'activity/workout'}  
        params = {'start': start, 'end': end}

        for endpoint in endpoints.values(): 
            json_data = self.get_json(self.base_url, endpoint, params, self.access_token)   
            df = self.paginator(json_data, endpoint, params['start'], params['end'])
            endpoint = endpoint.replace('/', '_')
            df.to_csv(f"data/{endpoint}_data.csv", index=False)
        




if __name__ == '__main__':
    whoop_client = WhoopClient()

    tokens = whoop_client.load_tokens()

    if tokens.get("expires_at", 0) <= int(time.time()):
        tokens = whoop_client.authorisation()
        tokens = whoop_client.load_tokens()


 
    whoop_ingestor = WhoopDataIngestor(tokens.get('access_token', 0))

    whoop_ingestor.data_retrieval('2025-08-14T00:00:00.000Z', '2025-08-27T00:00:00.000Z')
   