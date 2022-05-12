import requests as r
from json.decoder import JSONDecodeError


def send_request(method: str, url: str) -> dict:
    """Send api request and check the answer"""
    # Define mapping: string arg to requests function
    method_map = {
        'get': r.get,
        'post': r.post,
        'delete': r.delete
    }
    # Send request to api and verify response
    try:
        resp = method_map[method](url)
        if resp.status_code in [200, 201, 204]:
            resp = resp.json()
        else:
            resp = {'errors': 'Wrong response from API: ' + resp.json()}
    except r.exceptions.ConnectionError as e:
        resp = {'errors': 'No response from API: ' + str(e)}
    except JSONDecodeError as e:
        resp = {'errors': 'Wrong response from API: ' + str(e)}

    return resp
