import argparse
from elasticsearch import Elasticsearch
import json

from scraper import Scraper
from parser import Parser
from credentials import token


def scrape():
    crawler = Scraper(token)
    crawler.run()


def parse():
    parser = Parser("data/java", "metadata.json")
    for json_object in parser.parse_folder():
        upload(json_object)


def upload(json_object):
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

    if args.parse:
        parse()
        exit(0)


if __name__ == '__main__':
    main()
