from threading import Thread
from time import sleep
from flask import Flask, request
import pymongo
from github import Github
from github.GithubException import RateLimitExceededException
from time import sleep
import os
from datetime import datetime, timedelta
import json


import os
from dotenv import load_dotenv
load_dotenv()

db = pymongo.MongoClient(os.getenv("MONGO_ENDPOINT"))["scraper"]["docs"]
app = Flask(__name__)
g = Github(os.getenv("GH_TOKEN"))
dates = (datetime.now() - timedelta(days=7), datetime.now())

def get_repos():
    # One week at a time
    start, end = dates
    rate_limit = g.get_rate_limit()
    while rate_limit.search.remaining > 0:
        try:
            yield g.search_repositories(
                f"language:Java created:{start.isoformat()}..{end.isoformat()}",
                sort="stars",
            )
            start, end = start - timedelta(days=7), start
        except RateLimitExceededException:
            print("Rate limit exceeded, sleeping for one minute")
            sleep(60)
        finally:
            rate_limit = g.get_rate_limit()
            print(f"Rate limit remaining: {rate_limit.search.remaining}")

def save_repos():
    while True:
        print("getting new repos")
        for repos in get_repos():
            for repo in repos:
                #insert into db without duplicates
                if not db.find_one({"url": repo.html_url}):
                    db.insert_one({"url": repo.html_url, "completed": False})
                    print("inserting " + repo.html_url) 
        sleep(60)

def start_scrape_thread():
    print("Starting scraper thread")
    thread = Thread(target=save_repos)
    thread.start()

# get 5 documents, and set the "completed" field to true
@app.route("/fetch")
def fetch():
    docs = db.find({"completed": False}).limit(5)
    urls = []
    for doc in docs:
        urls.append(doc["url"])
        db.update_one({"_id": doc["_id"]}, {"$set": {"completed": True}})

    return urls

# peek how many docs are available
@app.route("/peek")
def peek():
    return str(len(list(db.find({"completed": False}))))

if __name__ == "__main__":
    start_scrape_thread()
    app.run(host='0.0.0.0', port=5001, debug=True)
