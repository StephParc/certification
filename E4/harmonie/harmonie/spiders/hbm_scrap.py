import scrapy
from harmonie.items import HarmonieItem

class HbmScrapSpider(scrapy.Spider):
    name = "hbm_scrap"
    allowed_domains = ["musicshopeurope.fr"]
    start_urls = ["https://musicshopeurope.fr/partitions/band/orchestre-d-harmonie/"]
    # nombre_pages = start_urls.xpath("//ul[@class='pager-list reset']/li//a/text()").getall()[-1]
    # print(nombre_pages)

    def parse(self, response):
        partitions = response.xpath("//a[@class='product-title']")
        for partition in partitions:
            if partition.xpath("./following-sibling::div[@class='product-attributes']/span[contains(text(), 'Set')]"):
                partition_url = partition.xpath("./@href").get()
                yield response.follow(partition, callback=self.parse_partition)
            

    def parse_partition(self, response):
        item = HarmonieItem()
        item["titre"]           = response.xpath("//h1/text()").get()
        item["sous_titre"]      = response.xpath("//h2/text()").get()
        item["compositeur"]     = response.xpath("//td[contains(text(), 'Compositeur')]/following-sibling::td/text()").getall()
        item["arrangeur"]       = response.xpath("//td[contains(text(), 'Arrangeur')]/following-sibling::td/text()").getall()
        item["edition"]         = response.xpath("//td[contains(text(), 'Édition musicale')]/following-sibling::td/text()").get()
        item["instrumentation"] = response.xpath("//td[contains(text(), 'Instrumentation')]/following-sibling::td/text()").get()
        item["niveau"]          = response.xpath("//td[contains(text(), 'Moeilijkheidsgraad orkest')]/following-sibling::td/text()").get()
        item["annee_sortie"]    = response.xpath("//td[contains(text(), 'Année')]/following-sibling::td/text()").get()   
        item["partie_euro"]     = response.xpath("//td[contains(text(), 'Europese partijen inbegrepen')]/following-sibling::td/text()").get()     
        item["genre"]           = response.xpath("//td[contains(text(), 'Genre')]/following-sibling::td/text()").get()
        item["style"]           = response.xpath("//td[contains(text(), 'Style')]/following-sibling::td/text()").get()
        item["ISMN"]            = response.xpath("//td[contains(text(), 'ISMN')]/following-sibling::td/text()").get()
        item["collection"]      = response.xpath("//td[contains(text(), 'Collection')]/following-sibling::td/text()").get()
        item["ref_editeur"]     = response.xpath("//td[contains(text(), 'No.')]/following-sibling::td/text()").get()
        item["duree"]           = response.xpath("//td[contains(text(), 'Tiijdsduur')]/following-sibling::td/text()").get()
        item["description"]     = response.xpath("//div[@itemprop='description']/text()").get()
        item["url"]             = response.url

        yield item
