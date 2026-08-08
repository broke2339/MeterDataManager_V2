import customtkinter as ctk
from tkinter import ttk


class ConsumerTable(ctk.CTkFrame):

    def __init__(self, master, open_callback):

        super().__init__(master)

        self.open_callback = open_callback

        columns = (
            "Meter No",
            "Consumer No",
            "Consumer Name",
            "Mobile",
            "Division"
        )

        self.table = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=15
        )

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=180)

        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.table.yview
        )

        self.table.configure(
            yscrollcommand=scrollbar.set
        )

        self.table.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.table.bind(
            "<Double-1>",
            self.on_double_click
        )

    def load(self, rows):

        self.clear()

        for row in rows:
            self.table.insert("", "end", values=row)

    def clear(self):

        for item in self.table.get_children():
            self.table.delete(item)

    def on_double_click(self, event):

        item = self.table.focus()

        if not item:
            return

        values = self.table.item(item)["values"]

        self.open_callback(values)

    def get_selected_meter(self):

        selected_item = self.table.focus()

        if not selected_item:
            return None

        values = self.table.item(selected_item).get("values", [])

        if not values:
            return None

        return values[0]