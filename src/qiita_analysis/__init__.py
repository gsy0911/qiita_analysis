import requests


def get_item(start_date: str, end_date: str, authorization: str):
    """

    Args:
        start_date: %Y-%m-%d
        end_date: %Y-%m-%d
        authorization:

    Returns:

    """
    # in order not to over the limitation accessing 1000 times in one hour
    sleep_sec = 3.6
    url = 'https://qiita.com/api/v2/items'

    p = {
        "per_page": 100,
        "page": 1,
        "query": f"created:>={start_date} created:<={end_date}"
    }


    r = requests.get(url, params=p, headers=_header(authorization=authorization))
    # print("remaining : " + str(r.headers['Rate-Remaining']))
    return r.json()


def _header(authorization):
    """
    get qiita header with specific header
    """
    return {
        "Authorization": f"Bearer {authorization}",
        "content-type": "application/json"
    }
