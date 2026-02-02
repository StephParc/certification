import re
import scrapy
from harmonie.items import HarmonieItem

class HbmScrapSpider(scrapy.Spider):
    """
    A Scrapy spider for scraping music sheet data from a specific website.

    Attributes:
        name (str): The name of the spider.
        allowed_domains (list): The list of domains allowed for scraping.
        start_urls (list): The list of URLs from which the spider starts scraping.
    """
    name = "hbm_scrap"
    allowed_domains = ["musicshopeurope.fr"]
    
    start_urls = ["https://www.musicshopeurope.fr/partitions/band/orchestre-d-harmonie/type%20de%20produit=conducteur%20-15=%20parties/?sort=Marketable+from_desc&page=1"] 

    def parse(self, response):
        """
        Parse the initial URLs and navigate through the pages.

        This method is responsible for iterating over the list of music sheets found on each page
        and following the links to scrape detailed information. It also handles pagination to navigate
        through multiple pages of results.

        Args:
            response: The response object from Scrapy containing the page content.

        Yields:
            Request: A request to follow the link to the music sheet page for detailed scraping.
        """
        partitions = response.xpath("//a[@class='product-title']")
        # for partition in partitions:
        #     if partition.xpath("./following-sibling::div[@class='product-attributes']/span[contains(text(), 'Set')]"):
        #         partition_url = partition.xpath("./@href").get()
        #         yield response.follow(partition, callback=self.parse_partition)

        for partition in partitions:
            yield response.follow(partition, callback=self.parse_partition)

        # Nombres de pages à scraper (commenter la ligne non retenue)
        #       ligne 45 pour le nombre de pages du site
        #       ligne 46 pour un nombre choisi
        # nombre_pages = int(response.xpath("//ul[@class='pager-list reset']/li//a/text()").getall()[-1])
        nombre_pages = 10

        # Page de démarrage du scraping
        numero_page_actuelle = 1
        if re.findall(r'page=(\d+)', response.url)[0] and int(re.findall(r'page=(\d+)', response.url)[0]) < nombre_pages:
            numero_page_actuelle = int(re.findall(r'page=(\d+)', response.url)[0])
            numero_page_suivante = numero_page_actuelle + 1
        
        next_page = f'https://www.musicshopeurope.fr/partitions/band/orchestre-d-harmonie/type%20de%20produit=conducteur%20-15=%20parties/?sort=Marketable+from_desc&page={numero_page_suivante}'

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


    def parse_partition(self, response):
        """
        Extract detailed information from a music sheet page.

        This method targets specific HTML elements on the music sheet pages to extract desired fields
        such as title, subtitle, composer, arranger, and other relevant details.

        Args:
            response: The response object from Scrapy containing the music sheet page content.

        Yields:
            HarmonieItem: An item containing the extracted data fields from the music sheet page.
        """
        item = HarmonieItem()
        item["titre"]           = response.xpath("//h1/text()").get()
        item["sous_titre"]      = response.xpath("//td[contains(text(), 'Subtitle')]/following-sibling::td/text()").get()
        item["compositeur"]     = response.xpath("//td[contains(text(), 'Compositeur')]/following-sibling::td/text()").getall()
        item["arrangeur"]       = response.xpath("//td[contains(text(), 'Arrangeur')]/following-sibling::td/text()").getall()
        item["artiste"]         = response.xpath("//td[contains(text(), 'Artiste')]/following-sibling::td/text()").getall()
        item["edition"]         = response.xpath("//td[contains(text(), 'Édition musicale')]/following-sibling::td/text()").get()
        item["instrumentation"] = response.xpath("//td[contains(text(), 'Instrumentation')]/following-sibling::td/text()").get()
        item["niveau"]          = response.xpath("//td[contains(text(), 'Grade')]/following-sibling::td/text()|//td[contains(text(),'Moeilijkheidsgraad orkest')]/following-sibling::td/text()").get()
        item["annee_sortie"]    = response.xpath("//td[contains(text(), 'Année')]/following-sibling::td/text()").get()   
        item["partie_euro"]     = response.xpath("//td[contains(text(), 'Europe')]/following-sibling::td/text()").get()     
        item["genre"]           = response.xpath("//td[contains(text(), 'Genre')]/following-sibling::td/text()").get()
        item["style"]           = response.xpath("//td[contains(text(), 'Style')]/following-sibling::td/text()").get()
        item["ISMN"]            = response.xpath("//td[contains(text(), 'ISMN')]/following-sibling::td/text()").get()
        item["collection"]      = response.xpath("//td[contains(text(), 'Collection')]/following-sibling::td/text()").get()
        item["ref_editeur"]     = response.xpath("//td[contains(text(), 'No.')]/following-sibling::td/text()").get()
        item["duree"]           = response.xpath("//td[contains(text(), 'Duration')]/following-sibling::td/text()|//td[contains(text(), 'Tiijdsduur')]/following-sibling::td/text()").get()
        item["description"]     = response.xpath("//meta[@name='description']/@content").get()
        item["url"]             = response.url

        yield item
