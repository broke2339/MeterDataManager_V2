import customtkinter as ctk


class Toolbar(ctk.CTkFrame):

    def __init__(self, master, import_callback, search_callback):

        super().__init__(master)

        self.pack(
            fill="x",
            padx=20,
            pady=10
        )

        self.import_btn = ctk.CTkButton(
            self,
            text="📂 Import Excel",
            width=170,
            command=import_callback
        )

        self.import_btn.pack(
            side="left",
            padx=10,
            pady=10
        )

        self.search_box = ctk.CTkEntry(
            self,
            width=450,
            placeholder_text="Meter No / Consumer No"
        )

        self.search_box.pack(
            side="left",
            padx=10
        )

        self.search_box.bind(
            "<Return>",
            lambda e: search_callback()
        )

        self.search_btn = ctk.CTkButton(
            self,
            text="🔍 Search",
            width=120,
            command=search_callback
        )

        self.search_btn.pack(
            side="left",
            padx=10
        )