import re
import scrapy
from harmonie.items import HarmonieItem
from scrapy_playwright.page import PageMethod

class HbmScrapSpider(scrapy.Spider):
    """
    A Scrapy spider for scraping music sheet data from a specific website.

    Attributes:
        name (str): The name of the spider.
        allowed_domains (list): The list of domains allowed for scraping.
        start_urls (list): The list of URLs from which the spider starts scraping.
    """
    name = "hbm_scrap"
    allowed_domains = ["musicshopeurope.com"]

    handle_httpstatus_list = [403]
   
    # start_urls = ["https://www.musicshopeurope.com/partitions/band/orchestre-d-harmonie/type%20de%20produit=conducteur%20-15=%20parties/?sort=Marketable+from_desc&page=1"] 
    # start_urls = ["https://www.musicshopeurope.fr/partitions/band/orchestre-d-harmonie/type de produit=conducteur -15= parties/?sort=Marketable+from_desc&page=1"]

    def start_requests(self):
        # ÉTAPE 1 : On va d'abord sur l'accueil pour initialiser la session Azure/Cookies
        yield scrapy.Request(
            "https://www.musicshopeurope.com/",
            callback=self.parse_home,
            meta={
                "playwright": True,
                "playwright_include_page": True, # On demande à garder la page ouverte
                "playwright_page_methods": [
                    # Utilisation obligatoire des objets PageMethod
                    PageMethod("wait_for_timeout", 5000), 
                    PageMethod("evaluate", '() => { const btn = document.querySelector("button"); if(btn && btn.innerText.includes("Accept")) btn.click(); }'),
                ],
            }
        )

    async def parse_home(self, response):
        page = response.meta["playwright_page"]
        if response.status == 403:
            self.logger.warning("Barrage Azure détecté, attente de 5s...")
            await page.wait_for_timeout(5000)
        # ÉTAPE 2 : Une fois la session "chaude", on va vers les partitions
        target_url = "https://www.musicshopeurope.com/partitions/band/orchestre-d-harmonie/type%20de%20produit=conducteur%20-15=%20parties/?sort=Marketable+from_desc"
        yield scrapy.Request(
            target_url,
            callback=self.parse,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_goto_params": {"wait_until": "networkidle"},
            }
        )

    async def parse(self, response):
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
        page = response.meta.get("playwright_page")

        if not page:
            self.logger.error(f"Objet Playwright absent pour l'URL : {response.url}")
            return

        partitions = response.xpath("//a[@class='product-title']")
        # for partition in partitions:
        #     if partition.xpath("./following-sibling::div[@class='product-attributes']/span[contains(text(), 'Set')]"):
        #         partition_url = partition.xpath("./@href").get()
        #         yield response.follow(partition, callback=self.parse_partition)

        for partition in partitions:
            yield response.follow(partition, callback=self.parse_partition, meta={"playwright": True})

        # Nombres de pages à scraper (commenter la ligne non retenue)
        #       ligne 88 pour le nombre de pages du site
        #       ligne 89 pour un nombre choisi
        # nombre_pages = int(response.xpath("//ul[@class='pager-list reset']/li//a/text()").getall()[-1])
        nombre_pages = 2

        page_matches = re.findall(r'page=(\d+)', response.url)
        if page_matches:
            numero_page_actuelle = int(page_matches[0])
        else:
            numero_page_actuelle = 1

        # Page de démarrage du scraping
        if numero_page_actuelle < nombre_pages:
            numero_page_suivante = numero_page_actuelle + 1
            # next_page = f"https://www.musicshopeurope.com/sheet-music-and-books/band/concert-band/product%20type=Set/?sort=Marketable+from_desc&page={numero_page_suivante}"
            next_page = f"https://www.musicshopeurope.com/partitions/band/orchestre-d-harmonie/type%20de%20produit=conducteur%20-15=%20parties/?sort=Marketable+from_desc&page={numero_page_suivante}"
            self.logger.info(f"Passage à la page suivante : {numero_page_suivante}")
            yield response.follow(next_page, callback=self.parse, meta={"playwright": True, "playwright_include_page": True})
        
        self.logger.info(f"Statut final de cette page : {response.status}")
        
        await page.close()

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
