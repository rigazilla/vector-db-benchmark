import json
import threading
from typing import List, Optional

import httpx

from engine.base_client.upload import BaseUploader
from engine.clients.infinispan.config import *
import zlib

class InfinispanUploader(BaseUploader):
    conn = None
    cur = None
    upload_params = {}
    host = None

    @classmethod
    def init_client(cls, host, distance, connection_params, upload_params):
        cls.host = host
        cls.h2c = httpx.Client(http2=True, http1=False)
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
                    #compress = zlib.compressobj(wbits=16 + zlib.MAX_WBITS)
                    #body = zlib.compress(data_str.encode())
                    response = cls.h2c.put(req_str_tpl % i,
                                            data=data_str,
                                            headers={
                                                "Content-Type": "application/json",
                                                #"Content-Encoding": "gzip"
                                            },
                                            timeout=infinispan_timeout,
                                            )
                    if response.status_code != httpx.codes.OK:
                        break
                except Exception as ex:
                    print(ex)
                    pass
                if repeat >= 10:
                    raise Exception("too many failures, giving up")
                print("%d: Failure server side, retrying..." % threading.get_native_id())
                repeat += 1
                continue

    @classmethod
    def post_upload(cls, distance):
        req_str = infinispan_base_url(cls.host) + "/caches/items/search/indexes?action=reindex"
        response = cls.h2c.post(req_str,
                                 timeout=infinispan_timeout*1000
                                 )
        print(response)
        return {}

    @classmethod
    def delete_client(cls):
        try:
            cls.h2c.close()
        except:
            return
        return
