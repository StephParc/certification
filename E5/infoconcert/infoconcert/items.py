# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InfoconcertItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    artiste         = scrapy.Field()
    style           = scrapy.Field()
    date_concert    = scrapy.Field()
    jour_semaine    = scrapy.Field()
    salle           = scrapy.Field()
    adresse         = scrapy.Field()
    ville           = scrapy.Field()
    departement     = scrapy.Field()
    tarif_min       = scrapy.Field()
    tarif_max       = scrapy.Field()

