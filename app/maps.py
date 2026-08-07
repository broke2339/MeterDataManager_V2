import webbrowser
from tkinter import messagebox


def open_google_maps(location):

    if not location:
        messagebox.showwarning(
            "Location",
            "Location not available."
        )
        return

    location = str(location).strip()

    if location == "" or location.upper() == "#N/A":
        messagebox.showwarning(
            "Location",
            "Invalid location."
        )
        return

    url = f"https://www.google.com/maps?q={location}"

    webbrowser.open(url)