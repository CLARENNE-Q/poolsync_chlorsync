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

def change_chlor_output(access_token: str, hub_id: str, device_index: int, new_output: int) -> bool:
    """Change le chlorOutput d’un appareil ChlorSync."""
    url = f"https://lsx6q9luzh.execute-api.us-east-1.amazonaws.com/api/app/things/{hub_id}"
    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "authorization": access_token,
        "user-agent": "Sync/522 CFNetwork/3826.500.131 Darwin/24.5.0",
        "accept-language": "fr-CA,fr;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }
    payload = {
        "devices": {
            str(device_index): {
                "config": {
                    "chlorOutput": new_output
                }
            }
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 200
