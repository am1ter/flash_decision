import requests as r


def send_request(url: str) -> str:
    """Send api request and check the answer"""
    try:
        resp = r.get(url)
        if resp.status_code == 200:
            result = True
        else:
            result = False
    except r.exceptions.ConnectionError as e:
        result = 'No response from API: ' + str(e)

    return result
