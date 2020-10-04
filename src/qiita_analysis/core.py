import requests
from typing import Optional

from .utils import get_item, header
from .error import QiitaTokenInvalidError, QiitaGetItemError
from .qiita_item import QiitaItemBox


class QiitaClient:

    SLEEP_SEC = 1

    def __init__(self, qiita_token: Optional[str] = None):
        self.qiita_token = qiita_token
        self.token_rate_remaining = 1000
        self.qiita_item_box = QiitaItemBox()

    def get_item_at(self, target_date: str):
        result_list = []
        if self.qiita_token is None:
            raise QiitaTokenInvalidError("your Qiita Token is None")

        response = get_item(start_date=target_date, end_date=target_date, qiita_token=self.qiita_token)
        self.token_rate_remaining = response.headers['Rate-Remaining']
        result_list.extend(response.json())
        total_count = int(response.headers['Total-Count'])

        first_url = response.links['first']['url']
        next_url = response.links['next']['url']
        last_url = response.links['last']['url']
        if first_url == last_url:
            if len(result_list) != total_count:
                raise QiitaGetItemError("想定した数と異なります")
            self.qiita_item_box.extend(result_list)
            return result_list
        while True:
            response = requests.get(next_url, headers=header(qiita_token=self.qiita_token))
            self.token_rate_remaining = response.headers['Rate-Remaining']
            result_list.extend(response.json())

            if next_url == last_url:
                break
            next_url = response.links['next']['url']
            last_url = response.links['last']['url']

        if len(result_list) != total_count:
            raise QiitaGetItemError("想定した数と異なります")
        self.qiita_item_box.extend(result_list)
        return result_list
