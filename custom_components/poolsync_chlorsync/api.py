import requests

LOGIN_URL = "https://lsx6q9luzh.execute-api.us-east-1.amazonaws.com/api/app/auth/login"

def login(email, password):
    """Connexion à l'API Cloud PoolSync et récupération du token."""
    payload = {
        "email": email,
        "password": password
    }
    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "user-agent": "Sync/522 CFNetwork/3826.500.131 Darwin/24.5.0",
        "accept-language": "fr-CA,fr;q=0.9",
        "accept-encoding": "gzip, deflate, br"
    }

    response = requests.post(LOGIN_URL, headers=headers, json=payload, timeout=10)
    response.raise_for_status()

    tokens = response.json().get("tokens")
    return tokens.get("access")
