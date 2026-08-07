import customtkinter as ctk
from tkinter import messagebox
from app.maps import open_google_maps


# ==========================================
# Copy Single Value
# ==========================================

def copy_text(text):

    temp = ctk.CTkToplevel()

    temp.withdraw()

    temp.clipboard_clear()

    temp.clipboard_append(str(text))

    temp.update()

    temp.destroy()


# ==========================================
# Copy All Consumer Details
# ==========================================

def copy_all(row):

    text = f"""Meter No : {row[0]}

Consumer No : {row[1]}

Consumer Name : {row[2]}

Father Name : {row[3]}

Address : {row[4]}

Zone : {row[5]}

Division : {row[6]}

Subdivision : {row[7]}

Mobile 1 : {row[8]}

Mobile 2 : {row[9]}

Location : {row[10]}

Remark : {row[11]}
"""

    copy_text(text)

    messagebox.showinfo(
        "Copy",
        "Consumer Details Copied Successfully."
    )


# ==========================================
# Consumer Window
# ==========================================

def show_consumer(row):

    if row is None:
        return

    def safe(value):
        if value is None:
            return "--"

        value = str(value).strip()

        if value == "" or value.lower() == "none":
            return "--"

        return value

    win = ctk.CTkToplevel()

    win.title("Consumer Details")

    win.geometry("950x720")

    win.minsize(900, 650)

    title = ctk.CTkLabel(
        win,
        text="Consumer Details",
        font=("Arial", 26, "bold")
    )

    title.pack(
        pady=(15, 5)
    )

    scroll = ctk.CTkScrollableFrame(
        win,
        width=880,
        height=520
    )

    scroll.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    labels = [

        ("Meter No", safe(row[0]), True),

        ("Consumer No", safe(row[1]), True),

        ("Consumer Name", safe(row[2]), False),

        ("Father Name", safe(row[3]), False),

        ("Address", safe(row[4]), True),

        ("Zone", safe(row[5]), False),

        ("Division", safe(row[6]), False),

        ("Subdivision", safe(row[7]), False),

        ("Mobile 1", safe(row[8]), True),

        ("Mobile 2", safe(row[9]), True),

        ("Location", safe(row[10]), True),

        ("Remark", safe(row[11]), False)

    ]

    for i, item in enumerate(labels):

        title_text, value, allow_copy = item

        ctk.CTkLabel(
            scroll,
            text=title_text,
            width=150,
            anchor="w",
            font=("Arial", 14, "bold")
        ).grid(
            row=i,
            column=0,
            padx=10,
            pady=8,
            sticky="nw"
        )

        ctk.CTkLabel(
            scroll,
            text=value,
            width=520,
            justify="left",
            wraplength=520,
            anchor="w"
        ).grid(
            row=i,
            column=1,
            padx=10,
            pady=8,
            sticky="w"
        )

        if allow_copy:

            ctk.CTkButton(
                scroll,
                text="Copy",
                width=70,
                command=lambda v=value: copy_text(v)
            ).grid(
                row=i,
                column=2,
                padx=10,
                pady=5
            )
                # ==========================================
    # Bottom Buttons
    # ==========================================

    bottom = ctk.CTkFrame(win)

    bottom.pack(
        fill="x",
        padx=20,
        pady=(5, 15)
    )

    copy_all_btn = ctk.CTkButton(
        bottom,
        text="📋 Copy All",
        width=150,
        command=lambda: copy_all(row)
    )

    copy_all_btn.pack(
        side="left",
        padx=10,
        pady=10
    )

    maps_btn = ctk.CTkButton(
        bottom,
        text="📍 Google Maps",
        width=170,
        command=lambda: open_google_maps(safe(row[10]))
    )

    maps_btn.pack(
        side="left",
        padx=10,
        pady=10
    )

    close_btn = ctk.CTkButton(
        bottom,
        text="❌ Close",
        width=120,
        fg_color="#d32f2f",
        hover_color="#b71c1c",
        command=win.destroy
    )

    close_btn.pack(
        side="right",
        padx=10,
        pady=10
    )

    win.focus()
    win.grab_set()