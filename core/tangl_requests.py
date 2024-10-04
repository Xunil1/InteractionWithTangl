import requests


def get_attr(url: str, auth_token: str) -> dict:
    head = {'Content-Type': 'text/plain', "Authorization": "Bearer " + auth_token}
    req = requests.get(url, headers=head)

    try:
        res = req.json()
    except:
        res = req.text

    return res