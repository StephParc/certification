# gen_exchange_rates.py

import pandas as pd
import random
import os
from datetime import datetime

from utils.S3_utils import upload_file
from utils.logger_config import setup_logger, trace_action

logger_name = "E6 - Génération taux de change"
logger = setup_logger(logger_name)

@trace_action(logger_name)
def generate_exchange_rates():
    seed_path = "harmonie_dbt/seeds/currencies.csv"
    if not os.path.exists(seed_path):
        logger.error("Fichier currencies.csv introuvable")
        return
    
    currencies = pd.read_csv(seed_path)['currency_code'].tolist()

    base_rates = {
        'EUR': 1.0,
        'GBP': 0.84,
        'CHF': 0.95,
        'PLN': 4.30,
        'SEK': 11.20,
        'DKK': 7.45,
        'NOK': 11.50,
        'USD': 1.08,
    }
    rates_data = []
    today = datetime.now().strftime('%Y-%m-%d')

    for curr in currencies:
        base = base_rates.get(curr, 1.0)
        variation = random.uniform(0.99,1.01)
        final_rate = round(base*variation, 6) if curr != 'EUR' else 1.0

        rates_data.append({
            "date_key": today,
            "currency_code": curr,
            "exchange_rate": final_rate
        })

    df_rates = pd.DataFrame(rates_data)

    tmp_path = "/tmp/exchange_rates.csv"
    df_rates.to_csv(tmp_path, index=False)

    upload_file(tmp_path, "zone-brutes", f"E6/musicshop/exchange_rates/{today}.csv")
    logger.info(f"Taux de change générés et uploadés pour le {today}")

if __name__ == "__main__":
        generate_exchange_rates()
