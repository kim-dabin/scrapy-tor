# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class MetaItem(Item):
    # 웹 수집기에서 저장한 파일에 대한 메타 데이터 필드
    request = Field()           # HTTP request 정보 (중요)
    response = Field()          # HTTP response 정보 (중요)
    sha256 = Field()            # 해당 파일에 대한 sha256 값
    timestamp = Field()         # 사이트 방문 시간
    timestamp_store = Field()   # 파일 저장 시간
    tag = Field()               # 그 외 필요한 기타 정보

class ScrapyTorItem(Item):
    meta = Field()
    # 웹 수집기에서 축출한 데이터에 대한 필드
    body = Field()
    filename = Field()
    date = Field()
    domain = Field()
    sitename = Field()          
    web_type = Field()          # ransomware, forum_user, forum_post



