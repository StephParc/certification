# gen_orders.py

import pandas as pd
import random
import uuid
from datetime import datetime
from sqlalchemy import create_engine

from utils.S3_utils import upload_file
from utils.logger_config import setup_logger, trace_action
from config.config import SQL_MUSICSHOP_URL, SQL_DATABASE_URL

logger_name = "E6 - Génération commandes"
logger = setup_logger(logger_name)

@trace_action(logger_name)
def generate_orders(n=50):
    engine_ms = create_engine(SQL_MUSICSHOP_URL)
    engine_hbm = create_engine(SQL_DATABASE_URL)

    customers = pd.read_sql("SELECT * FROM raw.customer", engine_ms)

    partitions = pd.read_sql(
        """SELECT
            partition_id,
            titre,
            ref_editeur,
            edition
            FROM public."TB_partition"
        """, engine_hbm)

    orders = []
    for _ in range(n):
        cust = customers.sample(1).iloc[0]
        items = partitions.sample(random.randint(1,3))

        order_id = f"ORD-{str(uuid.uuid4())[:8].upper()}"
        order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for _, item in items.iterrows():
            orders.append({
                "order_id": order_id,
                "customer_id": cust['customer_id'],
                "system_source": f"DB_{cust['country'].upper()[:3]}",
                "name": cust['name'],
                "address": cust['address'],
                "postal_code": cust['postal_code'],
                "email": cust['email'],
                "country": cust['country'],
                "profile": cust['profile'],
                "order_date": order_date,
                "partition_id": item['partition_id'],
                "titre": item['titre'],
                "ref_editeur": item['ref_editeur'],
                "edition": item['edition'],
                "quantity": random.randint(1,3),
                "local_price": round(random.uniform(70.00,250.00),2)
            })

    df_orders = pd.DataFrame(orders)

    filename = f"orders_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"
    tmp_path = f"/tmp/{filename}"
    df_orders.to_csv(tmp_path, index=False)

    upload_file(
        local_path=tmp_path, 
        bucket="zone-brutes", 
        s3_path=f"E6/musicshop/orders/{filename}",
        metadata={
            "source": "Généré par gen_orders.py à partir de hbm.public.TB_partition et customer",
            "step": "raw",
            "dag": "simulate_musicshop_orders_dag.py",
            "destination": "musicshop.raw.orders et zone-brutes/E6/musicshop/archives"
            })

    logger.info(f"{n} commandes générées ({len(orders)} lignes) et uploadées")

if __name__ == "__main__":
    generate_orders(50)