import urllib.parse
from urllib.parse import urlparse, parse_qs
from whoop_pipeline.config import settings
from whoop_pipeline.database import WhoopDB
import requests
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import threading
import json
import os
import pandas as pd


class WhoopClient():
    def __init__(self, whoop_db=None):
        self.whoop_client_id = settings.whoop_client_id
        self.whoop_redirect_uri = settings.whoop_redirect_uri
        self.whoop_scope = settings.whoop_scope
        self.whoop_token_url = settings.whoop_token_url
        self.whoop_client_secret = settings.whoop_client_secret
        self.whoop_db = whoop_db or WhoopDB()

    def build_url_auth(self) -> str:
        """Build the URL for the OAuth2 authorization request."""

        params = {
            "response_type": "code", #Return the code from the auth server
            "client_id": self.whoop_client_id,
            "redirect_uri": str(self.whoop_redirect_uri), #casts from the pydantic AnyHttpUrl to str
            "scope": self.whoop_scope,
            "state": "random_state_string",
        }

        url = F"{settings.whoop_auth_url}?{urllib.parse.urlencode(params)}"

        return url
    
    def run_local_server_for_code(self, expected_state: str, timeout: int = 180) -> str:
        """Run a local server to capture the authorization code from the redirect."""

        parsed = urlparse(str(self.whoop_redirect_uri))
        host = parsed.hostname
        port = parsed.port
        path = parsed.path

        result = {"code": None, "state": None, "error": None}

        class AuthHandler(BaseHTTPRequestHandler):

            def do_GET(self):
                """Handle GET request to capture the authorization code."""
                parsed = urlparse(self.path)
                if parsed.path != path:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"Not Found")
                    return
                qs = parse_qs(parsed.query)
                result["code"] = qs.get("code", [None])[0]
                result["state"] = qs.get("state", [None])[0]
                result["error"] = qs.get("error", [None])[0]    
                
                self.send_response(200 if result["code"] else 400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body><h1>You can close this window now.</h1></body></html>")


            def log_message(self, *a, **k): 
                """Override to disable logging with a method that does nothing."""
                return
        

        httpd = HTTPServer((host, port), AuthHandler)
        try:
            t = threading.Thread(target=httpd.serve_forever, daemon=True)
            t.start()
            start_time = time.time()
            while time.time() -  start_time < timeout and not (result["code"] or result["error"]):
               time.sleep(0.1)
        finally:
            httpd.shutdown()
            httpd.server_close()

        if result["error"]:
            raise Exception(f"Error during authorization: {result['error']}")
        if result["state"] != expected_state:
            raise Exception("State mismatch. Possible CSRF attack.")
        if not result["code"]:
            raise Exception("No authorization code received.")
        
        return result["code"]


    def exchange_code_for_token(self, code: str) -> dict: #Return a dict of tokens
        """Exchange the authorization code for an access token."""

        # Headers must tell WHOOP we're sending form data
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Body of the POST request
        data = {
            "grant_type": "authorization_code",
            "code": code.strip(),
            "redirect_uri": str(self.whoop_redirect_uri),
            "client_id": self.whoop_client_id,
            "client_secret": self.whoop_client_secret,
            "scope": "offline",
        }

        response = requests.post(str(self.whoop_token_url), headers=headers, data=data)

        if response.status_code >= 400:
            print("STATUS:", response.status_code)
            print("URL:", str(settings.whoop_token_url))
            print("POSTED DATA:", {**data, "client_secret": "***masked***"})
            print("BODY:", response.text)   # <-- this tells us exactly what's wrong
            response.raise_for_status()
        return response.json()
    
    def refresh_access_token(self, tokens: dict) -> dict:
        """Refresh the access token using the refresh token."""
        
        refresh_token = tokens.get("refresh_token")
        if not refresh_token:
            raise ValueError("No refresh token available to refresh access token.")
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "refresh_token",
                "refresh_token": refresh_token.strip(),
                "client_id": self.whoop_client_id.strip(),
                "client_secret": self.whoop_client_secret.strip(),
                }

        response = requests.post(str(self.whoop_token_url), headers=headers, data=data)
        
        if response.status_code >= 400:
            print("STATUS:", response.status_code)
            print("URL:", str(settings.whoop_token_url))
            print("POSTED DATA:", {**data, "client_secret": "***masked***"})
            print("BODY:", response.text)   # <-- this tells us exactly what's wrong
            response.raise_for_status()
            return None

        return response.json()


    def authorisation(self):
        """Perform the OAuth2 authorization flow to obtain tokens."""
        auth_url = self.build_url_auth()
        webbrowser.open(auth_url)
        code = self.run_local_server_for_code(expected_state="random_state_string", timeout=180)
        tokens = self.exchange_code_for_token(code)
        
        return tokens
        
    def get_live_access_token(self):
        """Get a valid access token, refreshing it if necessary with OAuth."""      

        tokens = self.whoop_db.get_access_token(connection=None)
        if tokens == {}:
            tokens = self.authorisation()
            self.whoop_db.upsert_access_token(tokens, provider="whoop")

        elif int(time.time()) >= tokens.get('expires_at'):
            print("Access token expired or about to expire, refreshing...")
            tokens = self.refresh_access_token(tokens)
        
        else:
            print("Access token is still valid.")
        return tokens

if __name__ == "__main__":
    whoop_client = WhoopClient()
    whoop_client.get_live_access_token()