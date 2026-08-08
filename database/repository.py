from database.database import get_connection
import os


# =====================================================
# UPSERT (Insert + Update)
# =====================================================

def upsert_many(records):

    if not records:
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.executemany("""
        INSERT INTO consumers(
            meter_no,
            consumer_no,
            consumer_name,
            father_name,
            address,
            zone,
            division,
            subdivision,
            mobile1,
            mobile2,
            location,
            remark
        )

        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)

        ON CONFLICT(meter_no)
        DO UPDATE SET

            consumer_no = excluded.consumer_no,
            consumer_name = excluded.consumer_name,
            father_name = excluded.father_name,
            address = excluded.address,
            zone = excluded.zone,
            division = excluded.division,
            subdivision = excluded.subdivision,
            mobile1 = excluded.mobile1,
            mobile2 = excluded.mobile2,
            location = excluded.location,
            remark = excluded.remark

    """, records)

    conn.commit()
    conn.close()


# =====================================================
# Search Single Consumer
# =====================================================

def search_consumer(search_value):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            meter_no,
            consumer_no,
            consumer_name,
            father_name,
            address,
            zone,
            division,
            subdivision,
            mobile1,
            mobile2,
            location,
            remark

        FROM consumers

        WHERE meter_no = ?
           OR consumer_no = ?

        LIMIT 1

    """, (search_value, search_value))

    row = cursor.fetchone()

    conn.close()

    return row


# =====================================================
# Total Records
# =====================================================

def get_total_records():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM consumers")

    total = cursor.fetchone()[0]

    conn.close()

    return total


# =====================================================
# Database Size
# =====================================================

def get_database_size():

    path = "database/meterdata.db"

    if not os.path.exists(path):
        return "0 MB"

    size = os.path.getsize(path)

    mb = size / (1024 * 1024)

    return f"{mb:.2f} MB"


# =====================================================
# Search Multiple Consumers
# =====================================================

def search_consumers(search_value):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            meter_no,
            consumer_no,
            consumer_name,
            mobile1,
            division

        FROM consumers

        WHERE meter_no LIKE ?
           OR consumer_no LIKE ?
           OR consumer_name LIKE ?

        ORDER BY consumer_name

        LIMIT 100

    """, (
        f"%{search_value}%",
        f"%{search_value}%",
        f"%{search_value}%"
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows