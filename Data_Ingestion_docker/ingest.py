import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import time

# --- Config ---
DB_USER = "root"
DB_PASS = "root"
DB_HOST = "pgdatabase"  # Docker service name from docker-compose
DB_PORT = "5432"
DB_NAME = "nyc_taxi"
CSV_FILE = "yellow_tripdata_2021-01.csv"
TABLE_NAME = "yellow_taxi_data"
CHUNK_SIZE = 10_000

# --- Connect to PostgreSQL ---
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Wait for DB to be ready
for attempt in range(5):
    try:
        with engine.connect() as conn:
            print(" Connected to PostgreSQL.")
            break
    except OperationalError:
        print(f" Waiting for DB... (attempt {attempt+1})")
        time.sleep(5)
else:
    raise Exception(" Could not connect to the database.")

# --- Create table ---
create_table_query = """
CREATE TABLE IF NOT EXISTS yellow_taxi_data (
    vendorid INTEGER,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count INTEGER,
    trip_distance FLOAT,
    ratecodeid INTEGER,
    store_and_fwd_flag TEXT,
    pulocationid INTEGER,
    dolocationid INTEGER,
    payment_type INTEGER,
    fare_amount FLOAT,
    extra FLOAT,
    mta_tax FLOAT,
    tip_amount FLOAT,
    tolls_amount FLOAT,
    improvement_surcharge FLOAT,
    total_amount FLOAT,
    congestion_surcharge FLOAT
);
"""

with engine.begin() as conn:
    conn.execute(text(create_table_query))
    print(" Table created (if not exists).")

# --- Load and upload in chunks ---
for i, chunk in enumerate(pd.read_csv(CSV_FILE, chunksize=CHUNK_SIZE, dtype={'store_and_fwd_flag': str})):
    print(f" Uploading chunk {i+1} with {len(chunk)} rows...")

    # Normalize column names
    chunk.columns = [col.lower() for col in chunk.columns]

    # Convert datetimes
    chunk["tpep_pickup_datetime"] = pd.to_datetime(chunk["tpep_pickup_datetime"])
    chunk["tpep_dropoff_datetime"] = pd.to_datetime(chunk["tpep_dropoff_datetime"])

    # Upload to Postgres
    chunk.to_sql(name=TABLE_NAME, con=engine, if_exists="append", index=False)

print(" All data uploaded successfully.")
