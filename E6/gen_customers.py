# gen_customers.py
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
        upload_file(tmp_cust, "zone-brutes", "E6/musicshop/customers.csv")

        logger.info(f"Répartition par pays:\n{df_customer['country'].value_counts()}")

if __name__ == "__main__":
    save_to_s3()

# Génération
# df_cust = generate_customers(250)
# df_cust.to_csv('customers.csv', index=False)
# print(f"✅ 250 clients générés dans customers.csv (Pays cibles : {len(allowed_countries)})")
# print(f"Répartition par pays:\n{df_cust['country'].value_counts()}")