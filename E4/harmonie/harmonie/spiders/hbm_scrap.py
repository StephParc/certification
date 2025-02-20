import scrapy
from harmonie.items import HarmonieItem

class HbmScrapSpider(scrapy.Spider):
    name = "hbm_scrap"
    allowed_domains = ["musicshopeurope.fr"]
    start_urls = ["https://musicshopeurope.fr/partitions/band/orchestre-d-harmonie/"]
    # nombre_pages = response.xpath("//ul[@class='pager-list reset']/li//a/text()").getall()[-1]

    def parse(self, response):
        partitions = response.xpath("//a[@class='product-title']")
        for partition in partitions:
            partition_url = partition.xpath("./@href").get()
            yield response.follow(partition, callback=self.parse_partition)

    def parse_partition(self, response):
        item = HarmonieItem()
        item["titre"] = response.xpath("//h1/text()").get()
        item["sous_titre"] = response.xpath("//h2/text()").get()

        yield item
