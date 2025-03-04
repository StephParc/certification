# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re
from datetime import datetime
# import dateparser

class HarmoniePipeline:
    def process_item(self, item, spider):
        # item = self.clean_titre(item)
        # item = self.clean_sous_titre(item)
        # item = self.clean_compositeur(item)
        # item = self.clean_arrangeur(item)
        # item = self.clean_artiste(item)
        # item = self.clean_edition(item)
        # item = self.clean_instrumentation(item)
        item = self.clean_niveau(item)
        item = self.clean_annee_sortie(item)
        item = self.clean_partie_euro(item)
        # item = self.clean_genre(item)
        # item = self.clean_style(item)
        # item = self.clean_ISMN(item)
        # item = self.clean_collection(item)
        # item = self.clean_ref_editeur(item)
        item = self.clean_duree(item)
        # item = self.clean_description(item)
        item = self.clean_url(item)
        return item

    def clean_titre(self, item):
        adapter= ItemAdapter(item)
        titre = adapter.get("titre")
        if titre:
            titre = titre.strip()
        adapter["titre"] = titre
        return item

    def clean_sous_titre(self, item):
        adapter= ItemAdapter(item)
        sous_titre = adapter.get("sous_titre")
        if sous_titre:
            sous_titre = sous_titre.strip()
        adapter["sous_titre"] = sous_titre
        return item

    def clean_compositeur(self, item):
        adapter= ItemAdapter(item)
        compositeur = adapter.get("compositeur")
        compositeur_temp = []
        if compositeur and compositeur != []:            
            for i in range(len(compositeur)):
                compositeur[i] = compositeur[i].strip()
                compositeur_temp.append(compositeur[i])
            adapter["compositeur"] = compositeur_temp
        return item

    def clean_arrangeur(self, item):
        adapter= ItemAdapter(item)
        arrangeur = adapter.get("arrangeur")
        arrangeur_temp = []
        if arrangeur and arrangeur != []:            
            for i in range(len(arrangeur)):
                arrangeur[i] = arrangeur[i].strip()
                arrangeur_temp.append(arrangeur[i])
            adapter["arrangeur"] = arrangeur_temp
        return item

    def clean_artiste(self, item):
        adapter= ItemAdapter(item)
        artiste = adapter.get("artiste")
        artiste_temp = []
        if artiste and artiste != []:            
            for i in range(len(artiste)):
                artiste[i] = artiste[i].strip()
                artiste_temp.append(artiste[i])
            adapter["artiste"] = artiste_temp
        return item

    def clean_edition(self, item):
        adapter= ItemAdapter(item)
        edition = adapter.get("edition")
        if edition:
            edition = edition.strip()
        adapter["edition"] = edition
        return item

    def clean_instrumentation(self, item):
        adapter= ItemAdapter(item)
        instrumentation = adapter.get("instrumentation")
        if instrumentation:
            instrumentation = instrumentation.strip()
        adapter["instrumentation"] = instrumentation
        return item

    def clean_niveau(self, item):
        adapter= ItemAdapter(item)
        niveau = adapter.get("niveau")
        if niveau:
            # niveau = niveau.replace(",",".")
            chiffres = re.findall(r'(\d+)', niveau)
            niveau = ".".join(chiffres)
            niveau = float(niveau)
        adapter["niveau"] = niveau
        return item

    def clean_annee_sortie(self, item):
        adapter= ItemAdapter(item)
        annee_sortie = adapter.get("annee_sortie")
        if annee_sortie:
            annee_sortie = int(annee_sortie.strip())
        adapter["annee_sortie"] = annee_sortie
        return item

    def clean_partie_euro(self, item):
        adapter= ItemAdapter(item)
        partie_euro = adapter.get("partie_euro")
        if partie_euro:
            if partie_euro == "Oui":
                partie_euro = True
            elif partie_euro == "No":
                partie_euro = False
        adapter["partie_euro"] = partie_euro
        return item

    def clean_genre(self, item):
        adapter= ItemAdapter(item)
        genre = adapter.get("genre")
        if genre:
            genre = genre.strip()
        adapter["genre"] = genre
        return item

    def clean_style(self, item):
        adapter= ItemAdapter(item)
        style = adapter.get("style")
        if style:
            style = style.strip()
        adapter["style"] = style
        return item

    def clean_ISMN(self, item):
        adapter= ItemAdapter(item)
        ISMN = adapter.get("ISMN")
        if ISMN:
            ISMN = ISMN.strip()
        adapter["ISMN"] = ISMN
        return item

    def clean_collection(self, item):
        adapter= ItemAdapter(item)
        collection = adapter.get("collection")
        if collection:
            collection = collection.strip()
        adapter["collection"] = collection
        return item

    def clean_ref_editeur(self, item):
        adapter= ItemAdapter(item)
        ref_editeur = adapter.get("ref_editeur")
        if ref_editeur:
            ref_editeur = ref_editeur.strip()
        adapter["ref_editeur"] = ref_editeur
        return item

    def clean_duree(self, item):
        adapter= ItemAdapter(item)
        duree = adapter.get("duree")
        if duree:
            duree = duree.strip()
            duree = datetime.strptime(duree, "%H:%M:%S").time()
        adapter["duree"] = duree
        return item

    def clean_description(self, item):
        adapter= ItemAdapter(item)
        description = adapter.get("description")
        # Pour le cas où la description serait tronquée
        if description:
            description = re.findall(r'.*[.!?]', description)[0]
        adapter["description"] = description
        return item

    def clean_url(self, item):
        adapter= ItemAdapter(item)
        url = adapter.get("url")
        if url:
            url = url.strip()
        adapter["url"] = url
        return item
