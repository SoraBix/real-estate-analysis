# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class CraigslistItem(scrapy.Item):
	url = scrapy.Field()
	price = scrapy.Field()
	area = scrapy.Field()
	title = scrapy.Field()
	sub_title = scrapy.Field()
	map_address = scrapy.Field()
	latitude = scrapy.Field()
	longitude = scrapy.Field()
	detail = scrapy.Field()

class RealtorItem(scrapy.Item):
	url = scrapy.Field()
	street = scrapy.Field()
	locality = scrapy.Field()
	region = scrapy.Field()
	postal = scrapy.Field()
	latitude = scrapy.Field()
	longitude = scrapy.Field()
	price = scrapy.Field()
	detail = scrapy.Field()
