from tkinter import Tk, Frame, Label, Entry, Button, StringVar, OptionMenu, Text, Scrollbar

class DarkThemeUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Weekly Work Report")
        self.master.geometry("600x400")
        self.master.configure(bg="#2E2E2E")

        self.frame = Frame(self.master, bg="#2E2E2E")
        self.frame.pack(pady=20)

        self.label_title = Label(self.frame, text="Weekly Work Report", bg="#2E2E2E", fg="#FFFFFF", font=("Helvetica", 16))
        self.label_title.pack()

        self.label_agency = Label(self.frame, text="Agency:", bg="#2E2E2E", fg="#FFFFFF")
        self.label_agency.pack(pady=5)
        self.entry_agency = Entry(self.frame, bg="#4E4E4E", fg="#FFFFFF")
        self.entry_agency.pack(pady=5)

        self.label_days = Label(self.frame, text="Reporting Days:", bg="#2E2E2E", fg="#FFFFFF")
        self.label_days.pack(pady=5)
        self.entry_days = Entry(self.frame, bg="#4E4E4E", fg="#FFFFFF")
        self.entry_days.pack(pady=5)

        self.label_devices = Label(self.frame, text="Number of Devices:", bg="#2E2E2E", fg="#FFFFFF")
        self.label_devices.pack(pady=5)
        self.device_count = StringVar(self.master)
        self.device_count.set("Select Number of Devices")
        self.device_menu = OptionMenu(self.frame, self.device_count, "1", "2", "3", "4", "5")
        self.device_menu.config(bg="#4E4E4E", fg="#FFFFFF")
        self.device_menu.pack(pady=5)

        self.label_general_text = Label(self.frame, text="General Text:", bg="#2E2E2E", fg="#FFFFFF")
        self.label_general_text.pack(pady=5)
        self.text_general = Text(self.frame, height=5, bg="#4E4E4E", fg="#FFFFFF")
        self.text_general.pack(pady=5)

        self.button_save = Button(self.frame, text="Save Data", command=self.save_data, bg="#4E4E4E", fg="#FFFFFF")
        self.button_save.pack(pady=5)

        self.button_clear = Button(self.frame, text="Clear Data", command=self.clear_data, bg="#4E4E4E", fg="#FFFFFF")
        self.button_clear.pack(pady=5)

        self.button_generate_report = Button(self.frame, text="Generate Report", command=self.generate_report, bg="#4E4E4E", fg="#FFFFFF")
        self.button_generate_report.pack(pady=5)

    def save_data(self):
        # Logic to save data
        pass

    def clear_data(self):
        # Logic to clear data with confirmation
        pass

    def generate_report(self):
        # Logic to generate PDF report
        pass

if __name__ == "__main__":
    root = Tk()
    app = DarkThemeUI(root)
    root.mainloop()