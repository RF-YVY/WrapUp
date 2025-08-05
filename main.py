import sys
import json
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit, QDialog, QFileDialog, QMessageBox, QFormLayout, QGroupBox, QScrollArea, QTextEdit, QDialogButtonBox, QTextBrowser, QSplitter
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt
from data.storage import save_data, load_data, clear_data
from reports.pdf_generator import generate_pdf_report

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(400)
        layout = QFormLayout()
        self.name_input = QLineEdit()
        self.agency_input = QLineEdit()
        self.location_input = QLineEdit()
        self.logo_path_input = QLineEdit()
        self.logo_path_input.setReadOnly(True)
        self.logo_button = QPushButton("Choose Logo")
        self.logo_button.clicked.connect(self.choose_logo)
        layout.addRow("Name:", self.name_input)
        layout.addRow("Agency:", self.agency_input)
        layout.addRow("Location:", self.location_input)
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.logo_path_input)
        logo_layout.addWidget(self.logo_button)
        layout.addRow("Logo:", logo_layout)
        # Reporting range selection
        self.range_combo = QComboBox()
        self.range_combo.addItems(["Monday–Friday", "Thursday–Thursday"])
        layout.addRow("Reporting Range:", self.range_combo)

        # Additional custom field for each day
        self.additional_field_label = QLineEdit()
        self.additional_field_label.setPlaceholderText("e.g. Vehicle Mileage")
        self.additional_field_names = QLineEdit()
        self.additional_field_names.setPlaceholderText("Comma separated subfields, e.g. Start, End")
        layout.addRow("Additional Field Name (optional):", self.additional_field_label)
        layout.addRow("Subfields (comma separated):", self.additional_field_names)

        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.accept)
        layout.addRow(self.save_button)
        self.setLayout(layout)

    def choose_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Logo", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.logo_path_input.setText(file_path)

    def get_settings(self):
        additional_field = self.additional_field_label.text().strip()
        subfields = [s.strip() for s in self.additional_field_names.text().split(',') if s.strip()]
        return {
            'name': self.name_input.text(),
            'agency': self.agency_input.text(),
            'location': self.location_input.text(),
            'logo': self.logo_path_input.text(),
            'report_range': self.range_combo.currentText(),
            'additional_field': additional_field,
            'additional_subfields': subfields
        }

    def set_settings(self, settings):
        self.name_input.setText(settings.get('name', ''))
        self.agency_input.setText(settings.get('agency', ''))
        self.location_input.setText(settings.get('location', ''))
        self.logo_path_input.setText(settings.get('logo', ''))
        if 'report_range' in settings:
            idx = self.range_combo.findText(settings['report_range'])
            if idx != -1:
                self.range_combo.setCurrentIndex(idx)
        self.additional_field_label.setText(settings.get('additional_field', ''))
        self.additional_field_names.setText(', '.join(settings.get('additional_subfields', [])))

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Weekly Action Report")
        self.setMinimumSize(500, 400)
        layout = QVBoxLayout()
        about_text = QTextBrowser()
        about_text.setOpenExternalLinks(True)
        about_text.setHtml('''
        <h2>Weekly Report</h2>
        <b>Author:</b> Brett Wicker<br>
        <b>GitHub:</b> <a href="https://github.com/RF-YVY">https://github.com/RF-YVY</a><br><br>
        <b>Attribution:</b> Built with PySide6, ReportLab, Pillow. Icon by <a href="https://www.flaticon.com/free-icons/report">Report icons created by Freepik - Flaticon</a> <br><br>
        <b>Features:</b>
        <ul>
        <li>Modern dark/light themed UI</li>
        <li>Customizable reporting range (Monday–Friday or Thursday–Thursday)</li>
        <li>Daily notes, multiple agency/device intake per day</li>
        <li>Persistent data saving and clearing</li>
        <li>PDF and rich text report generation (with logo and header info)</li>
        <li>Copyable report for email</li>
        <li>Settings for user info and logo</li>
        <li>Tab navigation between fields</li>
        </ul>
        ''')
        layout.addWidget(about_text)
        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(self.accept)
        layout.addWidget(btns)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weekly Action Report")
        self.last_logo_path = ''
        self.last_pdf_path = ''
        self.theme = 'dark'
        self.summary_text = ''
        self.settings = load_data().get('settings', {})
        self.current_days = self.get_current_days()
        self.setStyleSheet(self.dark_theme())
        self.init_ui()
        self.load_saved_data()

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout()

        # Sidebar with buttons (in a QWidget)
        self.sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()
        save_button = QPushButton("Save")
        clear_button = QPushButton("Clear Data")
        report_button = QPushButton("Generate Report")
        richtext_button = QPushButton("Rich Text Export")
        settings_button = QPushButton("Settings")
        about_button = QPushButton("About")
        reset_button = QPushButton("Reset Application")
        sidebar_layout.addWidget(save_button)
        sidebar_layout.addWidget(clear_button)
        sidebar_layout.addWidget(report_button)
        sidebar_layout.addWidget(richtext_button)
        sidebar_layout.addStretch(1)
        sidebar_layout.addWidget(settings_button)
        sidebar_layout.addWidget(reset_button)
        sidebar_layout.addWidget(about_button)
        self.sidebar_widget.setLayout(sidebar_layout)
        self.sidebar_widget.setFixedWidth(170)

        # Sidebar toggle button
        self.sidebar_toggle_btn = QPushButton("☰")
        self.sidebar_toggle_btn.setFixedWidth(30)
        self.sidebar_toggle_btn.setToolTip("Show/Hide Menu")
        self.sidebar_toggle_btn.clicked.connect(self.toggle_sidebar)
        sidebar_toggle_layout = QVBoxLayout()
        sidebar_toggle_layout.addWidget(self.sidebar_toggle_btn)
        sidebar_toggle_layout.addStretch(1)
        sidebar_toggle_widget = QWidget()
        sidebar_toggle_widget.setLayout(sidebar_toggle_layout)
        sidebar_toggle_widget.setFixedWidth(30)

        # Main content area (vertical)
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        # Header section (matches PDF/Rich Text)
        header_layout = QHBoxLayout()
        left_header = QVBoxLayout()
        self.header_title = QLabel("Weekly Report")
        self.header_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        left_header.addWidget(self.header_title)
        # Get header data
        report_range = self.settings.get('report_range', 'Monday–Friday')
        date_start, date_end = self.get_date_range()
        name = self.settings.get('name', '')
        agency = self.settings.get('agency', '')
        location = self.settings.get('location', '')
        self.header_info = QLabel(f"<b>Report Range:</b> {report_range} ({date_start} to {date_end})<br>"
                                  f"<b>Name:</b> {name}<br>"
                                  f"<b>Agency:</b> {agency}<br>"
                                  f"<b>Location:</b> {location}")
        self.header_info.setTextFormat(Qt.RichText)
        left_header.addWidget(self.header_info)
        header_layout.addLayout(left_header)
        # Logo on top right
        logo_path = self.settings.get('logo', '')
        if logo_path:
            try:
                from PySide6.QtGui import QPixmap
                logo_label = QLabel()
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(100, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    logo_label.setPixmap(pixmap)
                    logo_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
                    header_layout.addWidget(logo_label)
            except Exception:
                pass
        content_layout.addLayout(header_layout)

        # Scroll area for day panels
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        days_widget = QWidget()
        days_layout = QVBoxLayout()
        self.day_widgets = {}
        self.day_groups = {}
        additional_field = self.settings.get('additional_field', '').strip()
        additional_subfields = self.settings.get('additional_subfields', [])
        for day in self.current_days:
            group = QGroupBox(day)
            group.setCheckable(True)
            group.setChecked(True)
            day_layout = QVBoxLayout()
            # General notes
            general_input = QTextEdit()
            general_input.setPlaceholderText("General notes...")
            general_input.setTabChangesFocus(True)
            day_layout.addWidget(general_input)
            # Additional custom field (if set)
            additional_inputs = []
            if additional_field:
                additional_label = QLabel(f"{additional_field}")
                additional_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
                day_layout.addWidget(additional_label)
                for subfield in additional_subfields:
                    subfield_layout = QHBoxLayout()
                    subfield_label = QLabel(subfield+":")
                    subfield_input = QLineEdit()
                    subfield_input.setPlaceholderText(subfield)
                    subfield_layout.addWidget(subfield_label)
                    subfield_layout.addWidget(subfield_input)
                    day_layout.addLayout(subfield_layout)
                    additional_inputs.append((subfield, subfield_input))
            group.setLayout(day_layout)
            days_layout.addWidget(group)
            self.day_widgets[day] = {
                'general': general_input,
                'additional_inputs': additional_inputs
            }
            self.day_groups[day] = group
        days_widget.setLayout(days_layout)
        scroll.setWidget(days_widget)
        content_layout.addWidget(scroll)

        # Summary/comments section
        summary_layout = QVBoxLayout()
        summary_label = QLabel("Summary/Comments:")
        self.summary_input = QTextEdit()
        self.summary_input.setTabChangesFocus(True)
        summary_layout.addWidget(summary_label)
        summary_layout.addWidget(self.summary_input)
        content_layout.addLayout(summary_layout)

        # Theme toggle at bottom of content
        theme_toggle = QPushButton("Toggle Theme")
        theme_toggle.clicked.connect(self.toggle_theme)
        content_layout.addWidget(theme_toggle)

        content_widget.setLayout(content_layout)

        # QSplitter for collapsible sidebar
        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(self.sidebar_widget)
        splitter.addWidget(content_widget)
        splitter.setSizes([0, 1])  # Start with sidebar collapsed

        # Add toggle button and splitter to main layout
        main_layout.addWidget(sidebar_toggle_widget)
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Connect buttons
        save_button.clicked.connect(self.save_all_data)
        clear_button.clicked.connect(self.confirm_clear)
        report_button.clicked.connect(self.generate_report)
        settings_button.clicked.connect(self.open_settings)
        richtext_button.clicked.connect(self.export_rich_text)
        about_button.clicked.connect(self.show_about)
        self.splitter = splitter
        reset_button.clicked.connect(self.reset_application)

    def toggle_sidebar(self):
        if self.sidebar_widget.isVisible():
            self.sidebar_widget.hide()
            self.splitter.setSizes([0, 1])
        else:
            self.sidebar_widget.show()
            self.splitter.setSizes([170, 1])

    def get_current_days(self):
        report_range = self.settings.get('report_range', 'Monday–Friday')
        if report_range == "Thursday–Thursday":
            days = ["Thursday", "Friday", "Monday", "Tuesday", "Wednesday", "Thursday"]
            return [d for d in days if d not in ["Saturday", "Sunday"]]
        return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    def get_date_range(self):
        today = datetime.today()
        if hasattr(self, 'range_combo') and self.range_combo.currentIndex() == 1:
            # Thursday–Thursday
            # Find the most recent Thursday
            offset = (today.weekday() - 3) % 7
            start = today - timedelta(days=offset)
            end = start + timedelta(days=6)
            # Remove Saturday and Sunday from range
            days = []
            d = start
            while d <= end:
                if d.weekday() not in (5, 6):
                    days.append(d)
                d += timedelta(days=1)
            return days[0].strftime('%Y-%m-%d'), days[-1].strftime('%Y-%m-%d')
        else:
            # Monday–Friday
            offset = (today.weekday() - 0) % 7
            start = today - timedelta(days=offset)
            end = start + timedelta(days=4)
            return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')

    def save_all_data(self):
        data = {}
        for day, widgets in self.day_widgets.items():
            additional_data = {}
            if 'additional_inputs' in widgets:
                for subfield, input_widget in widgets['additional_inputs']:
                    additional_data[subfield] = input_widget.text()
            data[day] = {
                'general': widgets['general'].toPlainText(),
                'additional': additional_data
            }
        data['summary'] = self.summary_input.toPlainText()
        data['settings'] = self.settings
        data['report_range'] = self.settings.get('report_range', 'Monday–Friday')
        data['date_range'] = self.get_date_range()
        save_data(data)
        # Visual confirmation
        QMessageBox.information(self, "Saved", "Data saved successfully.")

    def load_saved_data(self):
        data = load_data()
        # Restore settings if present
        if 'settings' in data:
            self.settings = data['settings']
        for day, widgets in self.day_widgets.items():
            if day in data:
                widgets['general'].setPlainText(data[day].get('general', ''))
                if 'additional_inputs' in widgets and 'additional' in data[day]:
                    for subfield, input_widget in widgets['additional_inputs']:
                        input_widget.setText(data[day]['additional'].get(subfield, ''))
        self.summary_input.setPlainText(data.get('summary', ''))

    def generate_report(self):
        week_data = {}
        for day, widgets in self.day_widgets.items():
            additional_data = {}
            if 'additional_inputs' in widgets:
                for subfield, input_widget in widgets['additional_inputs']:
                    additional_data[subfield] = input_widget.text()
            week_data[day] = {
                'general': widgets['general'].toPlainText(),
                'additional': additional_data
            }
        summary = self.summary_input.toPlainText()
        all_data = load_data()
        settings = all_data.get('settings', {})
        report_range = self.settings.get('report_range', 'Monday–Friday')
        date_start, date_end = self.get_date_range()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", self.last_pdf_path or "WeeklyReport.pdf", "PDF Files (*.pdf)")
        if file_path:
            self.last_pdf_path = file_path
            additional_field = settings.get('additional_field', '').strip()
            additional_subfields = settings.get('additional_subfields', [])
            generate_pdf_report(file_path, settings, week_data, summary, report_range, date_start, date_end, additional_field, additional_subfields)
            QMessageBox.information(self, "Report Generated", f"PDF report saved to:\n{file_path}")

    def open_settings(self):
        settings = load_data().get('settings', {})
        dialog = SettingsDialog(self)
        dialog.set_settings(settings)
        if dialog.exec() == QDialog.Accepted:
            all_data = load_data()
            all_data['settings'] = dialog.get_settings()
            self.last_logo_path = dialog.logo_path_input.text()
            save_data(all_data)
            self.settings = all_data['settings']
            self.current_days = self.get_current_days()
            self.takeCentralWidget()
            self.init_ui()
            self.load_saved_data()

    def export_rich_text(self):
        # Gather data from UI
        week_data = {}
        for day, widgets in self.day_widgets.items():
            additional_data = {}
            if 'additional_inputs' in widgets:
                for subfield, input_widget in widgets['additional_inputs']:
                    additional_data[subfield] = input_widget.text()
            week_data[day] = {
                'general': widgets['general'].toPlainText(),
                'additional': additional_data
            }
        summary = self.summary_input.toPlainText()
        all_data = load_data()
        settings = all_data.get('settings', {})
        report_range = self.settings.get('report_range', 'Monday–Friday')
        date_start, date_end = self.get_date_range()
        additional_field = settings.get('additional_field', '').strip()
        additional_subfields = settings.get('additional_subfields', [])
        # Build HTML
        html = f"""
        <h2>Weekly Report</h2>
        <b>Report Range:</b> {report_range} ({date_start} to {date_end})<br>
        <b>Name:</b> {settings.get('name', '')}<br>
        <b>Agency:</b> {settings.get('agency', '')}<br>
        <b>Location:</b> {settings.get('location', '')}<br><br>
        <table border='1' cellpadding='4' cellspacing='0'>
        <tr>
            <th>Day</th>
            <th>General Notes</th>
            {''.join(f'<th>{sub}</th>' for sub in additional_subfields) if additional_field and additional_subfields else ''}
        </tr>
        """
        for day, daydata in week_data.items():
            general = daydata.get('general', '').replace('\n', '<br>')
            additional = daydata.get('additional', {})
            html += f"<tr><td>{day}</td><td>{general}</td>"
            if additional_field and additional_subfields:
                for sub in additional_subfields:
                    html += f"<td>{additional.get(sub, '')}</td>"
            html += "</tr>"
        html += "</table><br>"
        summary_html = summary.replace('\n', '<br>')
        html += f"<b>Summary/Comments:</b><br>{summary_html}"
        # Show in dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Rich Text Report (Copy for Email)")
        dlg.setMinimumSize(700, 500)
        layout = QVBoxLayout()
        textedit = QTextEdit()
        textedit.setReadOnly(False)
        textedit.setHtml(html)
        layout.addWidget(textedit)
        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(dlg.accept)
        layout.addWidget(btns)
        dlg.setLayout(layout)
        dlg.exec()

    def confirm_clear(self):
        reply = QMessageBox.question(self, 'Are you sure?',
                                     'Are you sure you want to clear all data?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.clear_all_data()

    def clear_all_data(self):
        for widgets in self.day_widgets.values():
            widgets['general'].clear()
            if 'additional_inputs' in widgets:
                for _, input_widget in widgets['additional_inputs']:
                    input_widget.clear()
        self.summary_input.clear()
        clear_data()
        QMessageBox.information(self, "Cleared", "All data has been cleared.")

    def toggle_theme(self):
        if self.theme == 'dark':
            self.theme = 'light'
            self.setStyleSheet(self.light_theme())
        else:
            self.theme = 'dark'
            self.setStyleSheet(self.dark_theme())

    def dark_theme(self):
        return """
        QWidget {
            background-color: #232629;
            color: #f0f0f0;
            font-size: 14px;
        }
        QLineEdit, QTextEdit, QComboBox {
            background-color: #31363b;
            color: #f0f0f0;
            border: 1px solid #444;
        }
        QPushButton {
            background-color: #3daee9;
            color: #fff;
            border-radius: 4px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #007acc;
        }
        QLabel {
            color: #f0f0f0;
        }
        """

    def light_theme(self):
        return """
        QWidget {
            background-color: #f0f0f0;
            color: #232629;
            font-size: 14px;
        }
        QLineEdit, QTextEdit, QComboBox {
            background-color: #fff;
            color: #232629;
            border: 1px solid #bbb;
        }
        QPushButton {
            background-color: #3daee9;
            color: #fff;
            border-radius: 4px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #007acc;
        }
        QLabel {
            color: #232629;
        }
        """

    def show_about(self):
        dlg = AboutDialog(self)
        dlg.exec()

    def reset_application(self):
        clear_data()
        import os
        settings_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'data.json')
        if os.path.exists(settings_path):
            try:
                os.remove(settings_path)
            except Exception:
                pass
        QMessageBox.information(self, "Reset", "Application has been reset. It will now restart.")
        import sys
        python = sys.executable
        os.execl(python, python, *sys.argv)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
