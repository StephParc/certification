.
├── Avant-projet
│   ├── présentation certif.odp
│   └── référentiel écoresponsable.odt
├── Dockerfile
├── Dockerfile.app
├── Détail critères.ods
├── E1
│   ├── E1.odt
│   └── grilles
│       ├── GD01.odt
│       ├── GU01.odt
│       ├── GU02.odt
│       ├── GU03.odt
│       ├── GU04.odt
│       ├── GU05.odt
│       └── grille utilisateur.odt
├── E2
│   ├── E2.odt
│   ├── Gantt.odt
│   ├── cartographie.ods
│   ├── gantt.png
│   ├── matrice RICE.ods
│   ├── modèle support point hebdo.odt
│   └── veille.ods
├── E3
│   ├── E3.odt
│   └── support présentation E3.odp
├── E4
│   ├── E4.odt
│   ├── RGPD_fake.ods
│   ├── __init__.py
│   ├── harmonie
│   │   ├── BDD
│   │   │   ├── __init__.py
│   │   │   ├── api_externe.py
│   │   │   ├── api_hbm.py
│   │   │   ├── app_streamlit.py
│   │   │   ├── auth.py
│   │   │   ├── create_db.py
│   │   │   ├── crud.py
│   │   │   ├── crud_mongo.py
│   │   │   ├── database.py
│   │   │   ├── models.py
│   │   │   ├── pages
│   │   │   │   ├── 1_auteurs.py
│   │   │   │   ├── 2_partitions.py
│   │   │   │   └── 3_evenements.py
│   │   │   ├── routes
│   │   │   │   ├── __init__.py
│   │   │   │   ├── associations.py
│   │   │   │   ├── auteurs.py
│   │   │   │   ├── authentication.py
│   │   │   │   ├── evenements.py
│   │   │   │   ├── instruments.py
│   │   │   │   ├── instruments_dico.py
│   │   │   │   ├── musiciens.py
│   │   │   │   ├── partitions.py
│   │   │   │   ├── partitions_details.py
│   │   │   │   ├── partitions_hbm.py
│   │   │   │   ├── regles_substitution.py
│   │   │   │   └── users.py
│   │   │   ├── schemas.py
│   │   │   ├── schemas_mongo.py
│   │   │   └── sync_sql_mongo.py
│   │   ├── __init__.py
│   │   ├── harmonie
│   │   │   ├── __init__.py
│   │   │   ├── archives
│   │   │   │   ├── musicshop_2025-02-27.csv
│   │   │   │   ├── musicshop_2025-07-02.csv
│   │   │   │   └── musicshop_2025-08-03.csv
│   │   │   ├── clean_scrapy.py
│   │   │   ├── items.py
│   │   │   ├── middlewares.py
│   │   │   ├── pipelines.py
│   │   │   ├── settings.py
│   │   │   └── spiders
│   │   │       ├── hbm_scrap.py
│   │   ├── scrapy.cfg
│   │   └── sources
│   │       ├── collections.json
│   │       ├── events.csv
│   │       ├── fichier_base_test.csv
│   │       ├── instruments.csv
│   │       ├── instruments.json
│   │       ├── musiciens.json
│   │       ├── partitions.json
│   │       ├── regles_substitution.json
│   │       ├── users.csv
│   │       └── users_demo.csv
│   ├── registre-traitement-simplifie.ods
│   └── schema.md
├── E5
│   ├── E5.odt
│   ├── __init__.py
│   ├── ingest_ticketmaster.py
│   ├── load_ticketmaster_to_pg.py
│   ├── load_to_db.py
│   └── ticketmaster_harvester.py
├── E6
│   ├── E6.odt
│   ├── __init__.py
│   ├── gen_customers.py
│   ├── gen_exchange_rates.py
│   ├── gen_orders.py
│   ├── ingest_customers_to_postgres.py
│   ├── ingest_orders_to_postgres.py
│   ├── ingest_rates_to_postgres.py
│   └── update_customer_profiles.py
├── E7
│   ├── E7.odt
│   ├── Matrice des droits.ods
│   ├── __init__.py
│   ├── benchmark.odp
│   └── harvester.py
├── __init__.py
├── app_catalog.py
├── backups
│   ├── mongo_20260307T171023.gz
│   ├── mongo_20260308T000000.gz
│   ├── postgres_hbm_20260307T171023.sql
│   └── postgres_hbm_20260308T000000.sql
├── certification.log
├── config
│   ├── __init__.py
│   ├── access_control.json
│   └── config.py
├── dags
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
├── data_catalog.json
├── docker-compose.yml
├── garage.toml
├── garage.toml.template
├── garage_dl.txt
├── harmonie_dbt
│   ├── README.md
│   ├── analyses
│   │   └── rapport_mensuel.sql
│   ├── dbt_packages
│   ├── package-lock.yml
│   ├── packages.yml
│   ├── profiles.yml
│   ├── seeds
│   │   ├── countries.csv
│   │   └── currencies.csv
│   ├── snapshots
│   │   └── snp_customers.sql
│   ├── target
│   │   ├── manifest.json
│   │   └── semantic_manifest.json
│   └── tests
│       ├── assert_fact_has_valid_genres.sql
│       └── assert_unique_location_key.sql
├── logs
│   ├── dbt.log
│   ├── rejets
│   │   ├── api_musicbrainz
│   │   ├── imports_global
│   │   └── sync
├── nginx
│   └── nginx.conf
├── ngrok.yml
├── ngrok.yml.template
├── poetry.lock
├── pyproject.toml
├── requirements-airflow.txt
├── requirements-app.txt
├── scripts_postgres_init
│   ├── setup_musicshop.sql
│   └── setup_ticketmaster.sql
├── setup_infra.sh
└── utils
    ├── S3_utils.py
    ├── __init__.py
    ├── drop_clean.py
    ├── init_mongo.py
    ├── logger_config.py
    └── utils_functions.py