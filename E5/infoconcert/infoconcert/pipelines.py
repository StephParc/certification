# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re

class InfoconcertPipeline:
    def process_item(self, item, spider):
        item = self.clean_departement(item)
        item = self.clean_tarif(item)
        item = self.clean_jour(item)
        return item

    def clean_departement(self, item):
        adapter = ItemAdapter(item)
        departement = adapter.get("departement")
        if departement:
            if departement != []:
                for element in departement:
                    match = re.search(r'\((\d{2})\)', element)
                    if match:
                        adapter["departement"] = match.group(1)
                        break
        return item
    
    def clean_tarif(self, item):
        adapter = ItemAdapter(item)
        tarif = adapter.get("tarif_min")
        if tarif:
            match =  re.findall(r'(\d+(?:\.\d+)?)', tarif)
            if match:
                adapter["tarif_min"] = match[0]
                adapter["tarif_max"] = match[-1]
            else:
                adapter["tarif_min"] = None
                adapter["tarif_max"] = None
        return item
    
    def clean_jour(self, item):
        adapter = ItemAdapter(item)
        jour = adapter.get("jour_semaine")
        if jour:
            adapter["jour_semaine"] = jour.strip()
        return item



