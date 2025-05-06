# scripts/insert_data_graph.py

import psycopg2
import agensgraph                        # registers AGType support
from db.config import AGENS

def insert_data_graph(row):
    """
    Insert one log row into AgensGraph:
    - MERGE Device nodes (source & target)
    - MERGE Malware node (if any)
    - CREATE one Attack node
    - CREATE INITIATED, TARGETED, USED edges
    """
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(**AGENS)
        cur = conn.cursor()

        # ensure correct graph
        cur.execute(f"SET graph_path = {AGENS['graph_path']};")

        # 1) MERGE source Device
        cur.execute(
            """
            MERGE (d:Device {ip: $ip})
            ON CREATE SET
              d.hostname   = $hostname,
              d.location   = $location,
              d.os         = $os;
            """,
            {
                "ip": row["source_ip"],
                "hostname": row["hostname"],
                "location": row["location"],
                "os": row["os"]
            }
        )

        # 2) MERGE target Device
        cur.execute(
            """
            MERGE (t:Device {ip: $ip})
            ON CREATE SET
              t.hostname   = $hostname,
              t.location   = $location,
              t.os         = $os;
            """,
            {
                "ip": row["target_ip"],
                "hostname": row.get("target_hostname", ""),
                "location": row.get("target_location", ""),
                "os": row.get("target_os", "")
            }
        )

        # 3) MERGE Malware (if provided)
        if row.get("malware_name"):
            cur.execute(
                """
                MERGE (m:Malware {name: $name})
                ON CREATE SET
                  m.type           = $type,
                  m.signature_hash = $sig;
                """,
                {
                    "name": row["malware_name"],
                    "type": row.get("malware_type", ""),
                    "sig":  row.get("signature_hash", "")
                }
            )

        # 4) CREATE Attack node
        cur.execute(
            """
            CREATE (a:Attack {
              attack_type: $atype,
              timestamp:   $ts
            });
            """,
            {
                "atype": row["attack_type"],
                "ts":     row["timestamp"]
            }
        )

        # 5) Link source Device → Attack
        cur.execute(
            """
            MATCH (d:Device {ip: $src}), (a:Attack {timestamp: $ts, attack_type: $atype})
            CREATE (d)-[:INITIATED]->(a);
            """,
            {
                "src":   row["source_ip"],
                "ts":    row["timestamp"],
                "atype": row["attack_type"]
            }
        )

        # 6) Link target Device → Attack
        cur.execute(
            """
            MATCH (t:Device {ip: $tgt}), (a:Attack {timestamp: $ts, attack_type: $atype})
            CREATE (t)-[:TARGETED]->(a);
            """,
            {
                "tgt":   row["target_ip"],
                "ts":    row["timestamp"],
                "atype": row["attack_type"]
            }
        )

        # 7) Link Attack → Malware (if provided)
        if row.get("malware_name"):
            cur.execute(
                """
                MATCH (a:Attack {timestamp: $ts, attack_type: $atype}),
                      (m:Malware {name: $name})
                CREATE (a)-[:USED]->(m);
                """,
                {
                    "ts":    row["timestamp"],
                    "atype": row["attack_type"],
                    "name":  row["malware_name"]
                }
            )

        conn.commit()
        print(f"[AgensGraph] Created graph entities for attack {row['attack_type']}")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[AgensGraph] Failed to insert graph data for {row['attack_type']}: {e}")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
