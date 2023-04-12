import argparse
import os.path
import os
from dotenv import load_dotenv

from scraper import Scraper
from parserhelper import ParserHelper
from elastic import Elastic

load_dotenv()


def scrape(args):
    crawler = Scraper(gh_token=os.getenv("TOKEN"))
    crawler.run()


def parse(args):
    parser_path = "../parser/bin/parser.jar"
    path = "data/java"
    metadata_path = os.path.join(path, "metadata.json")
    parser = ParserHelper(parser_path, path, metadata_path)
    json_array = parser.parse_folder()
    if args.upload:
        upload(args, json_array)
    else:
        print(json_array)


def scrapeparse(args):
    scraper = Scraper(batch_size=5)
    for count in scraper.run():
        parse(args)


def upload(args, json_object):
    elastic = Elastic(args.upload)

    #if args.delete:
    #    args.delete = False
    #    elastic.delete()

    elastic.upload_bulk(json_object)


def parse_args():
    parser = argparse.ArgumentParser()
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("-S", "--scrape", help="should scraper", action="store_true")
    mode_group.add_argument("-P", "--parse", help="should parse", action="store_true")
    mode_group.add_argument("-SP", "--scrapeparse", help="should scrape and parse", action="store_true")
    parser.add_argument("-u", "--upload", metavar="index", help="should upload")
    #parser.add_argument("--delete", help="(WARNING, deletes entire index) should delete", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.scrape:
        scrape(args)
    elif args.parse:
        parse(args)
    elif args.scrapeparse:
        scrapeparse(args)


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as e:
        print("Make sure that Java exists, run java --version to check")
        print("https://www.oracle.com/java/technologies/downloads/#jdk20-windows")
