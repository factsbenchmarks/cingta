# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import hashlib
class CingtaPipeline(object):
    def md5(self,x):
        m = hashlib.md5()
        m.update(x)
        return m.hexdigest()
    def process_item(self, item, spider):
        content = item.get('content')
        res = re.sub('<img.*?/>', '', content)
        res = re.sub('<p.*?>', '', res)
        res = re.sub('</p>', '', res)
        res = re.sub('<div.*?>', '', res)
        res = re.sub('</div>', '', res)
        res = re.sub('<strong>', '', res)
        res = re.sub('</strong>', '', res)
        res = re.sub('<blockquote>', '', res)
        res = re.sub('</blockquote>', '', res)
        res = re.sub('- .*? -', '', res)
        res = re.sub('\?', '', res)
        res = re.sub('&ldquo;', '"', res)
        res = re.sub('&rdquo;', '"', res)
        res = re.sub('&lsquo;', '’', res)
        res = re.sub('&rsquo;', '‚', res)
        res = re.sub('&nbsp;', '', res)
        res = re.sub('<span.*?>', '', res)
        res = re.sub('</span>', '', res)
        res = re.sub('&middot;', '·', res)
        res = re.sub('<ul>', '', res)
        res = re.sub('</ul>', '', res)
        res = re.sub('</ol>', '', res)
        res = re.sub('<ol>', '', res)
        res = re.sub('&rarr;', '→', res)
        res = re.sub('<li>', '', res)
        res = re.sub('</li>', '', res)
        res = re.sub('（来源.*?）', '', res)
        res = re.sub('(来源.*?)', '', res)
        res = re.sub('&hellip;', '...', res)
        item['content'] = res
        item['md5'] = self.md5(bytes(item['title'],encoding='utf-8'))
        return item



import pymongo

class MongoPipeline(object):

    collection_name = 'items'
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item


from scrapy.exceptions import DropItem

class CingtaDuplicatesPipeline(object):
    ids_seen = 'ids_seen'
    def __init__(self,mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )
    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
    def close_spider(self,spider):
        self.client.close()
    def process_item(self, item, spider):
        data = {
            item['md5']:1,
        }
        if self.db[self.ids_seen].find_one(data):
            raise DropItem("Duplicate item found: %s" %item['title'])
        else:
            self.db[self.ids_seen].insert_one(data)
            return item