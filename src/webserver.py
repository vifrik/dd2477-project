from flask import Flask, request
from elasticsearch import Elasticsearch
import json
import os
from dotenv import load_dotenv

import query_dsl

load_dotenv()

if os.getenv("MODE") == "prod":
    es = Elasticsearch(os.getenv("ELASTIC_ENDPOINT"))
else:
    es = Elasticsearch("https://elastic.åt.se:443", basic_auth=(os.getenv("AUTH_USER"), os.getenv("AUTH_PASSWORD")))

app = Flask(__name__)


def get_elastic_query(query):
    lexer = query_dsl.lexer.Lexer(query)
    tokens = list(lexer.tokenize())

    parser = query_dsl.parser.Parser(tokens)
    output_queue = parser.parse()

    return parser.get_elasticsearch_query(output_queue)


@app.route("/query")
def query():
    try:
        query = request.args.get("q")
        return json.dumps(get_elastic_query(query))
    except query_dsl.error.DslSyntaxError as e:
        return {
            "error": str(e)
        }


@app.route("/search")
def search():
    try:
        query = request.args.get("q")
        index = request.args.get("index", default="main-index")
        from_index = request.args.get("from", default="0")
        size = request.args.get("size", default="10")

        body = get_elastic_query(query)
        
        response = es.search(index=index, query=body, size=size, from_=from_index)

        res = []
        for hit in response["hits"]["hits"]:
            new = {}
            new["id"] = hit["_id"]
            new["score"] = hit["_score"]
            new["url"] = hit["_source"]["metadata"]["download_url"]
            new["path"] = hit["_source"]["metadata"]["path"]
            new["repo"] = hit["_source"]["metadata"]["repo"]

            highlights = []
            for key in hit["inner_hits"].keys():
                type = key.split("=")[0].split(".")[1]
                for inner_hit in hit["inner_hits"][key]["hits"]["hits"]:
                    highlights.append({
                        "result": inner_hit["_source"][type + "_position"]
                    })

            new["highlights"] = highlights

            res.append(new)



        return json.dumps(res)
    except query_dsl.error.DslSyntaxError as e:
        return {
            "error": str(e)
        }


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
