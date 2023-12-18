# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import datetime
from pathlib import Path
from itemadapter import ItemAdapter
import pymongo

class ScrapyTorPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item).asdict()
        dirname = os.path.join("data/raw", 
                                adapter["date"], 
                                adapter["web_type"], 
                                adapter["sitename"],
                                adapter['filename'][:2])
        os.makedirs(dirname, mode=0o777, exist_ok=True)
        filename = os.path.join(dirname, adapter['filename'])
        Path(filename).write_bytes(adapter['body'])
        return item


class MongoPipeline:
    collection_name = "meta"

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE"),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        meta = ItemAdapter(item['meta']).asdict()
        meta['timestamp_store'] = datetime.datetime.now().isoformat()
        self.db[self.collection_name].insert_one(meta)
        return item