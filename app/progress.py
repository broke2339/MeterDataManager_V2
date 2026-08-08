import customtkinter as ctk


class ProgressFrame(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        self.pack(
            fill="x",
            padx=20,
            pady=10
        )

        self.label = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="w"
        )

        self.label.pack(
            fill="x",
            padx=10,
            pady=(10, 5)
        )

        self.bar = ctk.CTkProgressBar(self)

        self.bar.pack(
            fill="x",
            padx=10
        )

        self.bar.set(0)

        self.percent = ctk.CTkLabel(
            self,
            text="0%"
        )

        self.percent.pack(
            pady=(5, 10)
        )

    def update(self, current, total):

        if total <= 0:
            return

        p = current / total

        self.bar.set(p)

        self.percent.configure(
            text=f"{p*100:.1f}%"
        )

        self.label.configure(
            text=f"Processed : {current:,} / {total:,}"
        )

    def reset(self):

        self.bar.set(0)

        self.percent.configure(text="0%")

        self.label.configure(text="Ready")

    def complete(self):

        self.bar.set(1)

        self.percent.configure(text="100%")

        self.label.configure(
            text="Import Completed"
        )