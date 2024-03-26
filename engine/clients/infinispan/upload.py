import json
import threading
from typing import List, Optional

import numpy as np
import requests

from engine.base_client.upload import BaseUploader
from engine.clients.infinispan.config import *


class InfinispanUploader(BaseUploader):
    conn = None
    cur = None
    upload_params = {}
    host = None

    @classmethod
    def init_client(cls, host, distance, connection_params, upload_params):
        cls.host = host
        return

    @classmethod
    def upload_batch(
            cls, ids: List[int], vectors: List[list], metadata: Optional[List[dict]]
    ):

        req_str_tpl = infinispan_base_url(cls.host) + "/caches/items/%d"
        for i, embedding in zip(ids, vectors):
            data = {"_type": "vectors", "vector": embedding, "id": i}
            data_str = json.dumps(data)
            repeat = 0
            while True:
                try:
                    response = requests.put(req_str_tpl % i,
                                            data=data_str,
                                            headers={"Content-Type": "application/json"},
                                            timeout=infinispan_timeout,
                                            )
                    if response.ok:
                        break
                except:
                    pass
                if repeat >= 10:
                    raise Exception("too many failures, giving up")
                print("%d: Failure server side, retrying..." % threading.get_native_id())
                repeat += 1
                continue

    @classmethod
    def post_upload(cls, distance):
        req_str = infinispan_base_url(cls.host) + "/caches/items/search/indexes?action=reindex"
        response = requests.post(req_str,
                                 timeout=infinispan_timeout*1000
                                 )
        print(response)
        return {}

    @classmethod
    def delete_client(cls):
        return
