from elasticsearch import Elasticsearch
import json

from parser import Parser

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

    def upload(self, json_object):
        print(f"Uploading {json_object['metadata']['given_name']}...", end="")
        json_str = json.dumps(json_object, indent=2, default=Parser.Utils.serialize_sets)
        resp = self.es.index(index=self.index, document=json_str)
        print(resp["result"])
        self.es.indices.refresh(index=self.index)
