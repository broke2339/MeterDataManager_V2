import customtkinter as ctk


def copy_text(text):
    window = ctk.CTkToplevel()
    window.withdraw()

    window.clipboard_clear()
    window.clipboard_append(str(text))

    window.update()
    window.destroy()


def show_consumer(row):

    if row is None:
        return

    win = ctk.CTkToplevel()

    win.title("Consumer Details")

    win.geometry("800x650")

    labels = [

        ("Meter No", row[0], True),
        ("Consumer No", row[1], True),
        ("Consumer Name", row[2], False),
        ("Father Name", row[3], False),
        ("Address", row[4], False),
        ("Zone", row[5], False),
        ("Division", row[6], False),
        ("Subdivision", row[7], False),
        ("Mobile 1", row[8], True),
        ("Mobile 2", row[9], True),
        ("Location", row[10], True),
        ("Remark", row[11], False)

    ]

    for i, item in enumerate(labels):

        title, value, copy_btn = item

        ctk.CTkLabel(
            win,
            text=title,
            width=150,
            anchor="w"
        ).grid(row=i, column=0, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(
            win,
            text=str(value),
            width=450,
            anchor="w"
        ).grid(row=i, column=1, padx=10, pady=8, sticky="w")

        if copy_btn:

            ctk.CTkButton(
                win,
                text="Copy",
                width=70,
                command=lambda v=value: copy_text(v)
            ).grid(row=i, column=2, padx=10)