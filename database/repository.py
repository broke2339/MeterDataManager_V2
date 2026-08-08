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
# Search Multiple Consumers with Pagination
# =====================================================

def search_consumers_paginated(search_value, page, page_size):

    offset = (page - 1) * page_size

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

        LIMIT ?
        OFFSET ?

    """, (
        f"%{search_value}%",
        f"%{search_value}%",
        f"%{search_value}%",
        page_size,
        offset
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows


# =====================================================
# Advanced Search with Filters, Pagination, and Sorting
# =====================================================

def search_consumers_advanced(
    search_text,
    division=None,
    zone=None,
    subdivision=None,
    page=1,
    page_size=100,
    sort_column="consumer_name",
    sort_order="ASC"
):

    allowed_sort_columns = (
        "meter_no",
        "consumer_no",
        "consumer_name",
        "division",
        "zone",
        "subdivision"
    )

    if sort_column not in allowed_sort_columns:
        sort_column = "consumer_name"

    sort_order = sort_order.upper()
    if sort_order not in ("ASC", "DESC"):
        sort_order = "ASC"

    offset = (page - 1) * page_size
    search_text = search_text or ""
    term = f"%{search_text}%"

    query = """
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
        WHERE (
            meter_no LIKE ?
            OR consumer_no LIKE ?
            OR consumer_name LIKE ?
            OR father_name LIKE ?
            OR mobile1 LIKE ?
            OR mobile2 LIKE ?
            OR address LIKE ?
            OR division LIKE ?
            OR zone LIKE ?
            OR subdivision LIKE ?
        )
    """

    params = [
        term,
        term,
        term,
        term,
        term,
        term,
        term,
        term,
        term,
        term,
    ]

    if division is not None:
        query += "\n        AND division = ?"
        params.append(division)

    if zone is not None:
        query += "\n        AND zone = ?"
        params.append(zone)

    if subdivision is not None:
        query += "\n        AND subdivision = ?"
        params.append(subdivision)

    query += f"\n        ORDER BY {sort_column} {sort_order}\n        LIMIT ?\n        OFFSET ?\n"
    params.extend([page_size, offset])

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(query, params)
    rows = cursor.fetchall()

    conn.close()

    return rows


# =====================================================
# Count Advanced Search Results
# =====================================================

def count_advanced_results(
    search_text,
    division=None,
    zone=None,
    subdivision=None
):

    search_text = search_text or ""
    term = f"%{search_text}%"

    query = """
        SELECT COUNT(*)
        FROM consumers
        WHERE (
            meter_no LIKE ?
            OR consumer_no LIKE ?
            OR consumer_name LIKE ?
            OR father_name LIKE ?
            OR mobile1 LIKE ?
            OR mobile2 LIKE ?
            OR address LIKE ?
            OR division LIKE ?
            OR zone LIKE ?
            OR subdivision LIKE ?
        )
    """

    params = [
        term,
        term,
        term,
        term,
        term,
        term,
        term,
        term,
        term,
        term,
    ]

    if division is not None:
        query += "\n        AND division = ?"
        params.append(division)

    if zone is not None:
        query += "\n        AND zone = ?"
        params.append(zone)

    if subdivision is not None:
        query += "\n        AND subdivision = ?"
        params.append(subdivision)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(query, params)
    total = cursor.fetchone()[0]

    conn.close()

    return total


# =====================================================
# Count Search Results
# =====================================================

def count_search_results(search_value):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM consumers
        WHERE meter_no LIKE ?
           OR consumer_no LIKE ?
           OR consumer_name LIKE ?
    """, (
        f"%{search_value}%",
        f"%{search_value}%",
        f"%{search_value}%"
    ))

    total = cursor.fetchone()[0]

    conn.close()

    return total

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