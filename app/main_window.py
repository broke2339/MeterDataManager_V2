import time
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox
from openpyxl import Workbook
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table as PDFTable, TableStyle
import platform

from services.excel_importer import import_excel

from database.database import get_connection
from database.repository import (
    search_consumer,
    count_search_results,
    get_total_records,
    get_database_size
)

from app.details_window import show_consumer
from app.toolbar import Toolbar
from app.progress import ProgressFrame
from app.consumer_table import ConsumerTable


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# -----------------------------------
# Application Constants
# -----------------------------------

APP_NAME = "Meter Data Manager Pro"
APP_VERSION = "v2.0 Stable"


def show_about_dialog():
    about_dialog = ctk.CTkToplevel()
    about_dialog.title("About")
    about_dialog.resizable(False, False)
    about_dialog.grab_set()

    content = ctk.CTkFrame(about_dialog, padx=20, pady=20)
    content.pack(fill="both", expand=True)

    title_label = ctk.CTkLabel(
        content,
        text=APP_NAME,
        font=ctk.CTkFont(size=16, weight="bold"),
        anchor="w"
    )
    title_label.pack(fill="x", pady=(0, 10))

    info_items = [
        f"Version: {APP_VERSION}",
        "Developer:",
        "Sachin Sharma",
        "Database:",
        "SQLite",
        "Framework:",
        "CustomTkinter",
        "Python Version:",
        platform.python_version()
    ]

    for item in info_items:
        label = ctk.CTkLabel(content, text=item, anchor="w")
        label.pack(fill="x", pady=(0, 5))

    close_button = ctk.CTkButton(
        content,
        text="Close",
        command=about_dialog.destroy
    )
    close_button.pack(pady=(10, 0))


