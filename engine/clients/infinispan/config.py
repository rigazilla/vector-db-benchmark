import os
INFINISPAN_PORT = int(os.getenv("INFINISPAN_PORT", 11222))
INFINISPAN_SCHEMA = str(os.getenv("INFINISPAN_SCHEMA", "http"))
INFINISPAN_HOST = str(os.getenv("INFINISPAN_HOST", "localhost"))
infinispan_base_url = ("%s://%s:%d/rest/v2"
                       % (INFINISPAN_SCHEMA, INFINISPAN_HOST, INFINISPAN_PORT))
infinispan_timeout = 10
infinispan_cache_config = (
        '''
    {
"distributed-cache": {
"owners": "2",
"mode": "SYNC",
"statistics": true,
"encoding": {
"media-type": "application/x-protostream"
},
"indexing": {
"enabled": true,
"storage": "filesystem",
"startup-mode": "AUTO",
"indexing-mode": "MANUAL",
"indexed-entities": [ "vectors" ]
    }
  }
}
'''
)
infinispan_local_cache_config = (
        '''
    {
"local-cache": {
"statistics": true,
"encoding": {
"media-type": "application/x-protostream"
},
"indexing": {
"enabled": true,
"storage": "filesystem",
"startup-mode": "AUTO",
"indexing-mode": "AUTO",
"indexed-entities": [ "vectors" ]
    }
  }
}
'''
)
infinispan_schema_proto_tpl = """
/**
* @Indexed
*/
message vectors {
/**
* @Vector(
*       dimension=%d, 
*       similarity=org.infinispan.api.annotations.indexing.option.VectorSimilarity.%s,
*       maxConnections=%d,
*       beamWidth=%d
*       )
*/
repeated float vector = 1;
optional int32 id = 2;
}
"""

def infinispan_base_url(host: str) -> str:
        return("%s://%s:%d/rest/v2"
                       % (INFINISPAN_SCHEMA, host or INFINISPAN_HOST, INFINISPAN_PORT))
