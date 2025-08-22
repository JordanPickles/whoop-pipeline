# src/whoop_pipeline/test.py
import os
import requests
from whoop_pipeline.config import settings
from whoop_pipeline.refresh import refresh_access_token

def get_access_token() -> str:
    rt = os.getenv("WHOOP_REFRESH_TOKEN")
    if not rt:
        raise RuntimeError("Missing WHOOP_REFRESH_TOKEN in your environment/.env")
    js = refresh_access_token(rt)  # gets a fresh access_token
    return js["access_token"]

def safe_get(url: str, params=None):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    resp = requests.get(url, headers=headers, params=params or {}, timeout=30)

    # Always print diagnostics first
    print("STATUS:", resp.status_code)
    print("Content-Type:", resp.headers.get("Content-Type"))
    print("URL:", resp.url)
    print("Preview:", resp.text[:300], "...\n")

    # If not 2xx, raise so you see the server message
    resp.raise_for_status()

    # Ensure it's JSON before parsing
    if "application/json" not in (resp.headers.get("Content-Type") or ""):
        raise ValueError("Response is not JSON; cannot parse with .json()")
    return resp.json()

if __name__ == "__main__":
    # Adjust base + path to a valid WHOOP endpoint per docs
    base = (settings.whoop_api_base or "https://api.prod.whoop.com/developer").rstrip("/")
    url = f"{base}/users/me"   # <- Replace with a confirmed JSON endpoint if needed
    data = safe_get(url)
    print("JSON keys:", list(data)[:20])