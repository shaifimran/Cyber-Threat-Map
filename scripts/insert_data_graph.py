# scripts/insert_data_graph.py

import psycopg2
import agensgraph                  # registers Vertex/Edge/Path support
from db.config import AGENS, GRAPH_PATH

def insert_data_graph(row):
    """
    Insert one log row into AgensGraph:
      1) connect(**AGENS_CONN)
      2) SET graph_path = GRAPH_PATH
      3) MERGE / CREATE nodes & relationships
    """
    conn = None
    cur = None
    try:
        # 1) open connection
        conn = psycopg2.connect(**AGENS)
        cur = conn.cursor()

        # 2) switch to the proper graph
        cur.execute(f"SET graph_path = {GRAPH_PATH};")

        # 3) MERGE source Device
        cur.execute(
            """
            MERGE (d:Device {ip: %s})
            ON CREATE SET
              d.hostname = %s,
              d.location = %s,
              d.os       = %s;
            """,
            (
                row["source_ip"],
                row["hostname"],
                row["location"],
                row["os"]
            )
        )

        # 4) MERGE target Device
        cur.execute(
            """
            MERGE (t:Device {ip: %s})
            ON CREATE SET
              t.hostname = %s,
              t.location = %s,
              t.os       = %s;
            """,
            (
                row["target_ip"],
                row.get("target_hostname", ""),
                row.get("target_location", ""),
                row.get("target_os", "")
            )
        )

        # 5) MERGE Malware (if any)
        if row.get("malware_name"):
            cur.execute(
                """
                MERGE (m:Malware {name: %s})
                ON CREATE SET
                  m.type           = %s,
                  m.signature_hash = %s;
                """,
                (
                    row["malware_name"],
                    row.get("malware_type", ""),
                    row.get("signature_hash", "")
                )
            )

        # 6) CREATE Attack node
        cur.execute(
            """
            CREATE (a:Attack {
                attack_type: %s,
                timestamp:   %s
            });
            """,
            (
                row["attack_type"],
                row["timestamp"]
            )
        )

        # 7) INITIATED edge
        cur.execute(
            """
            MATCH (d:Device {ip: %s}), (a:Attack {attack_type: %s, timestamp: %s})
            CREATE (d)-[:INITIATED]->(a);
            """,
            (
                row["source_ip"],
                row["attack_type"],
                row["timestamp"]
            )
        )

        # 8) TARGETED edge
        cur.execute(
            """
            MATCH (t:Device {ip: %s}), (a:Attack {attack_type: %s, timestamp: %s})
            CREATE (t)-[:TARGETED]->(a);
            """,
            (
                row["target_ip"],
                row["attack_type"],
                row["timestamp"]
            )
        )

        # 9) USED edge (if malware)
        if row.get("malware_name"):
            cur.execute(
                """
                MATCH (a:Attack {attack_type: %s, timestamp: %s}),
                      (m:Malware {name: %s})
                CREATE (a)-[:USED]->(m);
                """,
                (
                    row["attack_type"],
                    row["timestamp"],
                    row["malware_name"]
                )
            )

        conn.commit()
        print(f"[AgensGraph] Graph data inserted for {row['attack_type']}")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[AgensGraph] Insert failed for {row['attack_type']}: {e}")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
