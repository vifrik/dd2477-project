from elasticsearch import Elasticsearch, BadRequestError
import json

from parserhelper import ParserHelper

import os
from dotenv import load_dotenv
load_dotenv()

class Elastic:
    def __init__(self, index):
        self.index = index  # sample-index
        self.es = Elasticsearch("https://elastic.åt.se:443", basic_auth=(os.getenv("AUTH_USER"), os.getenv("AUTH_PASSWORD")))

    def delete(self):
        print(f"Deleting index {self.index}...")
        resp = self.es.indices.delete(index=self.index, ignore=[400, 404])

    def upload_bulk(self, json_object):
        try:
            bulk_data = []

            for doc in json_object:
                json_str = json.dumps(doc, indent=2, default=ParserHelper.Utils.serialize_sets)
                bulk_data.append({
                    "index": {
                        "_index": self.index,
                    }
                })
                bulk_data.append(doc)

            resp = self.es.bulk(index="my_index", operations=bulk_data, refresh=True)
            print(resp)
        except BadRequestError as e:
            print(f"Failed to upload. {e.body}")
