from fpdf import FPDF

class PDFGenerator:
    def __init__(self, name, agency, location, logo_path):
        self.name = name
        self.agency = agency
        self.location = location
        self.logo_path = logo_path
        self.pdf = FPDF()

    def setup_pdf(self):
        self.pdf.add_page()
        self.pdf.set_font("Arial", 'B', 16)
        if self.logo_path:
            self.pdf.image(self.logo_path, 10, 8, 33)
        self.pdf.cell(0, 10, f"Weekly Work Report", 0, 1, 'C')
        self.pdf.cell(0, 10, f"Name: {self.name}", 0, 1)
        self.pdf.cell(0, 10, f"Agency: {self.agency}", 0, 1)
        self.pdf.cell(0, 10, f"Location: {self.location}", 0, 1)
        self.pdf.ln(10)

    def add_report_content(self, content):
        self.pdf.set_font("Arial", size=12)
        self.pdf.multi_cell(0, 10, content)

    def save_pdf(self, filename):
        self.pdf.output(filename)

    def generate_report(self, content, filename):
        self.setup_pdf()
        self.add_report_content(content)
        self.save_pdf(filename)