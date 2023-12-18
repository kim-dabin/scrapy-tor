from pathlib import Path
import datetime
import hashlib
from urllib.parse import urlparse
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy_tor.items import ScrapyTorItem, MetaItem
import scrapy 
import asyncio
from twisted.internet import asyncioreactor
scrapy.utils.reactor.install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
is_asyncio_reactor_installed = scrapy.utils.reactor.is_asyncio_reactor_installed()
print(f"Is asyncio reactor installed: {is_asyncio_reactor_installed}")
from twisted.internet import reactor
        
class RansomwareSpider(scrapy.Spider):
    name = 'ransomware'

    def start_requests(self):
        # reactor.callLater(15, self.start_requests)
        for domain in self.settings['DOMAIN']['ransomware']:
            yield scrapy.Request(url=domain['url'],
                                 callback=self.parse, 
                                 meta={'sitename': domain['sitename'],'page': 1})

    def parse(self, response):    
        sitename = response.meta['sitename']
        page = response.meta['page']
        
        if sitename == 'AKIRA':
            for next_url in ['l', 'n']:
                yield response.follow(next_url, 
                                      callback=self.parse_item,
                                      meta={'sitename': sitename, 'page': page})
        
        if sitename == 'Cuba':
            for page in range(1, 16):
                yield response.follow(f'ajax/page_free/{page}', 
                                        callback=self.parse_page_cuba, 
                                        meta={'sitename': sitename, 'page': page})
        if sitename == 'PLAY':
            last_page = response.css(".Page::text").getall()[-1]
            last_page_num = int(last_page) + 1
            for page in range(1, last_page_num):
                yield response.follow(f'index.php?page={page}', 
                                        callback=self.parse_item, 
                                        meta={'sitename': sitename, 'page': page})               

    def parse_page_cuba(self, response):
        meta = response.meta
        if response.body.decode('utf-8') in 'nomore':                              
            return
        yield from response.follow_all(css=".col-xs-12 a", 
                                       callback=self.parse_item,
                                       meta={'sitename': meta['sitename'], 'page': meta['page']})

    def parse_item(self, response):
        meta = MetaItem()
        item = ScrapyTorItem()

        meta['response'] = self.reconstruct_response(response)
        meta['request'] = self.reconstruct_request(response.request)
        now = datetime.datetime.now()
        meta['timestamp'] = now.isoformat()
        # item['timestamp_store'] # item piplines에서 저장
        meta['tag'] = {'web_type': self.name}
        file_name = now.strftime('%Y-%m-%d %H:%M:%S') + response.url
        meta['sha256'] = hashlib.sha256(file_name.encode('utf-8')).hexdigest()
        
        item['meta'] = meta
        item['sitename'] = response.meta['sitename']
        item['body'] = response.body
        item['date'] = now.strftime("%Y%m%d")   # e.g) 20231207
        item['domain'] = urlparse(response.url).netloc
        item['web_type'] = self.name
        item['filename'] = meta['sha256']
        return item

    def reconstruct_response(self, response):
        response_info = {}
        response_info['status_code'] = response.status
        response_info['url'] = response.url
        response_info['header'] = header2dict(response.headers)
        return response_info    

    def reconstruct_request(self, request):
        request_info = {}
        request_info['method'] = request.method
        request_info['url'] = request.url
        request_info['header'] = header2dict(request.headers)
        return request_info

def header2dict(headers: dict):
    header = {}
    for k, v in headers.items():
        k = str(k, 'utf-8')
        if type(v) is list:
            header[k] = str(v[0], 'utf-8')
        elif type(v) is str:
            header[k] = str(v, 'utf-8')
    return header