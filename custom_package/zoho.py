import requests


def refresh_access_token(refresh_token: str, client_id: str, client_secret: str, scope: str) -> str | None:
    """
    Use to refresh an access token from Zoho.

    :param refresh_token:
    :param client_secret:
    :param client_id:
    :param scope:

    :return: Returns an access token valid for 1 hour
    """

    url = "https://accounts.zoho.com/oauth/v2/token"

    params = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope,
        "redirect_uri": "https://www.zylker.com/oauthgrant",
        "grant_type": "refresh_token"
    }

    response = requests.post(url, params=params)

    if response.status_code != 200:
        print(f"Failed to get the access token. Reason: {response.reason}")
        return None

    result = response.json()

    return result["access_token"]
