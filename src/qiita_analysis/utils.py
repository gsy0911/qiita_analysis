import requests


def get_item(
        start_date: str,
        end_date: str,
        qiita_token: str,
        page: int = 1):
    """

    Args:
        start_date: %Y-%m-%d
        end_date: %Y-%m-%d
        qiita_token:
        page

    Returns:

    """
    url = 'https://qiita.com/api/v2/items'

    p = {
        "per_page": 100,
        "page": page,
        "query": f"created:>={start_date} created:<={end_date}"
    }

    return requests.get(url, params=p, headers=header(qiita_token=qiita_token))


def header(qiita_token):
    """
    get qiita header with specific header
    """
    return {
        "Authorization": f"Bearer {qiita_token}",
        "content-type": "application/json"
    }
