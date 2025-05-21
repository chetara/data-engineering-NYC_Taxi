# 🚖 NYC Taxi ETL with PostgreSQL & Kestra

This project implements a clean, idempotent ETL (Extract, Transform, Load) workflow for NYC taxi trip data using [Kestra](https://kestra.io), an open-source data orchestrator, and PostgreSQL 15+ with support for native `MERGE`.

---

## 📜 Description

This Kestra workflow downloads monthly NYC Taxi trip data (either **yellow** or **green** taxi type), loads it into a **staging table**, computes a **normalized unique ID**, removes records already in the production table, and then safely **merges** new records into the **production table** using PostgreSQL’s native `MERGE` statement.

It supports:

- Green or yellow taxi datasets
- Year and month selection
- Efficient deduplication and idempotent ingestion
- Safe handling of incremental data loads

---

## 🧱 Kestra Architecture Overview

Kestra is a declarative orchestrator built on core architectural principles:

### 🔧 Core Components

| Component         | Description |
|------------------|-------------|
| **Flows**        | YAML-based definition of ETL logic (like this workflow) |
| **Tasks**        | Units of work (e.g., shell commands, SQL queries, file operations) |
| **Variables**    | Templating syntax to reuse logic dynamically (`{{inputs.taxi}}`) |
| **Plugins**      | Modular actions (PostgreSQL, Shell, Storage, etc.) |
| **Executions**   | Instances of flows running with given inputs |
| **Web UI & API** | Track flows, executions, logs, and retry logic |

### 🔁 Execution Lifecycle

1. **Inputs** collected via a UI form or API
2. **Variables** resolved to construct file names, table names, etc.
3. Tasks are **executed in sequence**, with logic branching for yellow/green taxi type
4. Outputs and logs are **tracked in the UI or logs**
5. Temporary files are **purged** post-success

---

## 🧪 Supported Inputs

| Input ID | Type | Description | Example |
|----------|------|-------------|---------|
| `taxi`   | SELECT | Taxi type | `yellow`, `green` |
| `year`   | SELECT | Year of data | `2019`, `2020` |
| `month`  | SELECT | Month of data | `01` to `12` |

---

## 🗂️ Workflow Overview

### 🔽 Step 1: **Download CSV**

Uses `wget` to download `.csv.gz` file from GitHub, decompresses using `gunzip`.

```bash
wget -qO- https://.../green_tripdata_2019-01.csv.gz | gunzip > green_tripdata_2019-01.csv
```

---

### 📄 Step 2: **Create Tables**

Creates two tables if not already present:

- `public.green_tripdata` — Production table
- `public.green_tripdata_staging` — Temporary staging table

Schema varies depending on taxi type.

---

### 📥 Step 3: **Copy CSV → Staging**

Loads the CSV into staging using `COPY IN`.

---

### 🧠 Step 4: **Add Unique ID**

Adds a **deterministic MD5 hash** (`unique_row_id`) per row using a combination of:

- Pickup/Dropoff datetime
- PULocationID / DOLocationID
- Fare amount / Distance

```sql
UPDATE staging_table
SET unique_row_id = md5(...), filename = '...'
```

---

### 🧹 Step 5: **Remove Existing Records**

Deletes from staging any rows that already exist in production:

```sql
DELETE FROM staging WHERE unique_row_id IN (SELECT unique_row_id FROM production);
```

---

### 🔁 Step 6: **Merge to Production**

Uses PostgreSQL 15+ `MERGE` to insert only non-duplicate records:

```sql
MERGE INTO production AS T
USING (SELECT DISTINCT ON (unique_row_id) * FROM staging) AS S
ON T.unique_row_id = S.unique_row_id
WHEN NOT MATCHED THEN INSERT (...)
```

---

### 🧼 Step 7: **Purge Temp Files**

Optionally deletes execution files to keep workspace clean.

---

## ✅ Features

- ✅ PostgreSQL-native `MERGE` for safe deduplication
- ✅ Uses hash-based deduplication, resilient to row order/format changes
- ✅ Table schemas per taxi type (yellow/green)
- ✅ Easy parameterization via `inputs`
- ✅ Fully observable via Kestra UI or API

---

## 📦 Requirements

- Kestra (local or cloud)
- PostgreSQL 15+ (for native `MERGE`)
- Docker setup (optional for local development)
- Network access to GitHub

---

## 🚀 Getting Started

### 1. Clone & Deploy Kestra

```bash
git clone https://github.com/your-org/kestra-taxi-etl.git
cd kestra-taxi-etl
```

### 2. Setup PostgreSQL

Use Docker Compose or existing DB. Credentials default to:

```ini
URL=jdbc:postgresql://postgres:5432/zoomcamp
USERNAME=admin
PASSWORD=admin
```

### 3. Run the Flow

Via UI or CLI:

```bash
kestra executions trigger --id zoomcamp.03_postgres_taxi \
  --inputs '{
    "taxi": "green",
    "year": "2019",
    "month": "01"
  }'
```

---

## 🧪 Testing

To test:

1. Load small month (e.g., Jan 2019)
2. Re-run same inputs — observe **no duplicates**
3. Load different month — new data appears in production table

---

## 📈 Monitoring & Observability

Kestra provides:

- Task-level logs
- Flow retries & error alerts
- Input/output inspection
- Visual DAG execution trace

---



## 🔐 Security & Idempotency

- All data is hashed before insert — avoids duplicates
- `TRUNCATE` staging table before every run
- Merges are conditional — nothing overwrites existing rows
- Good for production-grade ingestion


## 🗓️ Schedule & Backfills

### 📅 Automated Monthly Schedules

| Taxi Type | Cron Schedule         | Description                 |
|-----------|-----------------------|-----------------------------|
| Yellow    | `0 9 1 * *`           | 9 AM on 1st of every month  |
| Green     | `0 10 1 * *`          | 10 AM on 1st of every month |

Each run downloads and processes data for the **previous month**, based on the `trigger.date`.

---

### 🔁 Backfill Support

You can run historical loads using `--trigger-date`. Example:

```bash
kestra executions trigger --id zoomcamp.04_postgres_taxi \
  --inputs '{ "taxi": "yellow" }' \
  --trigger-date 2020-04-01
```

This processes `yellow_tripdata_2020-04.csv`.

---

## 🚀 Workflow Overview

This ETL job performs the following steps:

1. **Download** CSV file for the selected taxi and month
2. **Create tables** if not already present
3. **Copy CSV → staging table**
4. **Compute unique row ID**
5. **Remove already-existing rows**
6. **Merge new rows into production**
7. **Purge execution files**

---

## 🎛️ Inputs

| Input ID | Type   | Description         | Example Values |
|----------|--------|---------------------|----------------|
| `taxi`   | SELECT | Type of taxi        | `yellow`, `green` |

---

## 🔧 Variables

| Variable         | Description                                      |
|------------------|--------------------------------------------------|
| `file`           | File name, e.g. `yellow_tripdata_2020-01.csv`    |
| `staging_table`  | Staging table name in PostgreSQL                 |
| `table`          | Final target table name in PostgreSQL            |
| `data`           | Path to downloaded CSV file                      |

---

## 🔁 Deduplication Strategy

A deterministic `unique_row_id` is generated using fields like:

- VendorID
- Pickup/dropoff timestamp
- Location IDs
- Fare and distance

This enables idempotent loading, with no duplicates.

---

## ✅ Features

- 📅 Cron-based monthly ingestion
- 🔙 Historical backfill support
- 🧹 Deduplicated loads using `MERGE`
- 🧪 Easily testable
- 🔒 Idempotent & robust

---

## 🔐 PostgreSQL Details

- Requires PostgreSQL 15+ for native `MERGE`
- Tables are dynamically created by taxi type (yellow vs green)
- Primary key: `unique_row_id`
- Copy from CSV using `COPY IN`

---

## 📚 References

- [Kestra Scheduling](https://kestra.io/docs/concepts/triggers)
- [NYC TLC Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- [PostgreSQL MERGE](https://www.postgresql.org/docs/current/sql-merge.html)

