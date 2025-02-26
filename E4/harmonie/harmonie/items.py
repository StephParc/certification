# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HarmonieItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    titre           = scrapy.Field()
    sous_titre      = scrapy.Field()
    compositeur     = scrapy.Field()
    arrangeur       = scrapy.Field()
    artiste         = scrapy.Field()
    edition         = scrapy.Field()
    instrumentation = scrapy.Field()
    niveau          = scrapy.Field()
    annee_sortie    = scrapy.Field()
    partie_euro     = scrapy.Field()
    genre           = scrapy.Field()
    style           = scrapy.Field()
    ISMN            = scrapy.Field()
    collection      = scrapy.Field()
    ref_editeur     = scrapy.Field()
    duree           = scrapy.Field()
    description     = scrapy.Field()
    url             = scrapy.Field()
