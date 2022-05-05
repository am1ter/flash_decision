import requests as r


def send_request(method: str, url: str) -> str:
    """Send api request and check the answer"""
    # Define mapping: string arg to requests function
    method_map = {
        'get': r.get,
        'post': r.post,
        'delete': r.delete
    }
    try:
        resp = method_map[method](url)
        if resp.status_code == 200:
            result = True
        else:
            result = False
    except r.exceptions.ConnectionError as e:
        result = 'No response from API: ' + str(e)

    return result
