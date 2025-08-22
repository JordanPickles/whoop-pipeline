import requests
from whoop_pipeline.config import settings


def exchange_code_for_token(code: str) -> dict:
    """Exchange the authorization code for an access token."""

     # Headers must tell WHOOP we're sending form data
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Body of the POST request
    data = {
        "grant_type": "authorization_code",
        "code": code.strip(),
        "redirect_uri": str(settings.whoop_redirect_uri),
        "client_id": settings.whoop_client_id,
        "client_secret": settings.whoop_client_secret,
    }

    
    response = requests.post(str(settings.whoop_token_url), headers=headers, data=data)

    if response.status_code >= 400:
        print("STATUS:", response.status_code)
        print("URL:", str(settings.whoop_token_url))
        print("POSTED DATA:", {**data, "client_secret": "***masked***"})
        print("BODY:", response.text)   # <-- this tells us exactly what's wrong
        response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    code = "G7RDrr7QC4poRgACQJ_o2YOIgI_uSjUwiOoU16caQfQ.7CRI-1ACCg4LHamMGowf86ECu_73JVzzLAuUKMUAgvE"

    tokens = exchange_code_for_token(code)

    print("\nToken response (summary):")
    print("  has access_token?  ", "access_token" in tokens)
    print("  has refresh_token? ", "refresh_token" in tokens)
    print("  expires_in (secs): ", tokens.get("expires_in"))
    print(tokens)
    print(tokens['access_token'])

