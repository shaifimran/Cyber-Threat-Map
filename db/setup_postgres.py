import psycopg2
from config import POSTGRES

def create_schema_and_tables():
    """Create 'cyber' schema and necessary tables in PostgreSQL."""
    try:
        conn = psycopg2.connect(**POSTGRES)
        cur = conn.cursor()

        # Create schema and tables
        cur.execute("CREATE SCHEMA IF NOT EXISTS cyber;")

        # Device table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cyber.devices (
                ip TEXT PRIMARY KEY,
                hostname TEXT,
                location TEXT,
                os TEXT
            );
        """)

        # Malware table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cyber.malware (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                signature_hash TEXT
            );
        """)

        # Attacks table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cyber.attacks (
                id SERIAL PRIMARY KEY,
                source_ip TEXT NOT NULL,
                target_ip TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                attack_type TEXT NOT NULL,
                malware_id INT,
                FOREIGN KEY (source_ip) REFERENCES cyber.devices(ip),
                FOREIGN KEY (target_ip) REFERENCES cyber.devices(ip),
                FOREIGN KEY (malware_id) REFERENCES cyber.malware(id)
            );
        """)

        conn.commit()
        print("PostgreSQL schema and tables created.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_schema_and_tables()
