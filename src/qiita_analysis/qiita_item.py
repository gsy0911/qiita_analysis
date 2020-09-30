from datetime import datetime
import re
from typing import List


class QiitaItem:
    def __init__(self, payload: dict):
        self.rendered_body: str = payload['rendered_body']
        self.body: str = payload['body']
        self.coediting: bool = payload['coediting']
        self.comments_count: str = payload['comments_count']
        self.created_at: str = payload['created_at']
        self.group = payload['group']
        self.id: str = payload['id']
        self.likes_count: int = payload['likes_count']
        self.private: bool = payload['private']
        self.reactions_count: int = payload['reactions_count']
        self.tags: List[dict] = payload['tags']
        self.title: str = payload['title']
        self.updated_at: str = payload['updated_at']
        self.url: str = payload['url']

    def _to_str(self) -> str:
        updated_at = datetime.fromisoformat(self.updated_at)
        response_list = [
            f"LGTM=[{self.likes_count:>5}]({updated_at.strftime('%Y-%m-%d')})【{self.title}】",
            f"    * tag: {', '.join([i['name'] for i in self.tags])}",
            f"    * length: {len(self.body)}"
        ]
        return "\n".join(response_list)

    def __str__(self):
        return self._to_str()

    def __repr__(self):
        return self._to_str()
