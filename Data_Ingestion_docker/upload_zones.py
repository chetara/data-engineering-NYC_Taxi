import pandas as pd
from sqlalchemy import create_engine, text
import time

# --- Config ---
DB_USER = "root"
DB_PASS = "root"
DB_HOST = "pgdatabase"  # Use service name from docker-compose
DB_PORT = "5432"
DB_NAME = "nyc_taxi"
ZONES_CSV = "zones.csv"
ZONES_TABLE = "zones"

# --- Connect to PostgreSQL ---
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Wait until the DB is ready
for attempt in range(5):
    try:
        with engine.connect() as conn:
            print(" Connected to PostgreSQL.")
            break
    except Exception:
        print(f" Waiting for DB... (attempt {attempt + 1})")
        time.sleep(5)
else:
    raise Exception(" Could not connect to the database.")

# --- Create zones table ---
create_zones_table = """
CREATE TABLE IF NOT EXISTS zones (
    "LocationID" INTEGER PRIMARY KEY,
    "Borough" TEXT,
    "Zone" TEXT,
    "service_zone" TEXT
);
"""

with engine.begin() as conn:
    conn.execute(text(create_zones_table))
    print("  Table 'zones' created (if not exists).")

# --- Load and upload the CSV ---
zones_df = pd.read_csv(ZONES_CSV)
zones_df.to_sql(name=ZONES_TABLE, con=engine, if_exists="replace", index=False)
print(" Zones data uploaded successfully.")
