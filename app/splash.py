import customtkinter as ctk
from PIL import Image
import tkinter as tk
from pathlib import Path


class SplashScreen:
    def __init__(self, parent_window_callback):
        """
        Initialize and display the splash screen.
        
        Args:
            parent_window_callback: Callback function to create main window after splash closes
        """
        self.parent_callback = parent_window_callback
        self.splash = ctk.CTk()
        self.splash.geometry("600x350")
        self.splash.resizable(False, False)
        self.splash.attributes("-topmost", True)
        
        # Center window on screen
        self.splash.update_idletasks()
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 350) // 2
        self.splash.geometry(f"+{x}+{y}")
        
        # Configure background
        self.splash.configure(fg_color="#ffffff")
        
        # Main frame
        main_frame = ctk.CTkFrame(self.splash, fg_color="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Icon
        try:
            icon_path = Path(__file__).parent.parent.parent / "assets" / "app_icon.png"
            if icon_path.exists():
                icon_image = Image.open(icon_path)
                icon_image = icon_image.resize((80, 80), Image.Resampling.LANCZOS)
                icon_photo = ctk.CTkImage(light_image=icon_image, size=(80, 80))
                icon_label = ctk.CTkLabel(main_frame, image=icon_photo, text="")
                icon_label.image = icon_photo
                icon_label.pack(pady=(0, 15))
        except Exception as e:
            print(f"Icon load error: {e}")
        
        # App Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Meter Data Manager Pro",
            font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
            text_color="#333333"
        )
        title_label.pack(pady=(0, 5))
        
        # Version
        version_label = ctk.CTkLabel(
            main_frame,
            text="Version 2.0 Stable",
            font=ctk.CTkFont(family="Arial", size=12),
            text_color="#666666"
        )
        version_label.pack(pady=(0, 20))
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            main_frame,
            width=500,
            height=6,
            fg_color="#e0e0e0",
            progress_color="#4CAF50"
        )
        self.progress_bar.pack(pady=(0, 15))
        self.progress_bar.set(0.3)
        
        # Loading Text
        loading_label = ctk.CTkLabel(
            main_frame,
            text="Loading...",
            font=ctk.CTkFont(family="Arial", size=11),
            text_color="#999999"
        )
        loading_label.pack(pady=(0, 20))
        
        # Developer Credit
        dev_label = ctk.CTkLabel(
            main_frame,
            text="Developed by Sachin Sharma",
            font=ctk.CTkFont(family="Arial", size=10),
            text_color="#cccccc"
        )
        dev_label.pack(side="bottom")
        
        # Close splash after 2 seconds
        self.splash.after(2000, self.close_splash)
    
    def close_splash(self):
        """Close splash screen and open main application."""
        self.splash.destroy()
        self.parent_callback()


def show_splash(main_window_callback):
    """
    Display splash screen.
    
    Args:
        main_window_callback: Function to call after splash closes
    """
    SplashScreen(main_window_callback)
