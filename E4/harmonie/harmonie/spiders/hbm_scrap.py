import scrapy
from harmonie.items import HarmonieItem

class HbmScrapSpider(scrapy.Spider):
    name = "hbm_scrap"
    allowed_domains = ["musicshopeurope.fr"]
    start_urls = ["https://musicshopeurope.fr/partitions/band/orchestre-d-harmonie/"] 

    def parse(self, response):
        partitions = response.xpath("//a[@class='product-title']")
        for partition in partitions:
            if partition.xpath("./following-sibling::div[@class='product-attributes']/span[contains(text(), 'Set')]"):
                partition_url = partition.xpath("./@href").get()
                yield response.follow(partition, callback=self.parse_partition)
            
        nombre_pages = response.xpath("//ul[@class='pager-list reset']/li//a/text()").getall()[-1]
        nombre_pages = '2'

        next_page = f'https://www.musicshopeurope.fr/partitions/band/orchestre-d-harmonie/?page={nombre_pages}'

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


    def parse_partition(self, response):
        item = HarmonieItem()
        item["titre"]           = response.xpath("//h1/text()").get()
        item["sous_titre"]      = response.xpath("//td[contains(text(), 'Subtitle')]/following-sibling::td/text()").get()
        item["compositeur"]     = response.xpath("//td[contains(text(), 'Compositeur')]/following-sibling::td/text()").getall()
        item["arrangeur"]       = response.xpath("//td[contains(text(), 'Arrangeur')]/following-sibling::td/text()").getall()
        item["artiste"]         = response.xpath("//td[contains(text(), 'Artiste')]/following-sibling::td/text()").getall()
        item["edition"]         = response.xpath("//td[contains(text(), 'Édition musicale')]/following-sibling::td/text()").get()
        item["instrumentation"] = response.xpath("//td[contains(text(), 'Instrumentation')]/following-sibling::td/text()").get()
        item["niveau"]          = response.xpath("//td[contains(text(), 'Grade')]/following-sibling::td/text()").get()
        item["annee_sortie"]    = response.xpath("//td[contains(text(), 'Année')]/following-sibling::td/text()").get()   
        item["partie_euro"]     = response.xpath("//td[contains(text(), 'European')]/following-sibling::td/text()").get()     
        item["genre"]           = response.xpath("//td[contains(text(), 'Genre')]/following-sibling::td/text()").get()
        item["style"]           = response.xpath("//td[contains(text(), 'Style')]/following-sibling::td/text()").get()
        item["ISMN"]            = response.xpath("//td[contains(text(), 'ISMN')]/following-sibling::td/text()").get()
        item["collection"]      = response.xpath("//td[contains(text(), 'Collection')]/following-sibling::td/text()").get()
        item["ref_editeur"]     = response.xpath("//td[contains(text(), 'No.')]/following-sibling::td/text()").get()
        item["duree"]           = response.xpath("//td[contains(text(), 'Duration')]/following-sibling::td/text()").get()
        item["description"]     = response.xpath("//div[@itemprop='description']/text()").get()
        item["url"]             = response.url

        # print("type titre           ",type(item["titre"]))
        # print("type sous_titre      ",type(item["sous_titre"]))
        # print("type compositeur     ",type(item["compositeur"]))
        # print("type arrangeur       ",type(item["arrangeur"]))
        # print("type artiste         ",type(item["artiste"]))
        # print("type edition         ",type(item["edition"]))
        # print("type instrumentation ",type(item["instrumentation"]))
        # print("type niveau          ",type(item["niveau"]))
        # print("type annee_sortie    ",type(item["annee_sortie"]))
        # print("type partie_euro     ",type(item["partie_euro"]))
        # print("type genre           ",type(item["genre"]))
        # print("type style           ",type(item["style"]))
        # print("type ISMN            ",type(item["ISMN"]))
        # print("type collection      ",type(item["collection"]))
        # print("type ref_editeur     ",type(item["ref_editeur"]))
        # print("type duree           ",type(item["duree"]))
        # print("type description     ",type(item["description"]))
        # print("type url             ",type(item["url"]))

        yield item
