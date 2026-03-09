# gen_customers.py
"""
Musicshop Synthetic Customer Generator.

This module generates a realistic, internationally-diverse customer dataset 
to simulate retail activity. It leverages the Faker library to produce 
localized data (names, addresses, phone formats) based on a list of 
supported countries.

Operational Features:
1. Integration with dbt Seeds: Reads 'countries.csv' from the dbt project 
   to ensure data consistency across the analytical pipeline.
2. Multi-Localization: Uses specific Faker locales (e.g., fr_FR, de_DE, en_GB) 
   to generate authentic regional data.
3. Automated S3 Delivery: Uploads the generated dataset directly to the 
   S3 Data Lake (Bronze zone) with rich audit metadata.
"""
import pandas as pd
from faker import Faker
import random
import os

from utils.S3_utils import upload_file
from utils.logger_config import setup_logger, trace_action

logger_name = "E6 - Génération clients Musicshop"
logger = setup_logger(logger_name)


@trace_action(logger_name)
def generate_customers(n=200):
    """
    Produces a DataFrame of synthetic customers.

    The function dynamically maps countries to their corresponding Faker 
    locale. Each record includes a randomized customer profile 
    (occasional, amateur, professional) and a historical creation date 
    spanning the last two years.

    Returns:
        pd.DataFrame: A collection of N customers with localized attributes.
    """
    seed_path = "harmonie_dbt/seeds/countries.csv"
    if not os.path.exists(seed_path):
        logger.error(f"Erreur: le fichier {seed_path} est introuvable. Lancer 'dbt seed'")
        return

    allowed_countries = pd.read_csv(seed_path)['country'].tolist()
    customers = []
    profiles = ["occasionnel", "amateur", "professionnel"]

    fakers = {
        "France": Faker("fr_FR"),
        "United Kingdom": Faker("en_GB"),
        "Germany": Faker("de_DE"),
        "Poland": Faker("pl_PL"),
        "Spain": Faker("es_ES"),
        "Italy": Faker("it_IT"),
        "Portugal": Faker("pt_PT"),
        "Sweden": Faker("sv_SE"),
        "Switzerland": Faker("fr_CH"),
        "Denmark": Faker("da_DK"),
        "Norway": Faker("no_NO"),
        "United States": Faker("en_US"),
        "Ireland": Faker("en_IE"),
        "Belgium": Faker("fr_BE")
    }
    default_fake = Faker("fr_FR")

    for i in range(1, n + 1):
        country = random.choice(allowed_countries)
        fake = fakers.get(country, default_fake)
        
        customers.append({
            "customer_id": f"CUST-{i:04d}",
            "name": fake.name(),
            "address": fake.address().replace('\n',', ').replace('\r',''),
            "postal_code": fake.postcode(),
            "email": f"{fake.user_name()}@{fake.free_email_domain()}",
            "country": country,
            "city": fake.city(),
            "profile": random.choice(profiles),
            "created_at": fake.date_between(start_date='-2y', end_date='-1y').strftime('%Y-%m-%d %H:%M:%S')
        })
    return pd.DataFrame(customers)

def save_to_s3():
    df_customer = generate_customers(250)
    if not df_customer.empty:
        # Chemins temporaires pour l'upload
        tmp_cust = "/tmp/customers.csv"

        df_customer.to_csv(tmp_cust, index=False)
        upload_file(
            local_path=tmp_cust,
            bucket="zone-brutes",
            s3_path="E6/musicshop/customers.csv",
            metadata={
                "source": "Généré par gen_customers.py",
                "step": "raw",
                "dag": "simulate_musicshop_customers_dag.py",
                "destination": "musicshop.raw.customer"
            })

        logger.info(f"Répartition par pays:\n{df_customer['country'].value_counts()}")

if __name__ == "__main__":
    save_to_s3()
