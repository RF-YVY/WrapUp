from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import os

def generate_pdf_report(filename, settings, week_data, summary, report_range, date_start, date_end, additional_field=None, additional_subfields=None):
    if additional_field is None:
        additional_field = settings.get('additional_field', '').strip()
    if additional_subfields is None:
        additional_subfields = settings.get('additional_subfields', [])

    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 50
    logo_width = 100
    logo_height = 60
    margin = 40
    text_left = margin
    logo_x = width - logo_width - margin
    logo_y = y - logo_height + 10

    # Draw logo at top right, no text overlap
    if settings.get('logo') and os.path.exists(settings['logo']):
        try:
            c.drawImage(ImageReader(settings['logo']), logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    # Header text, left-justified
    c.setFont("Helvetica-Bold", 18)
    c.drawString(text_left, y, "Weekly Report")
    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(text_left, y, f"Report Range: {report_range} ({date_start} to {date_end})")
    y -= 20
    c.setFont("Helvetica", 12)
    c.drawString(text_left, y, f"Name: {settings.get('name', '')}")
    y -= 18
    c.drawString(text_left, y, f"Agency: {settings.get('agency', '')}")
    y -= 18
    c.drawString(text_left, y, f"Location: {settings.get('location', '')}")
    y -= 20
    c.setStrokeColor(colors.grey)
    c.line(margin, y, width-margin, y)
    y -= 20
    # Table header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Day")
    c.drawString(margin+80, y, "General Notes")
    x = margin + 220
    for sub in additional_subfields:
        c.drawString(x, y, sub)
        x += 100
    y -= 18
    c.setFont("Helvetica", 12)
    for day, daydata in week_data.items():
        if y < 100:
            c.showPage()
            y = height - 50
        general = daydata.get('general', '')
        additional = daydata.get('additional', {})
        c.drawString(margin, y, day)
        c.drawString(margin+80, y, general[:40])
        x = margin + 220
        for sub in additional_subfields:
            c.drawString(x, y, str(additional.get(sub, ''))[:18])
            x += 100
        y -= 18
    # Summary/comments section
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Summary/Comments:")
    y -= 18
    c.setFont("Helvetica", 12)
    for line in summary.splitlines():
        if y < 60:
            c.showPage()
            y = height - 50
        c.drawString(margin+20, y, line)
        y -= 16
    c.save()
