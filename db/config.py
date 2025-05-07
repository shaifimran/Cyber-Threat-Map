# db/config.py

# PostgreSQL configuration (used for logs)
POSTGRES = {
    "host": "localhost",
    "port": 5432,
    "dbname": "cyber_logs",
    "user": "postgres",
    "password": "your_password"
}

# AgensGraph configuration (used for graph modeling)
AGENS = {
    "host": "localhost",
    "port": 5455,
    "database": "agens",
    "user": "agens",
    "password": "your_password",
}

GRAPH_PATH = "threat_graph"
