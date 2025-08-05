import tkinter as tk
from tkinter import messagebox
from ui.dark_theme import create_dark_theme_ui
from data.storage import load_data, save_data
from reports.pdf_generator import generate_pdf_report
from utils.confirmation import confirm_clear_data

class WeeklyWorkReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weekly Work Report App")
        self.root.geometry("600x400")
        self.data = load_data()
        self.create_ui()

    def create_ui(self):
        create_dark_theme_ui(self.root, self.data, self.save_data, self.clear_data, self.generate_report)

    def save_data(self, data):
        save_data(data)
        messagebox.showinfo("Success", "Data saved successfully!")

    def clear_data(self):
        if confirm_clear_data():
            self.data.clear()
            messagebox.showinfo("Cleared", "Data cleared successfully!")

    def generate_report(self):
        name = self.data.get("name", "")
        agency = self.data.get("agency", "")
        location = self.data.get("location", "")
        logo = self.data.get("logo", "")
        generate_pdf_report(name, agency, location, logo)
        messagebox.showinfo("Report", "PDF report generated successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeeklyWorkReportApp(root)
    root.mainloop()