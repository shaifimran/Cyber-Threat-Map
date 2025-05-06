# scripts/insert_data_pg.py

import psycopg2
from db.config import POSTGRES

def insert_data_postgres(row):
    """
    Insert one log row into PostgreSQL tables: devices, malware, attacks.
    Returns True on success, False on any error.
    """
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(**POSTGRES)
        cur = conn.cursor()

        # 1) Insert or ignore device (source)
        cur.execute(
            """
            INSERT INTO cyber.devices (ip, hostname, location, os)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (ip) DO NOTHING;
            """,
            (row["source_ip"], row["hostname"], row["location"], row["os"])
        )

        # 2) Insert or ignore device (target)
        cur.execute(
            """
            INSERT INTO cyber.devices (ip, hostname, location, os)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (ip) DO NOTHING;
            """,
            (
                row["target_ip"],
                row.get("target_hostname", ""),
                row.get("target_location", ""),
                row.get("target_os", "")
            )
        )

        # 3) Insert or ignore malware
        if row.get("malware_name"):
            cur.execute(
                """
                INSERT INTO cyber.malware (name, type, signature_hash)
                VALUES (%s, %s, %s)
                ON CONFLICT (name) DO NOTHING;
                """,
                (
                    row["malware_name"],
                    row.get("malware_type", ""),
                    row.get("signature_hash", "")
                )
            )

        # 4) Insert attack record, linking to malware_id if present
        cur.execute(
            """
            INSERT INTO cyber.attacks
              (source_ip, target_ip, timestamp, attack_type, malware_id)
            VALUES (
              %s, %s, %s, %s,
              (SELECT id FROM cyber.malware WHERE name = %s)
            );
            """,
            (
                row["source_ip"],
                row["target_ip"],
                row["timestamp"],
                row["attack_type"],
                row.get("malware_name")
            )
        )

        conn.commit()
        print(f"[Postgres] Inserted attack {row['attack_type']} from {row['source_ip']} → {row['target_ip']}")
        return True

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[Postgres] Failed to insert {row['source_ip']} → {row['target_ip']}: {e}")
        return False

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
