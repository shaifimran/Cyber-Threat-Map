import csv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.setup_postgres import create_schema_and_tables
from db.setup_graph import setup_graph_schema
from scripts.insert_data_pg import insert_data_postgres
from scripts.insert_data_graph import insert_data_graph

def process_logs(log_file):
    """Process log file, inserting into PostgreSQL first, then AgensGraph."""
    # Set up DBs (only run once)
    create_schema_and_tables()
    setup_graph_schema()

    # Open CSV file and process each log
    with open(log_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Insert into PostgreSQL first
            success_pg = insert_data_postgres(row)

            # Only insert into AgensGraph if PostgreSQL insertion is successful
            if success_pg:
                insert_data_graph(row)

if __name__ == "__main__":
    process_logs("data/sample_logs.csv")
