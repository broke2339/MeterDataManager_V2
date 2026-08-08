import time
import customtkinter as ctk
from tkinter import filedialog, messagebox
from openpyxl import Workbook
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table as PDFTable, TableStyle

from services.excel_importer import import_excel

from database.repository import (
    search_consumer,
    search_consumers,
    get_total_records,
    get_database_size
)

from app.details_window import show_consumer
from app.toolbar import Toolbar
from app.progress import ProgressFrame
from app.consumer_table import ConsumerTable


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def start_app():

    app = ctk.CTk()

    app.title("Meter Data Manager Pro")

    app.geometry("1250x750")

    app.minsize(1100,700)

    # -----------------------------------
    # Variables
    # -----------------------------------

    selected_row = None

    start_time = 0

    search_after_id = None

    # -----------------------------------
    # Search Function
    # -----------------------------------

    def do_search():

        value = toolbar.search_box.get().strip()

        if value == "":
            return

        rows = search_consumers(value)

        table.load(rows)

    # -----------------------------------
    # Open Consumer
    # -----------------------------------

    def open_from_table(values):

        meter = values[0]

        row = search_consumer(meter)

        if row:

            show_consumer(row)

    def schedule_live_search(event=None):

        nonlocal search_after_id

        if search_after_id:

            app.after_cancel(search_after_id)

        search_after_id = app.after(300, perform_live_search)

    def perform_live_search():

        nonlocal search_after_id

        search_after_id = None

        if toolbar.search_box.get().strip() == "":

            table.load([])

            return

        do_search()

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

    progress = ProgressFrame(app)

    table = ConsumerTable(

        app,

        open_callback=open_from_table

    )

    table.pack(

        fill="both",

        expand=True,

        padx=20,

        pady=10

    )

    table.bind("<Double-1>", open_selected_consumer)
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

    status = ctk.CTkLabel(
        app,
        text="Ready",
        anchor="w",
        height=28
    )

    status.pack(
        fill="x",
        side="bottom",
        padx=10,
        pady=(0, 5)
    )

    # -----------------------------------
    # Footer
    # -----------------------------------

    footer = ctk.CTkLabel(
        app,
        text="Meter Data Manager Pro v2.0",
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