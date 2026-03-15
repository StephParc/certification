
# Structure du projet:

```
.
├── Avant-projet/ 
|   ├── présentation certif.odp
|   └── référentiel écoresponsable.odt
├── backups
├── certification.log
├── config
│   ├── __init__.py
│   ├── access_control.json
│   └── config.py
├── dags/
│   ├── catalog_dag.py
│   ├── daily_events_update_dag.py
│   ├── daily_exchange_rates_dag.py
│   ├── daily_musicshop_update_dag.py
│   ├── daily_scrapy_update_dag.py
│   ├── daily_synchro_dag.py
│   ├── daily_ticketmaster_update_dag.py
│   ├── sauvegarde_bases_dag.py
│   ├── setup_hbm_dag.py
│   ├── simulate_musicshop_customers_dag.py
│   ├── simulate_musicshop_orders_dag.py
│   └── test_alerting.py
├── docs/  
|    ├── E1.md
|    ├── E2.md
|    ├── E3.md
|    ├── E4.md
|    ├── E5.md
|    ├── E6.md
|    ├── E7.md  
|    ├── index.md 
|    ├── parametrages_utilitaires.md  
|    └── structure_du_projet.md
├── E1/   
|    ├── grilles/
|       ├── GD01.odt
|       ├── grille utilisateur.odt
|       ├── GU01.odt
|       ├── GU02.odt
|       ├── GU03.odt
|       ├── GU04.odt
|       ├── GU05.odt
|   └── E1.odt  
├── E2/   
|    ├── cartographie.ods
|    ├── E2.odt
|    ├── Gantt.odt
|    ├── gantt.png
|    ├── matrice RICE.ods
|    ├── modèle de support point hebdo.odt
|    └── veille.ods
├── E3/   
|    ├── E3.odt
|    └── support présentation E3.odp
├── E4/
|   ├── harmonie/
|       ├── BDD/                            
|           ├── pages/                      
|               ├── 1_auteurs
|               ├── 2_partitions
|               ├── 3_événements
|               ├──
|           ├──routes/                      
|               ├── __init__.py
|               ├── associations.py
|               ├── auteurs.py
|               ├── authenification.py
|               ├── evenements.py
|               ├── instruments_dico.py
|               ├── instruments.py
|               ├── musiciens.py
|               ├── partitions_details.py
|               ├── partitions_hbm.py
|               ├── partitions.py
|               ├── regles_substitution.py
|               └── users.py
|           ├── __init__.py
|           ├── api_externe.py              
|           ├── api_hbm.py                  
|           ├── app_streamlit.py            
|           ├── auth.py
|           ├── create_db.py                
|           ├── crud_mongo.py               
|           ├── crud.py                     
|           ├── database.py                 
|           ├── models.py                   
|           ├── schemas_mongo.py            
|           ├── schemas.py                  
|           └── sync_sql_mongo.py            
|       ├── harmonie/                        
|           ├── spiders/
|               ├── __init__.py
|               └── hbm_scrap.py            
|           ├── __init__.py
|           ├── clean_scrapy.py                    
|           ├── items.py                     
|           ├── middlewares.py
|           ├── pipelines.py                
|           └── settings.py                 
|       ├── sources/                        
|           ├── collections.json            
|           ├── events.csv
|           ├── fichier_base_test.csv
|           ├── users_demo.csv              
|           └── users.csv                   
|       ├── __init__.py
|       └── scrapy.cfg
|   ├── __init__.py
|   ├── E4.odt                              
|   ├── RGPD_fake.ods                       
|   └── schema.md
├── E5/   
|    ├── E5.odt
|    ├── __init__.py
|    ├── ingest_ticketmaster.py
|    ├── load_tickermaster_to_pg.py
|    ├── load_to_db.py
|    └── ticketmaster_harvester.py
├── E6/   
|    ├── E6.odt
|    ├── __init__.py
|    ├── gen_customers.py
|    ├── gen_exchange_rates.py
|    ├── gen_orders.py
|    ├── ingest_customers_to_postgres.py
|    ├── ingest_orders_to_postgres.py
|    ├── ingest_rates_to_posgres.py
|    └── update_customer_profiles.py
├── E7/
|   ├── __ini__.py
|   ├── benchmark.odp
|   ├── E7.odt
|   └── harvester.py
├── harmonie_dbt/
|    ├── analyses/
|       └── rapport_mensuel.sql
|    ├── macros/
|       └── generate_schema_name.sql    
|    ├── models/
|       ├── musicshop
|           ├── gold/
|               ├── _gold_schema.yml
|               ├── dim_customers.sql
|               ├── dim_dates_musicshop.sql
|               ├── dim_products.sql
|               ├── fact_orders.sql
|               └── view_fact_orders.sql
|           ├── silver/
|               └── int_orders_converted.sql
|           └── staging/
|               ├── _sources.yml
|               └── stg_musicshop_orders.sql
|       └── ticketmaster
|           ├── marts/
|               ├── dim_dates.sql
|               ├── dim_genres.sql
|               ├── dim_venues.sql
|               ├── fact_events.sql
|               └── schema.yml
|           └── staging/
|               ├── _sources_.sql
|               ├── stg_ticketmaster.sql
|               └── stg_ticketmaster.yml
|    ├── seeds/
|       ├── countries.csv
|       └── currencies.csv
|    └── snapshots/                        
|       └── snp_customers.sql
|    └── tests/                         
|       ├── assert_fact_has_valid_genres.sql
|       └── assert_unique_location_key.sql
|    ├── dbt_project.yml                
|    ├── packages.yml                   
|    └── profiles.yml
├── logs/
├── nginx/
│   └── nginx.conf
├── plugins/
├── scripts_postgres_init/
|    ├── setup_musicshop.sql
|    └── setup_ticketmaster.sql
├── utils
|   ├── __init__.py
|   ├── drop_clean.py
|   ├── init_mongo.py
|   ├── logger_config.py
|   ├── S3_utils.py
|   └── utils_functions.py
├── ngrok.yml
├── poetry.lock
├── pyproject.toml
├── requirements-airflow.txt
├── requirements-app.txt
├── scripts_postgres_init
│   ├── setup_musicshop.sql
│   └── setup_ticketmaster.sql
├── .env
├── .env.last_run
├── .env.template
├── .gitignore
├── app_catalog.py
├── data_catalog.json
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.app
├── garage_dl.txt
├── garage.toml
├── garage.toml.template
├── ngrok.yml
├── ngrok.yml.template
├── poetry.lock
├── pyproject.toml
├── requirements-airflow.txt
├── requirements-app.txt
└── setup_infra.sh
``` 
