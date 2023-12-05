import os
from typing import List
from ast import literal_eval
import argparse
import yaml

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings, get_config
from scrapy_tor.spiders.OnionCrawler import OnionCrawler

# 아규먼트 파싱 메소드 
def parsing_argument() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
      description="SEED URL Arguments Parsing", 
      formatter_class=argparse.ArgumentDefaultsHelpFormatter
      )
  parser.add_argument(
    '-f',
    '--file',
    metavar='FILE',
    type=argparse.FileType('rt'),
    help='Option File Arguments',
    default=None
  )
  return parser.parse_args()


def main() -> None:
    args = parsing_argument().file
    settings = get_project_settings()
    filename, file_extension = os.path.splitext(args.name)
    domain_list = {}

    if args == None:
        return
    
    if file_extension == '.yaml' or file_extension == '.yml':
        domain_list = yaml.load(args.read(), Loader=yaml.FullLoader)

    if len(domain_list) < 1:
        return
    
    settings.set('DOMAIN', domain_list)
    process = CrawlerProcess(settings=settings)
    try:
        process.crawl(OnionCrawler)
        process.start()
    except Exception as e:
        process.stop()


if __name__ == '__main__':
    main()
    