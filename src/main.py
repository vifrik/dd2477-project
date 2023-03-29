import argparse
from elasticsearch import Elasticsearch
import json

from scraper import Scraper
from parser import Parser
from elastic import Elastic
from credentials import token


def scrape(args):
    crawler = Scraper(token)
    crawler.run()


def parse(args):
    parser = Parser("data/java", "metadata.json")
    for json_object in parser.parse_folder():
        if args.upload:
            upload(args, json_object)
        else:
            print(json_object)


def upload(args, json_object):
    elastic = Elastic(args.upload)

    if args.delete:
        args.delete = False
        elastic.delete()

    elastic.upload(json_object)


def parse_args():
    Parser = argparse.ArgumentParser()
    mode_group = Parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("-S", "--scrape", help="should scraper", action="store_true")
    mode_group.add_argument("-P", "--parse", help="should parse", action="store_true")
    Parser.add_argument("-u", "--upload", metavar="index", help="should upload")
    Parser.add_argument("--delete", help="(WARNING, deletes entire index) should delete", action="store_true")
    return Parser.parse_args()


def main():
    args = parse_args()

    if args.scrape:
        scrape(args)
    elif args.parse:
        parse(args)


if __name__ == '__main__':
    main()
