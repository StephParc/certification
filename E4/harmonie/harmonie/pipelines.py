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
    """
    A pipeline class for processing and cleaning items scraped by a Scrapy spider.
    This class contains methods to clean various fields of the scraped items.
    """

    def process_item(self, item, spider):
        """
        Process an item by applying various cleaning methods to its fields.

        Args:
            item: The scraped item containing various fields to be cleaned.
            spider: The Scrapy spider that scraped the item.

        Returns:
            item: The cleaned item with processed fields.
        """
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
        """
        Clean the 'titre' field of the item by stripping any leading or trailing whitespace.

        Args:
            item: The item whose 'titre' field needs to be cleaned.

        Returns:
            item: The item with the cleaned 'titre' field.
        """
         
        adapter= ItemAdapter(item)
        titre = adapter.get("titre")
        if titre:
            titre = titre.strip()
        adapter["titre"] = titre
        return item

    def clean_sous_titre(self, item):
        """
        Clean the 'sous_titre' field of the item by stripping any leading or trailing whitespace.

        Args:
            item: The item whose 'sous_titre' field needs to be cleaned.

        Returns:
            item: The item with the cleaned 'sous_titre' field.
        """
        adapter= ItemAdapter(item)
        sous_titre = adapter.get("sous_titre")
        if sous_titre:
            sous_titre = sous_titre.strip()
        adapter["sous_titre"] = sous_titre
        return item

    def clean_compositeur(self, item):
        """
        Clean the 'compositeur' field of the item by stripping any leading or trailing whitespace
        from each entry in the list.

        This method processes the 'compositeur' field, which is expected to be a list of strings.
        Each string in the list is stripped of leading and trailing whitespace, and the cleaned
        list is then updated back to the item.

        Args:
            item: The item whose 'compositeur' field needs to be cleaned. The 'compositeur'
                field should be a list of strings.

        Returns:
            item: The item with the cleaned 'compositeur' field.
        """
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
        """
        Clean the 'compositeur' field of the item by stripping any leading or trailing whitespace
        from each entry in the list.

        This method processes the 'compositeur' field, which is expected to be a list of strings.
        Each string in the list is stripped of leading and trailing whitespace, and the cleaned
        list is then updated back to the item.

        Args:
            item: The item whose 'compositeur' field needs to be cleaned. The 'compositeur'
                field should be a list of strings.

        Returns:
            item: The item with the cleaned 'compositeur' field.
        """
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
        """
        Clean the 'compositeur' field of the item by stripping any leading or trailing whitespace
        from each entry in the list.

        This method processes the 'compositeur' field, which is expected to be a list of strings.
        Each string in the list is stripped of leading and trailing whitespace, and the cleaned
        list is then updated back to the item.

        Args:
            item: The item whose 'compositeur' field needs to be cleaned. The 'compositeur'
                field should be a list of strings.

        Returns:
            item: The item with the cleaned 'compositeur' field.
        """
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
        """
        Clean the 'edition' field of the item by stripping any leading or trailing whitespace.

        Args:
            item: The item whose 'edition' field needs to be cleaned.

        Returns:
            item: The item with the cleaned 'edition' field.
        """
        adapter= ItemAdapter(item)
        edition = adapter.get("edition")
        if edition:
            edition = edition.strip()
        adapter["edition"] = edition
        return item

    def clean_instrumentation(self, item):
        """
        Clean the 'instrumentation' field of the item by stripping any leading or trailing whitespace.

        Args:
            item: The item whose 'instrumentation' field needs to be cleaned.

        Returns:
            item: The item with the cleaned 'instrumentation' field.
        """
        adapter= ItemAdapter(item)
        instrumentation = adapter.get("instrumentation")
        if instrumentation:
            instrumentation = instrumentation.strip()
        adapter["instrumentation"] = instrumentation
        return item

    def clean_niveau(self, item):
        """
        Clean the 'niveau' field of the item by extracting numerical values and converting them to a float.

        This method converts comma to dot to get a float value for the 'niveau' field. 

        Args:
            item: The item whose 'niveau' field needs to be cleaned. The 'niveau' field should be a string
                containing numerical values.

        Returns:
            item: The item with the cleaned 'niveau' field, converted to a float.
        """
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
        """
        Clean the 'annee_sortie' field of the item by stripping any leading or trailing whitespace.

        Args:
            item: The item whose 'annee_sortie' field needs to be cleaned.

        Returns:
            item: The item with the cleaned 'annee_sortie' field.
        """
        adapter= ItemAdapter(item)
        annee_sortie = adapter.get("annee_sortie")
        if annee_sortie:
            annee_sortie = int(annee_sortie.strip())
        adapter["annee_sortie"] = annee_sortie
        return item

    def clean_partie_euro(self, item):
        """
        Clean the 'partie_euro' field of the item by converting string values to boolean.

        This method processes the 'partie_euro' field, which is expected to be a string indicating
        "Oui" or "No". It converts these string values to their corresponding boolean values, True or False.

        Args:
            item: The item whose 'partie_euro' field needs to be cleaned. The 'partie_euro' field
                should be a string, either "Oui" or "No".

        Returns:
            item: The item with the cleaned 'partie_euro' field, converted to a boolean.
        """
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
        """
        Clean the 'genre' field of the item by stripping any leading or trailing whitespace.

        Args:
            item: The item whose 'genre' field needs to be cleaned.

        Returns:
            item: The item with the cleaned 'genre' field.
        """
        adapter= ItemAdapter(item)
        genre = adapter.get("genre")
        if genre:
            genre = genre.strip()
        adapter["genre"] = genre
        return item

    def clean_style(self, item):        
        """
        Clean the 'style' field of the item by stripping any leading or trailing whitespace.

        Args:
            item: The item whose 'style' field needs to be cleaned.

        Returns:
            item: The item with the cleaned 'style' field.
        """

        adapter= ItemAdapter(item)
        style = adapter.get("style")
        if style:
            style = style.strip()
        adapter["style"] = style
        return item

    def clean_ISMN(self, item):
        """
        Clean the 'ISMN' field of the item by stripping any leading or trailing whitespace.

        Args:
            item: The item whose 'ISMN' field needs to be cleaned.

        Returns:
            item: The item with the cleaned 'ISMN' field.
        """
        adapter= ItemAdapter(item)
        ISMN = adapter.get("ISMN")
        if ISMN:
            ISMN = ISMN.strip()
        adapter["ISMN"] = ISMN
        return item

    def clean_collection(self, item):
        """
        Clean the 'collection' field of the item by stripping any leading or trailing whitespace.

        Args:
            item: The item whose 'collection' field needs to be cleaned.

        Returns:
            item: The item with the cleaned 'collection' field.
        """
        adapter= ItemAdapter(item)
        collection = adapter.get("collection")
        if collection:
            collection = collection.strip()
        adapter["collection"] = collection
        return item

    def clean_ref_editeur(self, item):
        """
        Clean the 'ref_editeur' field of the item by stripping any leading or trailing whitespace.

        Args:
            item: The item whose 'ref_editeur' field needs to be cleaned.

        Returns:
            item: The item with the cleaned 'ref_editeur' field.
        """        
        adapter= ItemAdapter(item)
        ref_editeur = adapter.get("ref_editeur")
        if ref_editeur:
            ref_editeur = ref_editeur.strip()
        adapter["ref_editeur"] = ref_editeur
        return item

    def clean_duree(self, item):
        """
        Clean the 'duree' field of the item by stripping whitespace and converting it to a time object.

        This method processes the 'duree' field, which is expected to be a string representing time
        in the format "HH:MM:SS". It strips any leading or trailing whitespace and converts the string
        to a datetime.time object.

        Args:
            item: The item whose 'duree' field needs to be cleaned. The 'duree' field should be a
                string in the format "HH:MM:SS".

        Returns:
            item: The item with the cleaned 'duree' field, converted to a time object.
        """
        adapter= ItemAdapter(item)
        duree = adapter.get("duree")
        if duree:
            duree = duree.strip()
            duree = datetime.strptime(duree, "%H:%M:%S").time()
        adapter["duree"] = duree
        return item

    def clean_description(self, item):
        """
        Clean the 'description' field of the item by extracting the first complete sentence.

        This method processes the 'description' field, which is expected to be a string. It uses
        regular expressions to find the first complete sentence ending with a period, exclamation
        mark, or question mark, which is useful in cases where the description might be truncated.

        Args:
            item: The item whose 'description' field needs to be cleaned. The 'description' field
                should be a string.

        Returns:
            item: The item with the cleaned 'description' field, containing only the first complete sentence.
        """
        adapter= ItemAdapter(item)
        description = adapter.get("description")
        # Pour le cas où la description serait tronquée
        if description:
            description = re.findall(r'.*[.!?]', description)[0]
        adapter["description"] = description
        return item

    def clean_url(self, item):
        """
        Clean the 'url' field of the item by stripping any leading or trailing whitespace.

        Args:
            item: The item whose 'url' field needs to be cleaned.

        Returns:
            item: The item with the cleaned 'url' field.
        """
        adapter= ItemAdapter(item)
        url = adapter.get("url")
        if url:
            url = url.strip()
        adapter["url"] = url
        return item
