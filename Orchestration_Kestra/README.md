# 🚖 Scheduled NYC Taxi ETL with Kestra & PostgreSQL

This workflow (`04_postgres_taxi`) is a **monthly scheduled ETL pipeline** for processing NYC Taxi data (green/yellow). It supports automated scheduling, clean deduplication, PostgreSQL-native `MERGE`, and easy **backfilling** via `--trigger-date`.

---

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

---

## 🛠️ Example: Full CLI Trigger

```bash
kestra executions trigger --id zoomcamp.04_postgres_taxi \
  --inputs '{ "taxi": "green" }' \
  --trigger-date 2019-06-01
```

---

## 📁 Output Cleanup

Temporary files are purged post-run with:

```yaml
type: io.kestra.plugin.core.storage.PurgeCurrentExecutionFiles
```

This keeps executions lightweight and clean.

---

## 🤝 Contributing

Feedback and PRs welcome. Let us know how you're using this workflow or what features you'd like to see next.
