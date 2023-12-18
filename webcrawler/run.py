import os
import argparse
import yaml

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.reactor import install_reactor
from scrapy_tor.spiders.ransomware_spider import RansomwareSpider
from apscheduler.schedulers.twisted import TwistedScheduler

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

def main():
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
    scheduler = TwistedScheduler()
    try:
        # 60초마다 실행
        scheduler.add_job(process.crawl, 'interval', args=[RansomwareSpider], seconds=60)
        scheduler.start()
        process.start(stop_after_crawl=False)
    except Exception as e:
        process.stop()


if __name__ == '__main__':
    main()
