import json
from typing import List, Tuple

import requests

from engine.base_client.search import BaseSearcher
from engine.clients.infinispan.config import *
from engine.clients.infinispan.parser import InfinispanConditionParser


class InfinispanSearcher(BaseSearcher):
    conn = None
    cur = None
    distance = None
    search_params = {}
    parser = InfinispanConditionParser() # TODO: Implement metadata subfilters

    @classmethod
    def init_client(cls, host, distance, connection_params: dict, search_params: dict):
        return

    @classmethod
    def search_one(cls, vector, meta_conditions, top) -> List[Tuple[int, float]]:
        # TODO: raise NotImplementedError for not implemented metrics
        query_str_tpl = "select id, score(v) from vectors v where v.vector <-> %s~%d"
        query_str = query_str_tpl % (json.dumps(vector), top)
        req_str = infinispan_base_url + "/caches/items?action=search&local=False"
        data = {"query": query_str, "max_results": top}
        data_json = json.dumps(data)
        query_res = requests.post(url=req_str, data=data_json,
                                   headers={"Content-Type": "application/json;charset=UTF-8",
                                            "Accept": "application/json; q=0.01",
                                            "Accept-Encoding": "identity"
                                            },
                                   timeout=infinispan_timeout,
                                   )
        result_set = json.loads(query_res.text)
        result = []
        for row in result_set["hits"]:
            hit = row["hit"] or {}
            result.append((hit.get("id"), hit.get("score(v)")))
        return result

    @classmethod
    def delete_client(cls):
        return
