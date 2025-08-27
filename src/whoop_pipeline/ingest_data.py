import requests
import json
from whoop_pipeline.config import settings
from whoop_pipeline.auth import WhoopClient
import pandas as pd





class WhoopDataIngestor():
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = settings.whoop_api_base_url
        
        

    def get_recovery_data(self, start, end) -> pd.DataFrame:
        """Fetch recovery data from Whoop API."""

        access_token = self.access_token
        response_json_list = []

        endpoint = f"{self.base_url}recovery?start={start}&end={end}"
        headers = {
            "Authorization": f"Bearer {access_token}"
            , "Accept": "application/json"
        }  
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        records = response_json.get("records", [])
        response_json_list.extend(records)
        next_access_token = response_json.get("next_token")

        while next_access_token is not None:
            
            print("Fetching next page of data with token:", next_access_token)
            endpoint = f"{self.base_url}recovery?nextToken={next_access_token}&start={start}&end={end}"
            headers = {
                "Authorization": f"Bearer {access_token}"
                , "Accept": "application/json"
            }   
        
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            records = response_json.get("records", [])

            response_json_list.extend(records)

            next_access_token = response_json.get("next_token")
        
        df_recovery =  pd.json_normalize(response_json_list)
        
        return df_recovery

if __name__ == '__main__':
    whoop_client = WhoopClient()
    
    tokens = whoop_client.load_tokens()
    access_token = tokens['access_token']
    whoop_ingestor = WhoopDataIngestor(access_token)

    recovery_data = whoop_ingestor.get_recovery_data('2025-08-14T00:00:00.000Z', '2025-08-27T00:00:00.000Z')
    print(recovery_data)