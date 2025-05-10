# Cyber Threat Map

A hybrid application that ingests raw cyber-attack logs into **PostgreSQL** and models their relationships in **AgensGraph** for graph-based analysis and visualization.

## Features

- **Structured storage** of logs (IPs, timestamps, attack types, malware) in PostgreSQL  
- **Graph modeling** of Devices, Attacks, Malware in AgensGraph  
- Automated **Python scripts** for schema & graph setup, data ingestion, and relationship building  
- **AgensGraph Viewer** screenshot included for quick inspection  

## Prerequisites

1. **Python 3.8+**  
2. **PostgreSQL 12+**  
3. **AgensGraph** (v2.x)  
   - Native install: follow the [AgensGraph docs](https://github.com/skaiworldwide-oss/agensgraph)  
   - **Or via Docker**:
     ```bash
     docker run --name agensgraph -p 5455:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=agens -e POSTGRES_DB=agens -d skaiworldwide/agensgraph
     ```

## Step 1 — Clone & Install

```bash
git clone https://github.com/shaifimran/cyber-threat-map.git
cd cyber-threat-map
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2 — Configure Databases

### 2.1 PostgreSQL Setup

Start your PostgreSQL server.

Create a database for logs:

```sql
CREATE DATABASE cyber_logs;
```

Edit `db/config.py` → `POSTGRES` dictionary:

```python
POSTGRES = {
  "host":     "localhost",
  "port":     5432,
  "dbname":   "cyber_logs",
  "user":     "your_pg_user",
  "password": "your_pg_password"
}
```

### 2.2 AgensGraph Setup

Start AgensGraph (native or Docker).

Edit `db/config.py` → `AGENS` and `GRAPH_PATH`:

```python
AGENS_CONN = {
  "host":     "localhost",
  "port":     5455,
  "dbname":   "agens",
  "user":     "postgres",
  "password": "agens"
}
GRAPH_PATH = "threat_graph"
```

## Step 3 — Initialize Schemas & Graph

```bash
# 1) PostgreSQL schema & tables
python db/setup_postgres.py

# 2) AgensGraph path, VLABELs & ELABELs
python db/setup_graph.py
```

## Step 4 — Ingest Logs & Build Graph

Place your CSV logs in `data/sample_logs.csv`, then:

```bash
python logs/log_processor.py
```

This will, for each row:

- Insert devices, malware, attacks into PostgreSQL
- On success, insert corresponding nodes & relationships into AgensGraph

## Step 5 — Visualize in AgensGraph Viewer

Open AgensGraph Viewer.

Select the `threat_graph` graph path.

Run a sample query:

```cypher
MATCH (v)-[r:used]->(m:Malware)
RETURN *
```

Inspect the graph:

![AgensGraph Viewer](![alt text](image.png))

## Project Structure

```text
cyber-threat-map/
├── db/
│   ├── config.py           # Edit POSTGRES & AGENS/GRAPH_PATH here
│   ├── setup_postgres.py   # Creates PostgreSQL schema & tables
│   └── setup_graph.py      # Creates graph path & labels in AgensGraph
├── data/
│   └── sample_logs.csv     # CSV of sample logs to ingest
├── docs/
│   └── agviewer.png        # Screenshot of AgensGraph Viewer
├── logs/
│   └── log_processor.py    # Reads CSV, inserts into PG then AgensGraph
├── scripts/
│   ├── insert_data_pg.py   # Inserts devices, malware, attacks into PG
│   └── insert_data_graph.py# Inserts nodes & edges into AgensGraph
├── requirements.txt        # psycopg2-binary, agensgraph, python-dotenv, etc.
└── README.md
```
