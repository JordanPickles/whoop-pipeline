import urllib.parse
from whoop_pipeline.config import settings, WHOOP_SCOPES
import requests
import webbrowser


def buidl_url_auth():
    """Build the URL for the OAuth2 authorization request."""
    print(settings.whoop_client_id)
    params = {
        "response_type": "code",
        "client_id": settings.whoop_client_id,
        "redirect_uri": settings.whoop_redirect_uri,
        "scope": WHOOP_SCOPES,
        "state": "random_state_string",
    }
    print(params)
    url = F"{settings.whoop_auth_url}?{urllib.parse.urlencode(params)}"


    return url
if __name__ == "__main__":
    print(buidl_url_auth())

    webbrowser.open(buidl_url_auth())