import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import time

from services.excel_importer import import_excel

from database.repository import (
    search_consumer,
    get_total_records,
    get_database_size
)

from app.details_window import show_consumer


def start_app():

    # ----------------------------
    # Theme
    # ----------------------------

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # ----------------------------
    # Main Window
    # ----------------------------

    app = ctk.CTk()

    app.title("Meter Data Manager Pro")

    app.geometry("1200x900")

    app.minsize(1100, 850)

    # ----------------------------
    # Variables
    # ----------------------------

    start_time = 0

    # ----------------------------
    # Progress Callback
    # ----------------------------

    def update_progress(current, total):

        if total <= 0:
            return

        percent = current / total

        progress_bar.set(percent)

        progress_percent.configure(
            text=f"{percent*100:.1f}%"
        )

        progress_label.configure(
            text=f"Processed : {current:,} / {total:,}"
        )

        app.update_idletasks()

    # ----------------------------
    # Import Function
    # ----------------------------

    def do_import():

        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[
                ("Excel Files", "*.xlsx *.xls")
            ]
        )

        if not file_path:
            return

        def worker():

            nonlocal start_time

            try:

                start_time = time.time()

                import_btn.configure(state="disabled")

                progress_bar.set(0)

                progress_percent.configure(
                    text="0%"
                )

                progress_label.configure(
                    text="Starting Import..."
                )

                status.configure(
                    text="Importing..."
                )

                total = import_excel(
                    file_path,
                    progress_callback=update_progress
                )

                seconds = round(
                    time.time() - start_time,
                    2
                )

                progress_bar.set(1)

                progress_percent.configure(
                    text="100%"
                )

                progress_label.configure(
                    text="Import Completed"
                )

                total_records.configure(
                    text=f"Database Records : {get_total_records():,}"
                )

                status.configure(
                    text="Ready"
                )
                

                messagebox.showinfo(
                    "Import Complete",
                    f"""
Total Imported : {total:,}

Time : {seconds} sec
"""
                )

            except Exception as e:

                messagebox.showerror(
                    "Import Error",
                    str(e)
                )

                status.configure(
                    text="Import Failed"
                )

            finally:

                import_btn.configure(
                    state="normal"
                )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    # ----------------------------
    # Search
    # ----------------------------

    def do_search():

        value = search_box.get().strip()

        if value == "":

            messagebox.showwarning(
                "Warning",
                "Enter Meter No or Consumer No"
            )

            return

        row = search_consumer(value)

        if row:

            status.configure(
                text="Consumer Found"
            )

            show_consumer(row)

        else:

            status.configure(
                text="Consumer Not Found"
            )

            messagebox.showinfo(
                "Search",
                "Consumer Not Found"
            )

    # ----------------------------
    # Header
    # ----------------------------

    title = ctk.CTkLabel(
        app,
        text="Meter Data Manager Pro",
        font=("Arial", 28, "bold")
    )

    title.pack(pady=20)

    # ----------------------------
    # Toolbar
    # ----------------------------

    toolbar = ctk.CTkFrame(app)

    toolbar.pack(
        fill="x",
        padx=20
    )

    import_btn = ctk.CTkButton(
        toolbar,
        text="📂 Import Excel",
        width=160,
        command=do_import
    )

    import_btn.pack(
        side="left",
        padx=10,
        pady=10
    )

    search_box = ctk.CTkEntry(
        toolbar,
        width=450,
        placeholder_text="Meter No / Consumer No"
    )

    search_box.pack(
        side="left",
        padx=10
    )

    search_box.bind(
        "<Return>",
        lambda e: do_search()
    )

    search_btn = ctk.CTkButton(
        toolbar,
        text="Search",
        width=120,
        command=do_search
    )

    search_btn.pack(
        side="left",
        padx=10
    )
        # ----------------------------
    # Progress Frame
    # ----------------------------

    progress_frame = ctk.CTkFrame(app)

    progress_frame.pack(
        fill="x",
        padx=20,
        pady=10
    )

    progress_label = ctk.CTkLabel(
        progress_frame,
        text="Ready",
        anchor="w"
    )

    progress_label.pack(
        fill="x",
        padx=10,
        pady=(10, 5)
    )

    progress_bar = ctk.CTkProgressBar(
        progress_frame
    )

    progress_bar.pack(
        fill="x",
        padx=10
    )

    progress_bar.set(0)

    progress_percent = ctk.CTkLabel(
        progress_frame,
        text="0%"
    )

    progress_percent.pack(
        pady=(5, 10)
    )

    # ----------------------------
    # Information Frame
    # ----------------------------

    info_frame = ctk.CTkFrame(app)

    info_frame.pack(
        fill="x",
        padx=20
    )

    total_records = ctk.CTkLabel(
        info_frame,
        text=f"Database Records : {get_total_records():,}",
        font=("Arial", 15, "bold")
    )

    total_records.pack(
        side="left",
        padx=10,
        pady=10
    )

    status = ctk.CTkLabel(
        info_frame,
        text="Ready",
        font=("Arial", 14)
    )

    status.pack(
        side="right",
        padx=10
    )

        # ----------------------------
    # Dashboard
    # ----------------------------

    dashboard = ctk.CTkFrame(app)

    dashboard.pack(
        fill="x",
        padx=20,
        pady=15
    )

    dashboard_title = ctk.CTkLabel(
        dashboard,
        text="📊 Dashboard",
        font=("Arial", 18, "bold")
    )

    dashboard_title.pack(
        anchor="w",
        padx=15,
        pady=(10, 5)
    )

    info = ctk.CTkFrame(dashboard)

    info.pack(
        fill="x",
        padx=10,
        pady=(0, 10)
    )

    db_records = ctk.CTkLabel(
        info,
        text=f"Database Records : {get_total_records():,}",
        font=("Arial", 15)
    )

    db_records.grid(
        row=0,
        column=0,
        padx=20,
        pady=8,
        sticky="w"
    )

    db_size = ctk.CTkLabel(
        info,
        text=f"Database Size : {get_database_size()}",
        font=("Arial", 15)
    )

    db_size.grid(
        row=0,
        column=1,
        padx=20,
        pady=8,
        sticky="w"
    )

    # ----------------------------
    # Footer
    # ----------------------------
        # ----------------------------
    # Second Row
    # ----------------------------

    last_import = ctk.CTkLabel(
        info,
        text="Last Import : --",
        font=("Arial", 15)
    )

    last_import.grid(
        row=1,
        column=0,
        padx=20,
        pady=8,
        sticky="w"
    )

    import_time = ctk.CTkLabel(
        info,
        text="Import Time : --",
        font=("Arial", 15)
    )

    import_time.grid(
        row=1,
        column=1,
        padx=20,
        pady=8,
        sticky="w"
    )

    app_version = ctk.CTkLabel(
        info,
        text="Version : Build 1.1",
        font=("Arial", 15)
    )

    app_version.grid(
        row=2,
        column=0,
        padx=20,
        pady=8,
        sticky="w"
    )

    dashboard_status = ctk.CTkLabel(
        info,
        text="Status : Ready",
        font=("Arial", 15)
    )

    dashboard_status.grid(
        row=2,
        column=1,
        padx=20,
        pady=8,
        sticky="w"
    )

    # Equal column width
    info.grid_columnconfigure(0, weight=1)
    info.grid_columnconfigure(1, weight=1)

    footer = ctk.CTkLabel(
        app,
        text="Meter Data Manager Pro v1.0",
        text_color="gray"
    )

    footer.pack(
        side="bottom",
        pady=10
    )

    # ----------------------------
    # Focus
    # ----------------------------

    search_box.focus()

    app.mainloop()