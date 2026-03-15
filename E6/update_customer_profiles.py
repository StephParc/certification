# update_customers_profiles.py
"""
Musicshop Customer Profile Mutation Service.

This simulation utility performs random updates on the customer base to 
simulate behavioral changes over time. It is used to test the resilience 
and accuracy of analytical pipelines regarding data volatility.

Key Features:
1. Random Selection: Targeted updates on a parameterized number of 
   randomly selected customers.
2. Profile Cycling: Re-assigns customers to one of the three core 
   profiles (occasional, amateur, professional).
3. Audit Trail: Automatically updates the 'updated_at' timestamp for 
   proper Change Data Capture (CDC) tracking.
"""
import psycopg2
import random
from config.config import SQL_MUSICSHOP_URL
from utils.logger_config import setup_logger, trace_action

logger_name = "E6 - Mutation profils"
logger = setup_logger(logger_name)

@trace_action(logger_name)
def mutate_random_customers(n=5):
    """
    Randomly updates the profiles of N customers in the PostgreSQL database.

    This function picks N random customer IDs and assigns each a new 
    profile from the standard list. This simulates real-world customer 
    evolution (e.g., an amateur becoming a professional).

    Args:
        n (int): The number of customer records to mutate. Defaults to 5.
    """
    profiles = ["occasionnel", "amateur", "professionnel"]

    try:
        conn = psycopg2.connect(SQL_MUSICSHOP_URL)
        cur = conn.cursor()

        cur.execute("SELECT customer_id FROM raw.customer ORDER BY RANDOM() LIMIT %s", (n,))
        customer_ids = [row[0] for row in cur.fetchall()]

        for cid in customer_ids:
            new_profile = random.choice(profiles)
            cur.execute(
                "UPDATE raw.customer SET profile = %s, updated_at = CURRENT_TIMESTAMP WHERE customer_id = %s",
                (new_profile, cid)
            )

        conn.commit()
        logger.info(f"Mutation réussie: {len(customer_ids)} profils clients mis à jour")

        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Erreur lors de la mutation: {e}")
        raise

if __name__ == "__main__":
    mutate_random_customers(5)