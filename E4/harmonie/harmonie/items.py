# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HarmonieItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    titre = scrapy.Field()
    sous_titre = scrapy.Field()
