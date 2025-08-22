import requests


access_token = 'RJWY-vdiwOy2-uMbBDzdawb3zlX0wS8YJ0EvDisy3ac.USsiFLd8-pM891KOlrKI0THphBYF9wrf62-stPm0G8c'
headers = {"Authorization": f"Bearer {access_token}"}
resp = requests.get("https://api.prod.whoop.com/developer/v1/activity", headers=headers)
print(resp.json())
