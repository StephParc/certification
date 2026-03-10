
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
|    └── structure_du_projet.md
├── E1/   
├── E2/
├── E3/
├── E4/
├── E5/
├── E6/
├── E7/
├── harmonie_dbt
├── logs
├── nginx
│   └── nginx.conf
├── ngrok.yml
├── poetry.lock
├── pyproject.toml
├── requirements-airflow.txt
├── requirements-app.txt
├── scripts_postgres_init
│   ├── setup_musicshop.sql
│   └── setup_ticketmaster.sql
├── setup_infra.sh
├── utils
|   ├── __init__.py
|   ├── drop_clean.py
|   ├── init_mongo.py
|   ├── logger_config.py
|   ├── S3_utils.py
|   └── utils_functions.py
├── .gitignore
├── app_catalog.py
├── certification.log
├── data_catalog.json   
├── poetry.lock
├── pyproject.toml
└── requirements.txt

``` 
