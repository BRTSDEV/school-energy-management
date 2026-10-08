"""Entry point -- NOTE: written in 2026 (the original launcher was lost)."""
import customtkinter as ctk

from app import SEMApp

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    SEMApp(root)
    root.mainloop()
