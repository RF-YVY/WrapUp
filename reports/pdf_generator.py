
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
import os

def generate_pdf_report(filename, settings, week_data, summary, report_range, date_start, date_end, additional_field=None, additional_subfields=None):
    if additional_field is None:
        additional_field = settings.get('additional_field', '').strip()
    if additional_subfields is None:
        additional_subfields = settings.get('additional_subfields', [])

    from reportlab.platypus import Image
    from reportlab.lib.units import inch

    doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=50, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    normal_style.fontName = "Helvetica"
    normal_style.fontSize = 11
    normal_style.leading = 14
    normal_style.wordWrap = 'CJK'
    bold_style = styles["Heading4"]
    bold_style.fontName = "Helvetica-Bold"
    bold_style.fontSize = 14
    bold_style.leading = 16
    header_style = ParagraphStyle('header', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22, alignment=TA_LEFT)
    subheader_style = ParagraphStyle('subheader', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, leading=16, alignment=TA_LEFT)

    # --- onFirstPage and onLaterPages callbacks ---
    def draw_header_and_logo(canvas, doc):
        width, height = letter
        margin = 40
        text_left = margin
        logo_width = 1.2 * inch
        logo_height = 0.7 * inch
        logo_x = width - logo_width - margin
        logo_y = height - logo_height - margin + 10
        # Draw logo at top right
        logo_path = settings.get('logo')
        if logo_path and os.path.exists(logo_path):
            try:
                canvas.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
            except Exception:
                pass
        # Draw header text at top left
        y = height - margin
        canvas.setFont("Helvetica-Bold", 18)
        canvas.drawString(text_left, y, "Weekly Report")
        y -= 24
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(text_left, y, f"Report Range: {report_range} ({date_start} to {date_end})")
        y -= 18
        canvas.setFont("Helvetica", 12)
        canvas.drawString(text_left, y, f"Name: {settings.get('name', '')}")
        y -= 16
        canvas.drawString(text_left, y, f"Agency: {settings.get('agency', '')}")
        y -= 16
        canvas.drawString(text_left, y, f"Location: {settings.get('location', '')}")
        y -= 12
        canvas.setStrokeColor(colors.grey)
        canvas.line(margin, y, width-margin, y)

    def draw_nothing(canvas, doc):
        pass

    elements.append(Spacer(1, 90))  # Space below header/logo

    # --- Uniform font size logic ---
    # Find the minimum font size needed for all day names (e.g., Wednesday)
    min_day_font_size = 11
    for day in week_data.keys():
        if len(day) > 8:
            min_day_font_size = min(min_day_font_size, 9)
    # Optionally, you can set a lower bound if you want even smaller for very long names
    # Find the minimum font size needed for all general/additional fields
    min_data_font_size = 11
    for daydata in week_data.values():
        general = daydata.get('general', '')
        if len(general) > 300:
            min_data_font_size = min(min_data_font_size, 8)
        elif len(general) > 150:
            min_data_font_size = min(min_data_font_size, 9)
        additional = daydata.get('additional', {})
        for val in additional.values():
            val = str(val)
            if len(val) > 100:
                min_data_font_size = min(min_data_font_size, 8)
            elif len(val) > 50:
                min_data_font_size = min(min_data_font_size, 9)
    # Use the smallest font size needed for all table cells (day, general, additional)
    uniform_font_size = min(min_day_font_size, min_data_font_size)
    uniform_leading = 10 if uniform_font_size <= 8 else (12 if uniform_font_size == 9 else 14)

    # Table header
    table_data = []
    header_row = [Paragraph('<b>Day</b>', bold_style), Paragraph('<b>General Notes</b>', bold_style)]
    for sub in additional_subfields:
        header_row.append(Paragraph(f'<b>{sub}</b>', bold_style))
    table_data.append(header_row)

    # Table rows
    for day, daydata in week_data.items():
        day_style = ParagraphStyle('day', parent=normal_style)
        day_style.fontSize = uniform_font_size
        day_style.leading = uniform_leading
        row = [Paragraph(day, day_style)]
        general = daydata.get('general', '')
        gen_style = ParagraphStyle('gen', parent=normal_style)
        gen_style.fontSize = uniform_font_size
        gen_style.leading = uniform_leading
        row.append(Paragraph(general.replace('\n', '<br/>'), gen_style))
        additional = daydata.get('additional', {})
        for sub in additional_subfields:
            val = str(additional.get(sub, ''))
            sub_style = ParagraphStyle('sub', parent=normal_style)
            sub_style.fontSize = uniform_font_size
            sub_style.leading = uniform_leading
            row.append(Paragraph(val.replace('\n', '<br/>'), sub_style))
        table_data.append(row)

    # Table style
    # Make day column wider (80), general notes (190), subfields (90 each)
    col_widths = [80, 190] + [90 for _ in additional_subfields]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 13),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 16))

    # Summary/comments section
    elements.append(Paragraph("<b>Summary/Comments:</b>", bold_style))
    sum_style = ParagraphStyle('sum', parent=normal_style)
    sum_style.fontSize = 11
    sum_style.leading = 14
    if len(summary) > 600:
        sum_style.fontSize = 8
        sum_style.leading = 10
    elif len(summary) > 300:
        sum_style.fontSize = 9
        sum_style.leading = 12
    elements.append(Paragraph(summary.replace('\n', '<br/>'), sum_style))

    doc.build(elements, onFirstPage=draw_header_and_logo, onLaterPages=draw_nothing)
