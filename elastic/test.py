from datetime import datetime
from elasticsearch import Elasticsearch
es = Elasticsearch('https://elastic.åt.se:443')

doc = {
    'author': 'author_name',
    'text': 'Interesting content...',
    'timestamp': datetime.now(),
}
resp = es.index(index="test-index", document=doc)
print(resp['result'])

# Get document
resp = es.get(index="test-index", id=resp['_id'])
print(resp['_source'])

# Refresh index
es.indices.refresh(index="test-index")

# Search
resp = es.search(index="test-index", query={"match_all": {}})
print("Got %d Hits:" % resp['hits']['total']['value'])
for hit in resp['hits']['hits']:
    print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])
