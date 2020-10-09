import collections
from datetime import datetime
import functools
import itertools
import json
import multiprocessing as mp
import re
from typing import List, Union, Optional

import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import spacy
nlp = spacy.load('ja_ginza')


class QiitaItem:
    QIITA_URL_PATTERN = r"https://qiita.com/(?P<user_name>\w+)/items/(?P<item_id>\w+)"
    QIITA_URL_FORMAT = "https://qiita.com/{user_name}/items/{item_id}"
    IMG_PATTERN = r"!\[.*\]\(https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/[0-9]+/[0-9]+/[0-9a-z\-]+.png\)"
    LINK_PATTERN = r"\[.*\]\(https?://.+\)"
    CODE_PATTERN = r"```[\s\w\W]*```"

    def __init__(self, payload: dict):
        self.rendered_body: str = payload.get('rendered_body')
        self.body: str = payload.get('body')
        self.coediting: bool = payload.get('coediting')
        self.comments_count: str = payload.get('comments_count')
        self.created_at: str = payload.get('created_at')
        self.group = payload.get('group')
        self.id: str = payload.get('id')
        self.likes_count: int = payload.get('likes_count')
        self.private: bool = payload.get('private')
        self.reactions_count: int = payload.get('reactions_count')
        self.tags: List[dict] = payload.get('tags')
        self.title: str = payload.get('title')
        self.updated_at: str = payload.get('updated_at')
        self.url: str = payload.get('url')
        self.qiita_user = QiitaUser(payload=payload.get('user', {}))
        self.user_id = payload.get("user_id", self.qiita_user.id)
        self.permanent_id = payload.get("permanent_id", self.qiita_user.permanent_id)
        # additional
        self.image_num = self._image_count()
        self.qiita_refs: List[dict] = self._qiita_refs()
        self.qiita_refs_count = len(self.qiita_refs)

    def _image_count(self) -> int:
        """
        count attached-images in the article.

        Returns:

        """
        if self.body is None:
            return 0
        found_list = re.findall(self.IMG_PATTERN, self.body)
        return len(found_list)

    def _qiita_refs(self) -> List[dict]:
        """
        count references only from the Qiita to the Qiita

        Returns:

        """
        if self.body is None:
            return [{
                "user_name": "",
                "item_id": "",
                "url": ""
            }]
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
            f"    * tag: {', '.join(self.get_tags())}",
            f"    * length: {len(self.body)}",
            f"    * image_num: {self.image_num}",
            f"    * qiita_refs: {self.qiita_refs}",
            f"    * link: {self.url}",
        ]
        return "\n".join(response_list)

    def get_tags(self) -> list:
        return [i['name'] for i in self.tags]

    def is_tag_exist(self, tags: Union[str, List[str]]) -> bool:
        _tags = []
        if type(tags) is str:
            _tags.append(tags)
        elif type(tags) is list:
            _tags.extend(tags)
        if not _tags:
            return True

        item_tags = self.get_tags()
        for tag in _tags:
            if tag in item_tags:
                return True
        return False

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
            "tags": self.tags,
            "url": self.url,
            "body_length": len(self.body),
            "image_num": self.image_num,
            "qiita_refs_count": self.qiita_refs_count,
            "user_id": self.user_id,
            "permanent_id": self.permanent_id
        }
        if body:
            return_dict['rendered_body'] = self.rendered_body
            return_dict['body'] = self.body

        return return_dict

    def __str__(self):
        return self._to_str()

    def __repr__(self):
        return self._to_str()

    def _body_preprocess(self) -> List[str]:
        """
        vector化する前に文書中の、以下の項目を削除する
        * IMG
        * LINK
        * CODE

        Returns:

        """
        _body = self.body
        _body = re.sub(self.IMG_PATTERN, "", _body)
        _body = re.sub(self.LINK_PATTERN, "", _body)
        _body = re.sub(self.CODE_PATTERN, "", _body)

        body_text = _body.split("\n")
        body_text = [text for text in body_text if len(text) > 0]
        return body_text

    def to_vector(self):
        body_text = self._body_preprocess()
        docs = list(nlp.pipe(body_text))
        return functools.reduce(lambda x, y: x + y, [d.vector for d in docs])


class QiitaUser:
    def __init__(self, payload: dict):
        self.description: str = payload.get('description')
        self.facebook_id: str = payload.get('facebook_id')
        self.followees_count: int = payload.get('followees_count')
        self.followers_count: int = payload.get('followers_count')
        self.github_login_name: Optional[str] = payload.get('github_login_name')
        self.id: int = payload.get('id')
        self.items_count: int = payload.get('items_count')
        self.linkedin_id: str = payload.get('linkedin_id')
        self.location: str = payload.get('location')
        self.name: str = payload.get('name')
        self.organization = payload.get('organization')
        self.permanent_id: int = payload.get('permanent_id')
        self.profile_image_url: str = payload.get('profile_image_url')
        self.team_only: bool = payload.get('team_only')
        self.twitter_screen_name: str = payload.get('twitter_screen_name')
        self.website_url: str = payload.get('website_url')


