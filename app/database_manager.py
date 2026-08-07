from database.database import connect


def load_existing_meters():
    """
    Database ke saare Meter No memory me load karta hai.
    """
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT meter_no FROM consumers")

    meters = {row[0] for row in cursor.fetchall()}

    conn.close()

    return meters


def insert_many(records):

    if not records:
        return

    conn = connect()
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
    """, records)

    conn.commit()
    conn.close()


def update_many(records):

    if not records:
        return

    conn = connect()
    cursor = conn.cursor()

    cursor.executemany("""
        UPDATE consumers
        SET
            consumer_no=?,
            consumer_name=?,
            father_name=?,
            address=?,
            zone=?,
            division=?,
            subdivision=?,
            mobile1=?,
            mobile2=?,
            location=?,
            remark=?
        WHERE meter_no=?
    """, records)

    conn.commit()
    conn.close()