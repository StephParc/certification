import scrapy
from infoconcert.items import InfoconcertItem
from datetime import date, datetime

class InfoconcertScrapSpider(scrapy.Spider):
    name = "infoconcert_scrap_liste"
    allowed_domains = ["infoconcert.com"]
    start_urls = ["https://www.infoconcert.com/concerts/derniere-minute.html", "https://www.infoconcert.com/spectacles-musicaux/derniere-minute.html"]

    def parse(self, response):

        concerts = response.xpath("//div[@class='spectacle']/a")

        for i, concert in enumerate(concerts):
            item = InfoconcertItem()
            item["date_concert"]    = response.xpath("//time[@itemprop='startDate']/@datetime").getall()[i]
            item["jour_semaine"]    = response.xpath("//time[@itemprop='startDate']/span[@class='day-title']/text()").getall()[i]
            yield response.follow(concert, meta={"item":item}, callback=self.parse_concert)

    def parse_concert(self, response):
        item= response.meta["item"]
        item["artiste"]         = response.xpath("//h1/text()").get()
        item["style"]           = response.xpath("//h1/following-sibling::a/text()").get()
        # item["date_concert"]    = response.xpath(f"//time[@itemprop='startDate'][contains(@datetime, '{now}')]/@datetime").get()
        # item["jour_semaine"]    = response.xpath("//time[@itemprop='startDate']/span[@class='day-title']/text()").get()
        # item["salle"]           = response.xpath("").get()
        # item["adresse"]         = response.xpath("").get()
        # item["ville"]           = response.xpath("").get()
        # item["departement"]     = response.xpath("").get()
        # item["tarif"]           = response.xpath("").get()

        yield item
