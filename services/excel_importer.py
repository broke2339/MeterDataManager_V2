from openpyxl import load_workbook
from database.repository import upsert_many

BATCH_SIZE = 1000


def import_excel(file_path, progress_callback=None):

    # Workbook Open
    wb = load_workbook(
        filename=file_path,
        read_only=True,
        data_only=True
    )

    ws = wb.active

    # Total Rows
    total_rows = ws.max_row - 1

    # Read Rows
    rows = ws.iter_rows(values_only=True)

    headers = next(rows)

    headers = [
        str(h).strip() if h else ""
        for h in headers
    ]

    column = {
        name: index
        for index, name in enumerate(headers)
    }

    batch = []

    processed = 0

    for row in rows:

        meter_no = str(
            row[column["Meter no."]]
        ).strip()

        if meter_no in ("", "None"):
            continue

        batch.append((
            meter_no,
            row[column["Consumer Number"]],
            row[column["Consumer Name"]],
            row[column["Father name"]],
            row[column["Address"]],
            row[column["Zone"]],
            row[column["Division"]],
            row[column["Subdivision"]],
            row[column["Mobile Number 1"]],
            row[column["Mobile number 2"]],
            row[column["Location"]],
            row[column["Whats app remark"]],
        ))

        processed += 1

        if len(batch) >= BATCH_SIZE:

            upsert_many(batch)

            batch.clear()

            if progress_callback:
                progress_callback(
                    processed,
                    total_rows
                )

    if batch:
        upsert_many(batch)

    wb.close()

    if progress_callback:
        progress_callback(
            total_rows,
            total_rows
        )

    return processed