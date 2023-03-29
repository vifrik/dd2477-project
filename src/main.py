import argparse
from elasticsearch import Elasticsearch
import json

from scraper import Scraper
from credentials import token


def scrape():
    crawler = Scraper(token)
    crawler.run()


def parse():
    pass


def upload():
    pass


def parse_args():
    Parser = argparse.ArgumentParser()
    mode_group = Parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("-s", "--scrape", help="should scraper", action="store_true")
    mode_group.add_argument("-p", "--parse", help="should parse", action="store_true")
    return Parser.parse_args()


def main():
    args = parse_args()

    if args.scrape:
        scrape()
        exit(0)


if __name__ == '__main__':
    main()
