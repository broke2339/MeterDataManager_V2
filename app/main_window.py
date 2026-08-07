import customtkinter as ctk
from tkinter import filedialog, messagebox

from services.excel_importer import import_excel
from database.repository import search_consumer
from app.details_window import show_consumer


def start_app():

    # Theme
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # Window
    app = ctk.CTk()
    app.title("Meter Data Manager Pro")
    app.geometry("900x400")

    # -------------------------
    # Import Function
    # -------------------------

    def do_import():

        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )

        if not file_path:
            return

        try:

            status.configure(text="Importing... Please Wait")

            app.update()

            total = import_excel(file_path)

            status.configure(
                text=f"Import Completed | Records : {total}"
            )

            messagebox.showinfo(
                "Success",
                f"{total} Records Imported Successfully."
            )

        except Exception as e:

            status.configure(text="Import Failed")

            messagebox.showerror(
                "Error",
                str(e)
            )

    # -------------------------
    # Search Function
    # -------------------------

    def do_search():

        value = search_box.get().strip()

        if value == "":

            messagebox.showwarning(
                "Warning",
                "Please Enter Meter No or Consumer No"
            )

            return

        row = search_consumer(value)

        if row:

            status.configure(text="Consumer Found")

            show_consumer(row)

        else:

            status.configure(text="Consumer Not Found")

            messagebox.showinfo(
                "Search",
                "Consumer Not Found"
            )
                # -------------------------
    # Header
    # -------------------------

    title = ctk.CTkLabel(
        app,
        text="Meter Data Manager Pro",
        font=("Arial", 26, "bold")
    )

    title.pack(pady=20)

    # -------------------------
    # Toolbar
    # -------------------------

    toolbar = ctk.CTkFrame(app)
    toolbar.pack(fill="x", padx=20)

    import_btn = ctk.CTkButton(
        toolbar,
        text="📂 Import Excel",
        width=150,
        command=do_import
    )

    import_btn.pack(side="left", padx=10, pady=10)

    search_box = ctk.CTkEntry(
        toolbar,
        width=400,
        placeholder_text="Enter Meter No or Consumer No"
    )

    search_box.pack(side="left", padx=10)

    search_box.bind("<Return>", lambda event: do_search())

    search_btn = ctk.CTkButton(
        toolbar,
        text="Search",
        width=100,
        command=do_search
    )

    search_btn.pack(side="left", padx=10)

    # -------------------------
    # Status Bar
    # -------------------------

    status = ctk.CTkLabel(
        app,
        text="Ready",
        anchor="w"
    )

    status.pack(
        fill="x",
        padx=20,
        pady=20
    )

    # Search box par cursor
    search_box.focus()

    app.mainloop()