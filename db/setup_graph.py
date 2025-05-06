# db/setup_graph.py

import psycopg2
import agensgraph      # registers Vertex/Edge/Path types with psycopg2
from config import AGENS

GRAPH_PATH = AGENS.get("graph_path", "cyber_graph")

def setup_agens_graph():
    """
    Create an AgensGraph graph path and all required VLABELs/ELABELs.
    Uses the agensgraph-python driver extension (AGType support).
    """
    conn = None
    cur = None
    try:
        # 1) connect via psycopg2 (with agensgraph types registered)
        conn = psycopg2.connect(
            host=AGENS["host"],
            port=AGENS["port"],
            dbname=AGENS["database"],
            user=AGENS["user"],
            password=AGENS["password"],
        )
        cur = conn.cursor()

        # 2) create or reuse graph
        cur.execute(f"CREATE GRAPH IF NOT EXISTS {GRAPH_PATH};")
        # 3) set graph_path to direct subsequent Cypher to this graph
        cur.execute(f"SET graph_path = {GRAPH_PATH};")

        # 4) create vertex labels for our domain entities
        cur.execute("CREATE VLABEL IF NOT EXISTS Device;")
        cur.execute("CREATE VLABEL IF NOT EXISTS Malware;")
        cur.execute("CREATE VLABEL IF NOT EXISTS Attack;")

        # 5) create edge labels for the relationships
        cur.execute("CREATE ELABEL IF NOT EXISTS INITIATED;")
        cur.execute("CREATE ELABEL IF NOT EXISTS TARGETED;")
        cur.execute("CREATE ELABEL IF NOT EXISTS USED;")
        cur.execute("CREATE ELABEL IF NOT EXISTS INFECTED;")

        conn.commit()
        print(f"AgensGraph graph “{GRAPH_PATH}” and labels created.")

    except Exception as e:
        print(f"failed to set up AgensGraph: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    setup_agens_graph()
