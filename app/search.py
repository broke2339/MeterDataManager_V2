from database.database import connect


def search_consumer(search_text):

    search_text = str(search_text).strip()

    if search_text == "":
        return None

    conn = connect()
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
        WHERE meter_no=?
           OR consumer_no=?
        LIMIT 1
    """, (search_text, search_text))

    row = cursor.fetchone()

    conn.close()

    return row