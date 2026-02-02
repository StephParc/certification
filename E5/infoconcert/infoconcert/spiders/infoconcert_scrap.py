import scrapy
from infoconcert.items import InfoconcertItem
from datetime import date, datetime
import re

class InfoconcertScrapSpider(scrapy.Spider):
    name = "infoconcert_scrap"
    allowed_domains = ["infoconcert.com"]
    start_urls = ["https://www.infoconcert.com/concerts/derniere-minute.html", "https://www.infoconcert.com/spectacles-musicaux/derniere-minute.html"]

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'COOKIES_ENABLED': False
    }

    def parse(self, response):

        concerts = response.xpath("//div[@class='spectacle']/a")

        for concert in concerts:
            yield response.follow(concert, callback=self.parse_concert)
        
        page_actuelle = re.findall(r'derniere-minute-(\d+)', response.url)

        if page_actuelle == []:
            if "concerts" in response.url:
                event = "concerts"
            else :
                event = "spectacles-musicaux"
            page_suivante = 2
        else:
            if "concerts" in response.url:
                event = "concerts"
            else :
                event = "spectacles-musicaux"
            page_suivante = int(page_actuelle[0]) + 1

        url_page_suivante = f"https://www.infoconcert.com/{event}/derniere-minute-{page_suivante}.html"
        
        condition_page_utile = response.xpath("//div[@class='panel panel-default date-line date-line-concert']").get()
   
        # if page_actuelle == []:
        #     page_suivante = 2
        # else:
        #     page_suivante = int(page_actuelle[0]) + 1
        # url_page_suivante = response.xpath(f"//a[@class='page'][contains(text(),'{str(page_suivante)}')]/@href").get()
        if url_page_suivante and condition_page_utile:
            yield response.follow(url_page_suivante, callback=self.parse)
        

    def parse_concert(self, response):
        now = date.today().strftime("%Y-%m-%d")

        item= InfoconcertItem()
        item["artiste"]         = response.xpath("//h1/text()").get()
        item["style"]           = response.xpath("//h1/following-sibling::a/text()").getall()
        item["tarif_min"]       = response.xpath("//div[@class='col-xs-5 col-sm-12 price']/text()").get()
        item["salle"]           = response.xpath("//span[@itemprop='name']/text()").get()
        item["ville"]           = response.xpath("//span[@itemprop='locality']/text()").get()
        item["departement"]     = response.xpath("//div[@class='ville-dpt']/text()").getall()
        if response.xpath(f"//time[@itemprop='startDate'][contains(@datetime, '{now}')]/@datetime").get() != None:
            item["date_concert"]    = response.xpath(f"//time[@itemprop='startDate'][contains(@datetime, '{now}')]/@datetime").get()
            item["jour_semaine"]    = response.xpath("//time[@itemprop='startDate']/span[@class='day-title']/text()").get()
            
            url= response.xpath("//a[@itemprop='url']/@href").get()

            yield response.follow(url, meta={"item":item}, callback=self.parse_detail_unique)

        else:
            url= response.xpath("//a[@itemprop='url']/@href").get()

            yield response.follow(url, meta={"item":item}, callback=self.parse_detail_multiple)

    def parse_detail_unique(self, response):
        item = response.meta["item"]
        item["adresse"] = response.xpath("//h3[i[@class='fas fa-map-marker-alt fa-2x fa-fw']]/following-sibling::div/p[@class='m0']/span/text()").get()

        yield item

    def parse_detail_multiple(self, response):
        now = date.today()
        jour = now.day
        mois = now.month
        annee = now.year
        liste_mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        mois_long = liste_mois[mois-1]
        
        date_strong = f"{jour} {mois_long} {annee}"

        heure_texte = response.xpath(f"//li[@class='list-group-item']/strong[contains(text(), '{date_strong}')]/following-sibling::text()").get()
        if heure_texte:
            heure = re.findall(r'(\d+)', heure_texte)[0]
            minute = re.findall(r'(\d+)', heure_texte)[-1]
        else:
            heure = 00
            minute = 00

        date_concert = f"{annee}-{mois}-{jour}T{heure}:{minute}:00"

        item = response.meta["item"]
        item["date_concert"]    = datetime.strptime(date_concert, "%Y-%m-%dT%H:%M:%S")
        item["jour_semaine"]    = response.xpath(f"//li[@class='list-group-item'][contains(strong/text(), '{date_strong}')]/text()").get()
        item["adresse"]         = response.xpath("//h3[i[@class='fas fa-map-marker-alt fa-2x fa-fw']]/following-sibling::div/p[@class='m0']/span/text()").get()

        yield item