class QiitaItemBox:
    def __init__(self):
        self.item_list: List[QiitaItem] = []

    @staticmethod
    def read_json(path) -> Union[dict, List[dict]]:
        """

        Args:
            path: a path to the target_json

        Returns:
            dict contains qiita item information
        """
        with open(path, "r") as f:
            data = json.load(f)
        return data

    def extend_files(self, file_list: List[str]) -> None:
        """
        read json-files using multiprocessing

        Args:
            file_list: ["./dir/data1.json", ...]

        Returns:
            None

        Examples:
            >>> item_box = QiitaItemBox()
            >>> item_box.extend_files(file_list=["./dir/data1.json", "./dir/data2.json"])
        """
        with mp.Pool(mp.cpu_count()) as pool:
            result = pool.map(self.read_json, file_list)
        for r in result:
            self.extend(r)

    def dumps(self, body=False) -> List[dict]:
        return [item.dumps(body=body) for item in self.item_list]

    def append(self, item: Union[dict, QiitaItem]) -> None:
        """
        append `dict` or `QiitaItem()` to the QiitaItemBox()

        Args:
            item:

        Returns:
            None
        """
        if type(item) is dict:
            self.item_list.append(QiitaItem(item))
        elif type(item) is QiitaItem:
            self.item_list.append(item)
        else:
            raise Exception

    def extend(self, item_list: Union[List[dict], List[QiitaItem]]):
        """
        extend `List[dict]` or List[QiitaItem()]` to the QiitaItemBox()

        Args:
            item_list:

        Returns:
            None
        """
        for item in item_list:
            self.append(item)

    def get_item_list(
            self,
            tags: Optional[Union[str, List[str]]] = None,
            likes: Optional[int] = 0
    ) -> List[QiitaItem]:
        """
        get qiita_item_list

        Args:
            tags: filter the items which contains `tags`
            likes: filter the items which has `LGTM` more than `likes`

        Returns:

        """
        _tags: List[str] = []
        if tags is not None:
            if type(tags) is str:
                _tags.append(tags)
            elif type(tags) is list:
                _tags.extend(tags)

        return [
            item for item in self.item_list
            if item.is_tag_exist(tags=_tags) and
            item.likes_count >= likes
        ]

    def get_as_df(
            self,
            tags: Optional[Union[str, List[str]]] = None,
            likes: Optional[int] = 0
    ) -> pd.DataFrame:
        item_list = self.get_item_list(tags=tags, likes=likes)
        item_dict_list = [item.dumps() for item in item_list]
        df = pd.DataFrame(item_dict_list)

        # tags is stored as list
        df = df.explode("tags")
        df['tag'] = df['tags'].apply(lambda x: x['name'])

        # count tag appeared in the df above
        tag_count_df = df.groupby("tag", as_index=False).count()
        tag_count_df = tag_count_df.rename(columns={"id": "tag_count"}).loc[:, ["tag", "tag_count"]]

        merged = pd.merge(df, tag_count_df, on="tag", how="left")
        select_cols = ["title", "id", "updated_at", "likes_count", "tag", "tag_count", "body_length", "image_num"]
        return merged.loc[:, select_cols]

    def create_tag_graph(
            self,
            tags: Union[str, List[str]],
            common_n: int = 50,
            weight_more_than: int = 5,
            font_family: str = "Hiragino Maru Gothic Pro"
    ):
        # [ ["tag1", "tag2"], ["tag1"], ["tag3"]]
        tag_list = []
        for i in self.get_item_list(tags=tags):
            tag_list.append(i.get_tags())

        # [('Python', 11433),
        #  ('Python3', 3085)]
        tag_count = collections.Counter(itertools.chain.from_iterable(tag_list)).most_common(common_n)

        # add nodes
        graph = nx.Graph()
        graph.add_nodes_from([(tag, {"count": count}) for tag, count in tag_count])

        # add edge weight
        for tags in tag_list:
            for node0, node1 in itertools.combinations(tags, 2):
                if not graph.has_node(node0) or not graph.has_node(node1):
                    continue
                if graph.has_edge(node0, node1):
                    graph[node0][node1]["weight"] += 1
                else:
                    graph.add_edge(node0, node1, weight=1)

        # remove light-weighted edge
        remove_edge_list = []
        for (u, v, d) in graph.edges(data=True):
            if d["weight"] < weight_more_than:
                remove_edge_list.append((u, v))
        for (u, v) in remove_edge_list:
            graph.remove_edge(u, v)

        # 反発係数とか
        plt.figure(figsize=(16, 16))
        pos = nx.spring_layout(graph, k=0.3)
        # ノードの大きさと日本語
        node_size = [d["count"] * 10 for (n, d) in graph.nodes(data=True)]
        nx.draw_networkx_nodes(graph, pos, node_color="w", alpha=0.8, node_size=node_size, edgecolors="g")
        nx.draw_networkx_labels(graph, pos, font_size=14, font_family=font_family, font_weight="bold")
        # weightに応じたedgeの太さ
        edge_width = [d["weight"] * 0.2 for (u, v, d) in graph.edges(data=True)]
        nx.draw_networkx_edges(graph, pos, alpha=0.4, edge_color="c", width=edge_width)
        return plt

    def __add__(self, other):
        new_item_box = QiitaItemBox()
        new_item_box.extend(self.item_list)
        new_item_box.extend(other.item_list)
        return new_item_box

    def __radd__(self, other):
        return self.__add__(other=other)

    def __len__(self):
        return len(self.item_list)
