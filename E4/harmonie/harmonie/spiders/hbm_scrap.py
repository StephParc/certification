import sys
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from playwright.sync_api import sync_playwright
from scrapy.http import HtmlResponse


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from harmonie.items import HarmonieItem

class HbmScrapSpider(scrapy.Spider):
    name = "hbm_scrap"
    allowed_domains = ["musicshopeurope.fr"]
    start_urls = ["https://musicshopeurope.fr/partitions/band/orchestre-d-harmonie/"] 

    def __init__(self, *args, **kwargs):
        super(HbmScrapSpider, self).__init__(*args, **kwargs)
        self.playwright = sync_playwright().start()
        # self.browser = self.playwright.chromium.launch(headless=False)
        self.browser = self.playwright.firefox.launch(headless=True)

    def parse(self, response):
        print("coucou parse")
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
        print("coucou parse_partition")
        # Utiliser Playwright pour interagir avec les éléments dynamiques
        onglet = self.browser.new_page()
        onglet.goto(response.url)

        # Exemple : Cliquer sur un bouton pour charger du contenu dynamique
        # onglet.click('text=description')
        # onglet.wait_for_selector('css=#ui-id-3')
        onglet.wait_for_selector('a.ui-tabs-anchor[href="#description"]')
        onglet.click('a.ui-tabs-anchor[href="#description"]')
        print("onglet",onglet)
        # Extraire le contenu dynamique
        content = onglet.text_content('css=#ui-id-3')
        self.log(f'Dynamic Content: {content}')
        print("content", content)
        # Obtenir le contenu HTML rendu
        body = onglet.content()
        response_html = HtmlResponse(url=response.url, body=body, encoding='utf-8')

        item = HarmonieItem()
        item["titre"]           = response_html.xpath("//h1/text()").get()
        # item["sous_titre"]      = response_html.xpath("//td[contains(text(), 'Subtitle')]/following-sibling::td/text()").get()
        # item["compositeur"]     = response.xpath("//td[contains(text(), 'Compositeur')]/following-sibling::td/text()").getall()
        # item["arrangeur"]       = response.xpath("//td[contains(text(), 'Arrangeur')]/following-sibling::td/text()").getall()
        # item["artiste"]         = response.xpath("//td[contains(text(), 'Artiste')]/following-sibling::td/text()").getall()
        # item["edition"]         = response.xpath("//td[contains(text(), 'Édition musicale')]/following-sibling::td/text()").get()
        # item["instrumentation"] = response.xpath("//td[contains(text(), 'Instrumentation')]/following-sibling::td/text()").get()
        # item["niveau"]          = response.xpath("//td[contains(text(), 'Grade')]/following-sibling::td/text()").get()
        # item["annee_sortie"]    = response.xpath("//td[contains(text(), 'Année')]/following-sibling::td/text()").get()   
        # item["partie_euro"]     = response.xpath("//td[contains(text(), 'European')]/following-sibling::td/text()").get()     
        # item["genre"]           = response.xpath("//td[contains(text(), 'Genre')]/following-sibling::td/text()").get()
        # item["style"]           = response.xpath("//td[contains(text(), 'Style')]/following-sibling::td/text()").get()
        # item["ISMN"]            = response.xpath("//td[contains(text(), 'ISMN')]/following-sibling::td/text()").get()
        # item["collection"]      = response.xpath("//td[contains(text(), 'Collection')]/following-sibling::td/text()").get()
        # item["ref_editeur"]     = response.xpath("//td[contains(text(), 'No.')]/following-sibling::td/text()").get()
        # item["duree"]           = response.xpath("//td[contains(text(), 'Duration')]/following-sibling::td/text()").get()
        item["description"]     = response_html.xpath("//div[@class='description fr-view']/text()").get()
        # item["url"]             = response.url

        yield item

        # Fermer la page
        onglet.close()

    def closed(self, reason):
        self.browser.close()
        self.playwright.stop()

# Exécuter le spider
if __name__ == "__main__":
    process = CrawlerProcess(settings={
        'LOG_LEVEL': 'INFO',
        'FEEDS': {
            '../essai4.csv': {
                'format': 'csv',
                'overwrite': True,
            },
        },
    })
    process.crawl(HbmScrapSpider)
    process.start()