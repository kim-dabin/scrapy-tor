from pathlib import Path

import scrapy

class OnionCrawler(scrapy.Spider):

    name = 'OnionCrawler'

    def start_requests(self):
        urls = [ 'http://'+domain['domain'] for domain in self.settings['DOMAIN']['ransomware']]
        for url in urls:
            yield scrapy.Request(url=url, 
                                 callback=self.parse, 
                                 errback=self.errback)


    def parse(self, response):
        # page = response.
        # filename = f"quotes-{page}.html"
        # Path(filename).write_bytes()
        # self.log(response.body)
        self.logger.info(f'successful response from {response.url}')

    
    def errback(self, failure):
        # log all failures
        self.logger.error(repr(failure))