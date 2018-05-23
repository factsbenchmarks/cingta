# -*- coding: utf-8 -*-
import scrapy
import json
import time
import random
from scrapy import FormRequest
from Scrapy.items import *
INDEX_URL = 'https://www.cingta.com/page_list/'
DETAIL_URL = 'https://www.cingta.com/page_detail/'
INDEX_DATA = {
    'pageSize':'12',
    'id':'',
    'keyword':'',
}
class CingtaSpider(scrapy.Spider):
    name = 'cingta'
    def start_requests(self):
        yield FormRequest(url=INDEX_URL,formdata=INDEX_DATA,callback=self.parse_index)
    def parse_index(self, response):
        res = json.loads(response.text)
        for item in res.get('data').get('list'):
            DETAIL_DATA = {
                'id':str(item.get('id')),
            }
            time.sleep(2)
            yield FormRequest(url=DETAIL_URL,formdata=DETAIL_DATA,callback=self.parse_detail,)
    def parse_detail(self,response):
        data = json.loads(response.text).get('data')
        item = CingtaItem()

        date = data.get('date')
        provenance = data.get('deliver')
        title = data.get('title')
        content = data.get('content')

        item['date'] = date
        item['title'] = title
        item['provenance'] = provenance
        item['source'] = provenance
        item['author'] = ''
        item['area'] = ''
        item['content'] = content
        yield item
