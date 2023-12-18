
BOT_NAME = "scrapy_tor"
SPIDER_MODULES = ["scrapy_tor.spiders"]
NEWSPIDER_MODULE = "scrapy_tor.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# mongodb 정보
MONGO_URI = "mongodb://mongodb:27017"
MONGO_DATABASE = "web"

ITEM_PIPELINES = {
   "scrapy_tor.pipelines.ScrapyTorPipeline": 1,
   "scrapy_tor.pipelines.MongoPipeline": 300,

}

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
LOG_FILE = "scrapy.log"
LOG_LEVEL = "INFO"
REACTOR_THREADPOOL_MAXSIZE = 20
COOKIES_ENABLED = False
RETRY_ENABLED = True
DOWNLOAD_TIMEOUT = 40
AJAXCRAWL_ENABLED = True
ASYNCIO_EVENT_LOOP = None