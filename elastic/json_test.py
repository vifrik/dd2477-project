#!/usr/bin/env python

from datetime import datetime
from elasticsearch import Elasticsearch
import json
import argparse


def main():
    Parser = argparse.ArgumentParser()
    Parser.add_argument("-u", "--upload", help="should upload", action="store_true")
    Parser.add_argument("-D", "--delete", help="should delete", action="store_true")
    args = Parser.parse_args()

    es = Elasticsearch('https://elastic.åt.se:443')
    index = "sample-index"

    with open("sample.json", "r") as f:
        doc = json.load(f)

    if args.delete:
        es.indices.delete(index=index, ignore=[400, 404])
        exit(0)

    if args.upload:
        resp = es.index(index=index, document=doc)
        print(resp['result'])

        # Get document
        resp = es.get(index=index, id=resp['_id'])
        print(resp['_source'])

        # Refresh index
        es.indices.refresh(index=index)

    # Search
    query = {
        "match": {
            "document.functions.name": "MyFunction"
        }
    }

    resp = es.search(index=index, query=query)
    print("Got %d Hits:" % resp['hits']['total']['value'])
    for hit in resp['hits']['hits']:
        print(hit['_source'])


if __name__ == '__main__':
    main()
