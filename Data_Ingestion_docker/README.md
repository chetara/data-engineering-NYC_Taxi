# NYC Yellow Taxi Data Pipeline with Docker, PostgreSQL, and pgAdmin

This project demonstrates end-to-end data ingestion and exploration using the **NYC Yellow Taxi trip data** for January 2021. It features:
- Dockerized PostgreSQL and pgAdmin
- Python-based chunked ingestion from CSV to PostgreSQL
- Data exploration via SQL and Jupyter Notebooks
- Preparation for future Apache Spark analytics
---

## Project Structure

```
.
├── Dockerfile
├── docker-compose.yml
├── ingest.py
├── upload_zones.py
├── yellow_tripdata_2021-01.csv
├── zones.csv
├── requirements.txt
└── README.md
```

---


## 🛠️ Technologies Used
- Python 3.12
- Pandas
- SQLAlchemy
- PostgreSQL 14
- Docker & Docker Compose
- pgAdmin 4
- Jupyter Notebooks
- Power BI (for future visualization)

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <my_repo_url>
cd NYC_Yellow_Taxi
```

### 2. Add the Data Files
Download and place the following files in the project root:
- `yellow_tripdata_2021-01.csv` – Taxi trip data.
- `zones.csv` – Taxi zone lookup table.

### 3. Build and Run the Docker Containers
```bash
docker-compose up --build
```
This will:
- Start a PostgreSQL database
- Start pgAdmin (available at `http://localhost:8080` with email `admin@admin.com` and password `admin`)
- Run ingestion scripts that:
  - Create and populate the `yellow_taxi_data` table from the CSV file
  - Create and populate the `zones` table from `zones.csv`

---

## Database Schema

### `yellow_taxi_data`
| Column                 | Type    |
|------------------------|---------|
| vendorid              | INTEGER |
| tpep_pickup_datetime  | TIMESTAMP |
| tpep_dropoff_datetime | TIMESTAMP |
| passenger_count       | INTEGER |
| trip_distance         | FLOAT   |
| ratecodeid            | INTEGER |
| store_and_fwd_flag    | TEXT    |
| pulocationid          | INTEGER |
| dolocationid          | INTEGER |
| payment_type          | INTEGER |
| fare_amount           | FLOAT   |
| extra                 | FLOAT   |
| mta_tax               | FLOAT   |
| tip_amount            | FLOAT   |
| tolls_amount          | FLOAT   |
| improvement_surcharge | FLOAT   |
| total_amount          | FLOAT   |
| congestion_surcharge  | FLOAT   |

### `zones`
| Column       | Type    |
|--------------|---------|
| LocationID   | INTEGER |
| Borough      | TEXT    |
| Zone         | TEXT    |
| service_zone | TEXT    |

---

## Sample Queries

### Total Revenue by Pickup Zone on 2021-01-18
```sql
SELECT 
    z."Zone" AS pickup_zone,
    SUM(ytd.total_amount) AS total_revenue
FROM yellow_taxi_data ytd
JOIN zones z ON ytd.pulocationid = z."LocationID"
WHERE DATE(ytd.tpep_pickup_datetime) = '2021-01-18'
GROUP BY pickup_zone
HAVING SUM(ytd.total_amount) > 13000
ORDER BY total_revenue DESC;
```

---

## Connect Power BI (Optional)
You can connect Power BI to PostgreSQL to visualize the data:
1. Open Power BI Desktop.
2. Use **Get Data > PostgreSQL**.
3. Enter the host as `localhost`, port `5432`, and database `nyc_taxi`.
4. Provide credentials (`root` / `root`).

---


##  🧠 Insights & Learnings

    Built ingestion logic with chunked CSV uploads for memory efficiency

    Defined and normalized PostgreSQL schemas via SQL

    Mapped zones using LocationID for rich geo-context

    Practiced real-world SQL analysis to answer business-style questions

    Ready for extension to Spark or cloud data warehouses

📬 Contact

Feel free to connect:

    LinkedIn : Abdelouahab Chetara

    Email: abdelwahab.chetara@g.enp.edu.dz

## Author
**Chetara Abdelouahab**
