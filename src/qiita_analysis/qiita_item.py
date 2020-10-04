from datetime import datetime
import re
from typing import List, Union


class QiitaItem:
    QIITA_URL_PATTERN = r"https://qiita.com/(?P<user_name>\w+)/items/(?P<item_id>\w+)"
    QIITA_URL_FORMAT = "https://qiita.com/{user_name}/items/{item_id}"

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
        # additional
        self.image_num = self._image_count()
        self.qiita_refs: List[dict] = self._qiita_refs()
        self.qiita_refs_count = len(self.qiita_refs)

    def _image_count(self) -> int:
        """
        count attached-images in the article.

        Returns:

        """
        pattern = r"!\[.*\]\(https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/[0-9]+/[0-9]+/[0-9a-z\-]+.png\)"
        found_list = re.findall(pattern, self.body)
        return len(found_list)

    def _qiita_refs(self) -> List[dict]:
        """
        count references only from the Qiita to the Qiita

        Returns:

        """
        found_list = re.findall(self.QIITA_URL_PATTERN, self.body)

        found_dict = [
            {
                "user_name": user_name,
                "item_id": item_id,
                "url": self.QIITA_URL_FORMAT.format(user_name=user_name, item_id=item_id)
            }
            for user_name, item_id in found_list
        ]
        return found_dict

    def _to_str(self) -> str:
        updated_at = datetime.fromisoformat(self.updated_at)
        response_list = [
            f"LGTM=[{self.likes_count:>5}]({updated_at.strftime('%Y-%m-%d')})【{self.title}】",
            f"    * tag: {', '.join([i['name'] for i in self.tags])}",
            f"    * length: {len(self.body)}",
            f"    * image_num: {self.image_num}",
            f"    * qiita_refs: {self.qiita_refs}",
            f"    * link: {self.url}",
        ]
        return "\n".join(response_list)

    def dumps(self, body=False) -> dict:
        """

        Args:
            body: Also dumps with `body` and `rendered body`

        Returns:

        """

        return_dict = {
            "title": self.title,
            "id": self.id,
            "create_at": self.created_at,
            "updated_at": self.updated_at,
            "likes_count": self.likes_count,
            "url": self.url,
            "body_length": len(self.body),
            "image_num": self.image_num,
            "qiita_refs_count": self.qiita_refs_count
        }
        if body:
            return_dict['rendered_body'] = self.rendered_body
            return_dict['body'] = self.body

        return return_dict

    def __str__(self):
        return self._to_str()

    def __repr__(self):
        return self._to_str()


class QiitaUser:
    def __init__(self, payload: dict):
        self.description: str = payload['description']
        self.facebook_id: str = payload['facebook_id']
        self.followees_count: int = payload['followees_count']
        self.followers_count: int = payload['followers_count']
        self.github_login_name: Optional[str] = payload['github_login_name']
        self.id: int = payload['id']
        self.items_count: int = payload['items_count']
        self.linkedin_id: str = payload['linkedin_id']
        self.location: str = payload['location']
        self.name: str = payload['name']
        self.organization = payload['organization']
        self.permanent_id: int = payload['permanent_id']
        self.profile_image_url: str = payload['profile_image_url']
        self.team_only: bool = payload['team_only']
        self.twitter_screen_name: str = payload['twitter_screen_name']
        self.website_url: str = payload['website_url']


class QiitaItemBox:
    def __init__(self):
        self.item_list: List[QiitaItem] = []

    def dumps(self, body=False) -> List[dict]:
        return [item.dumps(body=body) for item in self.item_list]

    def append(self, item: Union[dict, QiitaItem]):
        if type(item) is dict:
            self.item_list.append(QiitaItem(item))
        elif type(item) is QiitaItem:
            self.item_list.append(item)
        else:
            raise Exception

    def extend(self, item_list: Union[List[dict], List[QiitaItem]]):
        for item in item_list:
            self.append(item)
