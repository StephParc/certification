
# Structure du projet:

```
.
├── docs/  
|    ├── E1.md
|    ├── E2.md
|    ├── E3.md
|    ├── E4.md
|    ├── E5.md
|    ├── E6.md
|    ├── E7.md  
|    ├── index.md  
|    └── structure_du_projet.md
├── Avant-projet/ 
|   ├── présentation certif.odp
|   └── référentiel écoresponsable.odt
├── E1/   
|    ├── grilles/
|       ├── GD01.odt
|       ├── grille utilisateur.odt
|       ├── GU01.odt
|       ├── GU02.odt
|       ├── GU03.odt
|       ├── GU04.odt
|       └── GU05.odt
|   └── E1.odt
├── E2/
|   └── E2.odt
├── E3/
|   └── E3.odt
├── E4/
|   ├── harmonie/
|       ├── BDD/
|           ├── pages/
|               ├── 1_auteurs.py
|               ├── 2_partitions.py
|               ├── 3_evenements.py
|               ├──
|           ├── routes/
|               ├── associations.py
|               ├── auteurs.py
|               ├── authentification.py
|               ├── evenements.py
|               ├── partitions_hbm.py
|               ├── partitions.py
|               └── users.py
|           ├── .env
|           ├── api_externe.py
|           ├── api_hbm.py
|           ├── app_streamlit.py
|           ├── auth.py
|           ├── config.py
|           ├── create_db.py
|           ├── crud.py
|           ├── hbm.db
|           ├── models.py
|           └── schemas.py
|       ├── harmonie/
|           ├── archives/
|               ├── musicshop_2025-02-27.csv
|               ├── musicshop_2025-07-02.csv
|               └── ...
|           ├── spiders/
|               └── hbm_scrap.py
|           ├── clean_scrapy.py 
|           ├── items.py
|           ├── middlewares.py
|           ├── musicshop_all.csv
|           ├── musicshop_last.csv
|           ├── musicshop_new.csv
|           ├── pipelines.py
|           ├── settings.py
|           └── sources/
|               ├── events.csv
|               └── users.csv
|       ├── scrapy.cfg
|       └── schema.md
|   RGPD_fake.ods
├── E6/
├── E7/
|   ├── .terraform/
|   ├── modules/
|        ├── resource_group/
|           ├── main.tf
|           ├── outputs.tf
|           └── variables.tf
|        ├── storage/
|           ├── main.tf
|           ├── outputs.tf
|           └── variables.tf
|   ├── (export_scrapy.py)
|   ├── main.tf
|   ├── provider.tf
|   ├── (test.py)
|   └── variables.tf 
├── .gitignore
├── (musicbrainz.org.json)
├── poetry.lock
├── pyproject.toml
└── requirements.txt

``` 
