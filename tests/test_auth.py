from whoop_pipeline.auth import WhoopClient
from whoop_pipeline.config import settings
import pandas as pd
import numpy as np
from urllib.parse import urlparse, parse_qs
import requests




class TestWhoopAuth():

    def setup_method(self, method):
        self.whoop_client = WhoopClient()
        self.whoop_client_id = settings.whoop_client_id
        self.whoop_redirect_uri = settings.whoop_redirect_uri
        self.whoop_scope = settings.whoop_scope
        self.whoop_token_url = settings.whoop_token_url
        self.whoop_client_secret = settings.whoop_client_secret

    def teardown_method(self, method):
        pass

    def test_build_url_auth(self):
        url_output = self.whoop_client.build_url_auth()
        parsed = urlparse(url_output)
        query_params = parse_qs(parsed.query)

        assert parsed.scheme == "https"
        assert query_params["response_type"][0] == "code"
        assert query_params["client_id"][0] == settings.whoop_client_id
        assert query_params["redirect_uri"][0] == str(settings.whoop_redirect_uri)
        assert query_params["scope"][0] == settings.whoop_scope
        assert query_params["state"][0] == "random_state_string"


    def test_exchange_code_for_token(self, mocker):
        mock_return = {
            "access_token": "GcBDG5zC9M2RKpIe3JnsrNTifsgt17CZhdzRM6eqygM.CeaTlH6hv-rtmnqPWLYM5eLyIWYfA7yfP1eMaye275U", 
             "expires_in": 3600, 
             "refresh_token": "EAS6VUaSbz6oF3Mdb6tAZVZ0ahi8SWhVOAkfIpytPt4.wWI9tSZTDTaDenagvZEJvF7hu94S_aHZAcJ1dNMF0Rg",
              "scope": "offline read:recovery read:cycles read:sleep read:workout read:profile read:body_measurement", 
              "token_type": "bearer",
            }
        
        mock_post = mocker.patch("whoop_pipeline.auth.requests.post")
        mock_post.return_value.status_code = 200
        
        mock_post.return_value.json.return_value = mock_return
        
        result = self.whoop_client.exchange_code_for_token("test_code")
        print(result)
        assert result == mock_return
        mock_post.assert_called_once()

    def test_refresh_access_token(self, mocker):
        mock_tokens = {
            "access_token": "GcBDG5zC9M2RKpIe3JnsrNTifsgt17CZhdzRM6eqygM.CeaTlH6hv-rtmnqPWLYM5eLyIWYfA7yfP1eMaye275U", 
             "expires_in": 3600, 
             "refresh_token": "EAS6VUaSbz6oF3Mdb6tAZVZ0ahi8SWhVOAkfIpytPt4.wWI9tSZTDTaDenagvZEJvF7hu94S_aHZAcJ1dNMF0Rg",
              "scope": "offline read:recovery read:cycles read:sleep read:workout read:profile read:body_measurement", 
              "token_type": "bearer",
            }

        mock_post = mocker.patch("whoop_pipeline.auth.requests.post")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_tokens
        
        result = self.whoop_client.refresh_access_token(mock_tokens)
        assert result == mock_tokens
        mock_post.assert_called_once()