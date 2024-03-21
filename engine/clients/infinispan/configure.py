import requests

from benchmark.dataset import Dataset
from engine.base_client.configure import BaseConfigurator
from engine.clients.infinispan.config import *
from engine.base_client.distances import Distance


class InfinispanConfigurator(BaseConfigurator):
    DISTANCE_MAPPING = {
            Distance.L2: "L2",
            Distance.COSINE: "COSINE",
            Distance.DOT: "INNER_PRODUCT"
        }

    def __init__(self, host, collection_params: dict, connection_params: dict):
        super().__init__(host, collection_params, connection_params)

    def clean(self):
        base_url = infinispan_base_url(self.host)
        req_str = base_url + "/caches/items"
        base_url = infinispan_base_url(self.host)
        response = requests.delete(req_str, timeout=infinispan_timeout)
        assert response.ok or response.status_code == 404
        req_str = base_url + "/schemas/vector.proto"
        response = requests.delete(req_str, timeout=infinispan_timeout)
        assert response.ok or response.status_code == 404

    def recreate(self, dataset: Dataset, collection_params):
        # TODO: raise IncompatibilityError for not implemented metrics
        base_url = infinispan_base_url(self.host)
        req_str = base_url + "/schemas/vector.proto"
        infinispan_schema_proto = (infinispan_schema_proto_tpl
                                   % (dataset.config.vector_size,
                                     self.DISTANCE_MAPPING[dataset.config.distance],
                                     collection_params["index_options"]['m'],
                                     collection_params["index_options"]['ef_construction']))
        response = requests.post(req_str, infinispan_schema_proto,
                                 headers={"Content-Type": "application/json"},
                                 timeout=infinispan_timeout,
                                 )
        assert response.ok
        req_str = base_url + "/caches/items"
        response = requests.post(req_str, infinispan_local_cache_config,
                                 headers={"Content-Type": "application/json"},
                                 timeout=infinispan_timeout,
                                 )
        assert response.ok
        req_str = base_url + "/caches/items/search/indexes?action=clear"
        response = requests.post(req_str,
                                 headers={"Content-Type": "application/json"},
                                 timeout=infinispan_timeout,
                                 )

    def delete_client(self):
        return