def start_app():

    app = ctk.CTk()

    app.title(APP_NAME)

    app.geometry("1250x750")

    app.minsize(1100,700)

    # -----------------------------------
    # Variables
    # -----------------------------------

    selected_row = None

    start_time = 0

    search_after_id = None

    current_page = 1
    page_size = 100
    search_total_results = 0

    sort_column = "Consumer Name"
    sort_direction = "ASC"

    column_sort_mapping = {
        "Meter No": "meter_no",
        "Consumer No": "consumer_no",
        "Consumer Name": "consumer_name",
        "Mobile": "mobile1",
        "Division": "division"
    }

    def get_search_rows(search_value, page, page_size, sort_column, sort_direction):
        db_column = column_sort_mapping.get(sort_column, "consumer_name")
        if sort_direction not in ("ASC", "DESC"):
            sort_direction = "ASC"

        offset = (page - 1) * page_size
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            f"""
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
            ORDER BY {db_column} {sort_direction}
            LIMIT ?
            OFFSET ?
            """,
            (
                f"%{search_value}%",
                f"%{search_value}%",
                f"%{search_value}%",
                page_size,
                offset
            )
        )

        rows = cursor.fetchall()
        conn.close()

        return rows

    def update_sort_indicators():
        for col in table.table["columns"]:
            if col == sort_column:
                arrow = " 🔼" if sort_direction == "ASC" else " 🔽"
                table.table.heading(col, text=col + arrow)
            else:
                table.table.heading(col, text=col)

    def sort_by_column(column):
        nonlocal sort_column, sort_direction

        if sort_column == column:
            sort_direction = "DESC" if sort_direction == "ASC" else "ASC"
        else:
            sort_column = column
            sort_direction = "ASC"

        update_sort_indicators()
        do_search(1)

    # -----------------------------------
    # Search Function
    # -----------------------------------

    def update_pagination_controls(start, end, total):

        if total == 0:
            pagination_label.configure(text="Showing 0-0 of 0 Records")
            prev_btn.configure(state="disabled")
            next_btn.configure(state="disabled")
            return

        last_page = (total + page_size - 1) // page_size

        pagination_label.configure(
            text=f"Showing {start}-{end} of {total:,} Records"
        )

        prev_btn.configure(
            state="disabled" if current_page <= 1 else "normal"
        )

        next_btn.configure(
            state="disabled" if current_page >= last_page else "normal"
        )

    def load_search_results(page=1):

        nonlocal current_page, search_total_results

        value = toolbar.search_box.get().strip()

        if value == "":
            current_page = 1
            search_total_results = 0
            table.load([])
            update_pagination_controls(0, 0, 0)
            return

        search_total_results = count_search_results(value)
        last_page = (search_total_results + page_size - 1) // page_size if search_total_results else 1

        if page < 1:
            page = 1
        elif page > last_page:
            page = last_page

        current_page = page

        rows = get_search_rows(value, page, page_size, sort_column, sort_direction)

        table.load(rows)

        if rows:
            start = (page - 1) * page_size + 1
            end = start + len(rows) - 1
        else:
            start = 0
            end = 0

        update_pagination_controls(start, end, search_total_results)

    def do_search(page=1):

        load_search_results(page)

    # -----------------------------------
    # Open Consumer
    # -----------------------------------

    def open_from_table(values):

        meter = values[0]

        row = search_consumer(meter)

        if row:

            show_consumer(row)

    # -----------------------------------
    # Advanced Filters
    # -----------------------------------

    def load_filter_values():
        """Load distinct values from database for filter dropdowns"""
        conn = get_connection()
        cursor = conn.cursor()
        
        filters = {
            "division": ["All"],
            "zone": ["All"],
            "subdivision": ["All"]
        }
        
        try:
            cursor.execute("SELECT DISTINCT division FROM consumers WHERE division IS NOT NULL AND division != '' ORDER BY division")
            filters["division"].extend([row[0] for row in cursor.fetchall()])
            
            cursor.execute("SELECT DISTINCT zone FROM consumers WHERE zone IS NOT NULL AND zone != '' ORDER BY zone")
            filters["zone"].extend([row[0] for row in cursor.fetchall()])
            
            cursor.execute("SELECT DISTINCT subdivision FROM consumers WHERE subdivision IS NOT NULL AND subdivision != '' ORDER BY subdivision")
            filters["subdivision"].extend([row[0] for row in cursor.fetchall()])
        finally:
            conn.close()
        
        return filters

    def refresh_filters():
        """Refresh filter dropdowns with latest database values"""
        filter_values = load_filter_values()
        division_combo.configure(values=filter_values["division"])
        zone_combo.configure(values=filter_values["zone"])
        subdivision_combo.configure(values=filter_values["subdivision"])
        
        division_combo.set("All")
        zone_combo.set("All")
        subdivision_combo.set("All")

    def search_consumers_advanced(search_value, division, zone, subdivision, page, page_size, sort_column, sort_direction):
        """Search consumers with advanced filters"""
        db_column = column_sort_mapping.get(sort_column, "consumer_name")
        if sort_direction not in ("ASC", "DESC"):
            sort_direction = "ASC"
        
        offset = (page - 1) * page_size
        conn = get_connection()
        cursor = conn.cursor()
        
        where_clauses = []
        params = []
        
        # Text search
        if search_value:
            where_clauses.append("(meter_no LIKE ? OR consumer_no LIKE ? OR consumer_name LIKE ?)")
            params.extend([f"%{search_value}%", f"%{search_value}%", f"%{search_value}%"])
        
        # Division filter
        if division and division != "All":
            where_clauses.append("division = ?")
            params.append(division)
        
        # Zone filter
        if zone and zone != "All":
            where_clauses.append("zone = ?")
            params.append(zone)
        
        # Subdivision filter
        if subdivision and subdivision != "All":
            where_clauses.append("subdivision = ?")
            params.append(subdivision)
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        cursor.execute(
            f"""
            SELECT
                meter_no,
                consumer_no,
                consumer_name,
                mobile1,
                division
            FROM consumers
            WHERE {where_clause}
            ORDER BY {db_column} {sort_direction}
            LIMIT ?
            OFFSET ?
            """,
            params + [page_size, offset]
        )
        
        rows = cursor.fetchall()
        conn.close()
        return rows

    def count_search_results_advanced(search_value, division, zone, subdivision):
        """Count total results with advanced filters"""
        conn = get_connection()
        cursor = conn.cursor()
        
        where_clauses = []
        params = []
        
        # Text search
        if search_value:
            where_clauses.append("(meter_no LIKE ? OR consumer_no LIKE ? OR consumer_name LIKE ?)")
            params.extend([f"%{search_value}%", f"%{search_value}%", f"%{search_value}%"])
        
        # Division filter
        if division and division != "All":
            where_clauses.append("division = ?")
            params.append(division)
        
        # Zone filter
        if zone and zone != "All":
            where_clauses.append("zone = ?")
            params.append(zone)
        
        # Subdivision filter
        if subdivision and subdivision != "All":
            where_clauses.append("subdivision = ?")
            params.append(subdivision)
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        cursor.execute(
            f"SELECT COUNT(*) FROM consumers WHERE {where_clause}",
            params
        )
        
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def on_filter_changed(event=None):
        """Handle filter dropdown changes"""
        nonlocal current_page
        current_page = 1
        load_search_results(1)

    def schedule_live_search(event=None):

        nonlocal search_after_id

        if search_after_id:

            app.after_cancel(search_after_id)

        search_after_id = app.after(300, perform_live_search)

    def perform_live_search():

        nonlocal search_after_id

        search_after_id = None

        do_search(1)

    def open_selected_consumer(event=None):

        meter_no = table.get_selected_meter()

        if not meter_no:

            return

        show_details(meter_no)

    def get_displayed_rows():

        rows = []

        for item in table.table.get_children():

            values = table.table.item(item).get("values", [])

            if values:

                rows.append(values)

        return rows

    def export_to_pdf():

        rows = get_displayed_rows()

        if not rows:
            messagebox.showinfo("Export PDF", "No data to export.")
            return

        file = filedialog.asksaveasfilename(
            title="Save PDF File",
            defaultextension=".pdf",
            filetypes=[("PDF Files","*.pdf")]
        )

        if not file:
            return

        headers = list(table.table["columns"])
        export_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        document = SimpleDocTemplate(
            file,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        title = Paragraph("Meter Data Manager Pro", styles["Title"])
        subtitle = Paragraph(f"Export Date & Time: {export_date}", styles["Normal"])

        data = [headers] + rows
        pdf_table = PDFTable(data, repeatRows=1)
        pdf_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9d9d9")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
        ]))

        elements = [title, Spacer(1, 12), subtitle, Spacer(1, 18), pdf_table]
        document.build(elements)

        messagebox.showinfo(
            "Export Complete",
            f"Exported {len(rows):,} rows to {file}"
        )

    def export_to_excel():

        rows = get_displayed_rows()

        if not rows:

            messagebox.showinfo("Export Excel", "No data to export.")

            return

        file = filedialog.asksaveasfilename(

            title="Save Excel File",

            defaultextension=".xlsx",

            filetypes=[("Excel Files","*.xlsx")]

        )

        if not file:

            return

        workbook = Workbook()

        sheet = workbook.active

        headers = list(table.table["columns"])

        sheet.append(headers)

        for row in rows:

            sheet.append(row)

        workbook.save(file)

        messagebox.showinfo(

            "Export Complete",

            f"Exported {len(rows):,} rows to {file}"

        )
                # -----------------------------------
    # Import Function
    # -----------------------------------

    def do_import():

        nonlocal start_time

        file = filedialog.askopenfilename(

            title="Select Excel File",

            filetypes=[("Excel Files","*.xlsx *.xls")]

        )

        if not file:
            return

        start_time = time.time()

        progress.reset()

        toolbar.import_btn.configure(state="disabled")

        app.update()

        def callback(current,total):

            progress.update(current,total)

            app.update()

        import_excel(
            file,
            progress_callback=callback
        )

        seconds = time.time() - start_time

        progress.complete()

        records_lbl.configure(
            text=f"{get_total_records():,}"
        )

        size_lbl.configure(
            text=get_database_size()
        )

        status_lbl.configure(
            text="Ready"
        )

        time_lbl.configure(
            text=f"{seconds:.2f} sec"
        )

        toolbar.import_btn.configure(
            state="normal"
        )

        status.configure(

            text=f"Import Completed | {seconds:.2f} sec | Records : {get_total_records():,}"

        )

    # -----------------------------------
    # Backup Database
    # -----------------------------------

    def backup_database():

        db_path = "database/meterdata.db"

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

        default_filename = f"meterdata_{timestamp}.db"

        file = filedialog.asksaveasfilename(
            title="Backup Database",
            defaultextension=".db",
            initialfile=default_filename,
            filetypes=[("Database Files","*.db")]
        )

        if not file:
            return

        try:
            shutil.copy2(db_path, file)
            messagebox.showinfo(
                "Backup Complete",
                f"Database backed up successfully to:\n{file}"
            )
            status.configure(text="Database backup completed")
        except Exception as e:
            messagebox.showerror(
                "Backup Error",
                f"Failed to backup database:\n{str(e)}"
            )
            status.configure(text="Backup failed")

    # -----------------------------------
    # Restore Database
    # -----------------------------------

    def restore_database():

        db_path = "database/meterdata.db"

        file = filedialog.askopenfilename(
            title="Select Database File to Restore",
            filetypes=[("Database Files","*.db")]
        )

        if not file:
            return

        confirm = messagebox.askyesno(
            "Confirm Restore",
            "This will replace your current database. Continue?"
        )

        if not confirm:
            return

        try:
            shutil.copy2(file, db_path)
            messagebox.showinfo(
                "Restore Complete",
                "Database restored successfully.\nPlease restart the application for changes to take effect."
            )
            status.configure(text="Database restored. Please restart application.")
        except Exception as e:
            messagebox.showerror(
                "Restore Error",
                f"Failed to restore database:\n{str(e)}"
            )
            status.configure(text="Restore failed")

    # -----------------------------------
    # UI
    # -----------------------------------

    toolbar = Toolbar(

        app,

        import_callback=do_import,

        search_callback=do_search

    )

    toolbar.search_box.bind("<KeyRelease>", schedule_live_search)

    toolbar.export_btn = ctk.CTkButton(

        toolbar,

        text="📤 Export Excel",

        width=140,

        command=export_to_excel

    )

    toolbar.export_btn.pack(

        side="left",

        padx=10

    )

    toolbar.export_pdf_btn = ctk.CTkButton(

        toolbar,

        text="📤 Export PDF",

        width=140,

        command=export_to_pdf

    )

    toolbar.export_pdf_btn.pack(

        side="left",

        padx=10

    )

    toolbar.backup_btn = ctk.CTkButton(

        toolbar,

        text="💾 Backup DB",

        width=140,

        command=backup_database

    )

    toolbar.backup_btn.pack(

        side="left",

        padx=10

    )

    toolbar.restore_btn = ctk.CTkButton(

        toolbar,

        text="♻️ Restore DB",

        width=140,

        command=restore_database

    )

    toolbar.restore_btn.pack(

        side="left",

        padx=10

    )

    toolbar.about_btn = ctk.CTkButton(

        toolbar,

        text="ℹ️ About",

        width=140,

        command=show_about_dialog

    )

    toolbar.about_btn.pack(

        side="left",

        padx=10

    )

    progress = ProgressFrame(app)

    table = ConsumerTable(

        app,

        open_callback=open_from_table

    )

    for col in table.table["columns"]:
        table.table.heading(col, command=lambda c=col: sort_by_column(c))

    update_sort_indicators()

    table.pack(

        fill="both",

        expand=True,

        padx=20,

        pady=10

    )

    table.bind("<Double-1>", open_selected_consumer)

    pagination_frame = ctk.CTkFrame(app)
    pagination_frame.pack(
        fill="x",
        padx=20,
        pady=(0,10)
    )

    prev_btn = ctk.CTkButton(
        pagination_frame,
        text="Previous",
        width=100,
        command=lambda: do_search(current_page - 1)
    )
    prev_btn.pack(side="left")

    pagination_label = ctk.CTkLabel(
        pagination_frame,
        text="Showing 0-0 of 0 Records",
        anchor="center"
    )
    pagination_label.pack(
        side="left",
        expand=True,
        padx=10
    )

    next_btn = ctk.CTkButton(
        pagination_frame,
        text="Next",
        width=100,
        command=lambda: do_search(current_page + 1)
    )
    next_btn.pack(side="right")
        # -----------------------------------
    # Dashboard
    # -----------------------------------

    dashboard = ctk.CTkFrame(app)

    dashboard.pack(

        fill="x",

        padx=20,

        pady=(0,10)

    )

    ctk.CTkLabel(

        dashboard,

        text="📊 Dashboard",

        font=("Arial",18,"bold")

    ).pack(

        anchor="w",

        padx=15,

        pady=(10,5)

    )

    cards = ctk.CTkFrame(

        dashboard,

        fg_color="transparent"

    )

    cards.pack(

        fill="x",

        padx=10,

        pady=(0,10)

    )

    def create_card(title,value):

        card = ctk.CTkFrame(

            cards,

            width=250,

            height=90,

            corner_radius=10

        )

        ctk.CTkLabel(

            card,

            text=title,

            font=("Arial",13)

        ).pack(

            pady=(12,2)

        )

        lbl = ctk.CTkLabel(

            card,

            text=value,

            font=("Arial",22,"bold")

        )

        lbl.pack(

            pady=(0,12)

        )

        return card,lbl

    card1,records_lbl = create_card(

        "📊 Records",

        f"{get_total_records():,}"

    )

    card2,size_lbl = create_card(

        "💾 Database",

        get_database_size()

    )

    card3,status_lbl = create_card(

        "✅ Status",

        "Ready"

    )

    card4,time_lbl = create_card(

        "⏱ Last Import",

        "--"

    )

    card1.grid(row=0,column=0,padx=10,pady=10,sticky="ew")

    card2.grid(row=0,column=1,padx=10,pady=10,sticky="ew")

    card3.grid(row=0,column=2,padx=10,pady=10,sticky="ew")

    card4.grid(row=0,column=3,padx=10,pady=10,sticky="ew")

    cards.grid_columnconfigure(0,weight=1)
    cards.grid_columnconfigure(1,weight=1)
    cards.grid_columnconfigure(2,weight=1)
    cards.grid_columnconfigure(3,weight=1)
        # -----------------------------------
    # Status Bar
    # -----------------------------------

    # Status bar frame to hold both status text and version
    status_frame = ctk.CTkFrame(app, height=28)
    status_frame.pack(
        fill="x",
        side="bottom",
        padx=10,
        pady=(0, 5)
    )

    status = ctk.CTkLabel(
        status_frame,
        text="Ready",
        anchor="w",
        height=28
    )
    status.pack(
        fill="x",
        side="left",
        expand=True
    )

    version_status = ctk.CTkLabel(
        status_frame,
        text=APP_VERSION,
        anchor="e",
        height=28,
        text_color="gray"
    )
    version_status.pack(
        side="right",
        padx=(10, 0)
    )

    # -----------------------------------
    # Footer
    # -----------------------------------

    footer = ctk.CTkLabel(
        app,
        text=f"{APP_NAME} {APP_VERSION}",
        text_color="gray"
    )

    footer.pack(
        side="bottom",
        pady=(0, 10)
    )

    # -----------------------------------
    # Focus
    # -----------------------------------

    toolbar.search_box.focus()

    app.mainloop()