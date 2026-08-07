import sqlite3
from pathlib import Path

DB_FOLDER = Path(__file__).parent
DB_PATH = DB_FOLDER / "meterdata.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA temp_store=MEMORY;")
    conn.execute("PRAGMA cache_size=-50000;")

    return conn


def create_database():

    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS consumers(

            meter_no TEXT PRIMARY KEY,

            consumer_no TEXT,
            consumer_name TEXT,
            father_name TEXT,
            address TEXT,

            zone TEXT,
            division TEXT,
            subdivision TEXT,

            mobile1 TEXT,
            mobile2 TEXT,

            location TEXT,
            remark TEXT
        )
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_consumer_no
        ON consumers(consumer_no)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_consumer_name
        ON consumers(consumer_name)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_mobile1
        ON consumers(mobile1)
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
    print("Database Ready")