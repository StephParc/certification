# gen_exchange_rates.py
"""
Musicshop Daily Exchange Rate Generator.

This module simulates a financial market feed by generating daily exchange 
rates for all currencies supported by the Musicshop platform. It ensures 
analytical consistency by reading the authoritative list of currencies 
from the dbt seed files.

Key Features:
1. dbt Integration: Sources the active currency list from 'currencies.csv' 
   to maintain cross-system integrity.
2. Market Simulation: Applies a randomized daily variation (±1%) to 
   predefined base rates (GBP, CHF, USD, etc.) against the Euro (base 1.0).
3. Automated S3 Archival: Delivers timestamped CSV files to the 
   'zone-brutes' bucket for historical analysis.
"""
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
    """
    Computes and uploads the daily exchange rate dataset.

    The function applies a random fluctuation to the base rates of 
    8 major currencies. The results are stored with a 'date_key' 
    to facilitate time-series joins in the Gold layer of the Data Warehouse.
    """
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

    upload_file(
        local_path=tmp_path, 
        bucket="zone-brutes", 
        s3_path=f"E6/musicshop/exchange_rates/{today}.csv",
        metadata={
                "source": "Genere par gen_exchange_rates.py",
                "step": "raw",
                "dag": "daily_exchange_rates_dag.py",
                "destination": "musicshop.raw.exchange_rates et zone-brutes/E6/musicshop/exchange_rates/"
            })

    logger.info(f"Taux de change générés et uploadés pour le {today}")

if __name__ == "__main__":
        generate_exchange_rates()
