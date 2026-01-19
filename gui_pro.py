import sys
import webbrowser
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                               QTableWidget, QTableWidgetItem, QHeaderView, 
                               QComboBox, QMessageBox, QAbstractItemView)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QPalette

# --- Import Module Project (Pastikan struktur folder sesuai) ---
try:
    from browser.launcher import launch_browser
    from collectors.youtube import collect_youtube_trends
    from collectors.tiktok import collect_tiktok_trends
    from storage.export_csv import export_to_csv
    from utils.time import utc_today
except ImportError as e:
    print(f"Error Import: {e}")
    sys.exit(1)

# --- Worker Thread ---
class ResearchWorker(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, platform, keyword):
        super().__init__()
        self.platform = platform
        self.keyword = keyword

    def run(self):
        try:
            p, browser, page = launch_browser(headless=True)
            
            data = []
            if self.platform == "YouTube":
                data = collect_youtube_trends(page, self.keyword, max_videos=20)
                out_dir = "data/youtube"
            else:
                data = collect_tiktok_trends(page, self.keyword, max_videos=20)
                out_dir = "data/tiktok"

            if data:
                safe_keyword = self.keyword.replace(" ", "-")
                date = utc_today()
                export_to_csv(data, out_dir, f"{date}_{safe_keyword}.csv")

            browser.close()
            p.stop()
            self.finished.emit(data)

        except Exception as e:
            self.error.emit(str(e))

# --- Numeric Item ---
class NumericTableItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            return float(self.text().replace(',', '').replace('.', '')) < float(other.text().replace(',', '').replace('.', ''))
        except ValueError:
            return super().__lt__(other)

# --- Main App ---
class MamenProApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mamen Research PLAYWRIGHT GUI")
        self.resize(1200, 700)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # 1. Controls
        self.setup_controls()

        # 2. Table
        self.setup_table()

        # 3. Status
        self.lbl_status = QLabel("Siap menunggu perintah.")
        self.lbl_status.setStyleSheet("color: #888; font-size: 12px; margin-top: 5px;")
        self.main_layout.addWidget(self.lbl_status)

    def setup_controls(self):
        layout = QHBoxLayout()
        
        lbl_title = QLabel("TREND RESEARCH")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4facfe;")
        
        self.input_keyword = QLineEdit()
        self.input_keyword.setPlaceholderText("Masukkan Keyword...")
        self.input_keyword.setStyleSheet("""
            QLineEdit {
                padding: 10px; border-radius: 5px; border: 1px solid #444; 
                background-color: #2b2b2b; color: white; font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #4facfe; }
        """)
        self.input_keyword.returnPressed.connect(self.start_research)

        self.combo_platform = QComboBox()
        self.combo_platform.addItems(["YouTube", "TikTok"])
        self.combo_platform.setFixedWidth(120)
        self.combo_platform.setStyleSheet("""
            QComboBox {
                padding: 8px; border-radius: 5px; background-color: #2b2b2b;
                color: white; border: 1px solid #444; font-size: 13px;
            }
        """)

        self.btn_run = QPushButton("🚀 MULAI RISET")
        self.btn_run.setCursor(Qt.PointingHandCursor)
        self.btn_run.setStyleSheet("""
            QPushButton {
                background-color: #007bff; color: white; font-weight: bold;
                padding: 10px 20px; border-radius: 5px; border: none; font-size: 13px;
            }
            QPushButton:hover { background-color: #0056b3; }
            QPushButton:disabled { background-color: #444; color: #888; }
        """)
        self.btn_run.clicked.connect(self.start_research)

        layout.addWidget(lbl_title)
        layout.addStretch()
        layout.addWidget(self.input_keyword, 1)
        layout.addWidget(self.combo_platform)
        layout.addWidget(self.btn_run)
        
        self.main_layout.addLayout(layout)

    def setup_table(self):
        self.table = QTableWidget()
        # Columns: 0=Title, 1=Views, 2=Channel, 3=Date, 4=URL
        columns = ["Judul Video", "Views", "Channel", "Upload", "URL"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSortingEnabled(True) 
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e; gridline-color: #333; color: #ddd; font-size: 13px; border: none;
            }
            QHeaderView::section {
                background-color: #2d2d2d; color: white; padding: 8px; border: none; font-weight: bold;
            }
            QTableWidget::item { padding: 5px; }
            QTableWidget::item:selected { background-color: #007bff; color: white; }
        """)

        # --- LOGIKA RESIZE BARU ---
        header = self.table.horizontalHeader()
        
        # Set SEMUA kolom ke mode "Interactive" agar user bisa geser-geser manual
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # Set lebar default awal (sebelum ada data) agar tidak terlihat berantakan
        header.resizeSection(0, 400) # Judul agak lebar
        header.resizeSection(1, 100)
        header.resizeSection(2, 150)
        header.resizeSection(3, 100)
        header.resizeSection(4, 300) # URL agak lebar
        
        # Supaya kolom terakhir (URL) tidak menyisakan ruang kosong jelek di kanan,
        # kita bisa set stretchLastSection(True). 
        # Tapi user minta "tiap kolom bisa digeser", stretchLastSection kadang mengunci kolom terakhir.
        # Jadi kita biarkan False (default), atau set True jika ingin URL mentok kanan.
        header.setStretchLastSection(True) 

        self.table.doubleClicked.connect(self.open_link)
        self.main_layout.addWidget(self.table)

    def start_research(self):
        keyword = self.input_keyword.text().strip()
        if not keyword:
            QMessageBox.warning(self, "Peringatan", "Silakan masukkan keyword terlebih dahulu!")
            return

        self.btn_run.setEnabled(False)
        self.btn_run.setText("⏳ SEDANG BEKERJA...")
        self.input_keyword.setEnabled(False)
        self.lbl_status.setText(f"Sedang mengambil data untuk '{keyword}'... Mohon tunggu.")
        self.table.setRowCount(0) 

        self.worker = ResearchWorker(self.combo_platform.currentText(), keyword)
        self.worker.finished.connect(self.on_research_finished)
        self.worker.error.connect(self.on_research_error)
        self.worker.start()

    def on_research_finished(self, data):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            # Title
            self.table.setItem(row, 0, QTableWidgetItem(item.get('title', '')))
            
            # Views
            views_raw = item.get('views', 0) or 0
            views_display = f"{int(views_raw):,}" if views_raw else "0"
            view_item = NumericTableItem(views_display)
            self.table.setItem(row, 1, view_item)
            
            # Channel
            self.table.setItem(row, 2, QTableWidgetItem(item.get('channel', '')))
            
            # Upload
            self.table.setItem(row, 3, QTableWidgetItem(str(item.get('upload_time', '-'))))
            
            # URL
            self.table.setItem(row, 4, QTableWidgetItem(item.get('url', '')))

        # --- TERAPKAN LOGIKA LEBAR KOLOM SESUAI REQUEST ---
        # 1. Resize kolom Views(1), Channel(2), Upload(3) agar pas dengan teks konten
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)
        self.table.resizeColumnToContents(3)
        
        # 2. Judul (0) dan URL (4) kita beri lebar manual yang cukup luas
        #    Kita tidak pakai resizeToContents untuk ini karena judul panjang bisa memakan layar.
        #    Kita hitung sisa ruang secara kasar atau set nilai fix yang bagus.
        
        total_width = self.table.viewport().width()
        used_width = self.table.columnWidth(1) + self.table.columnWidth(2) + self.table.columnWidth(3)
        remaining = total_width - used_width - 20 # sisa ruang (minus padding dikit)
        
        if remaining > 200:
            # Bagi sisa ruang: 60% untuk Judul, 40% untuk URL
            self.table.setColumnWidth(0, int(remaining * 0.6)) 
            # URL otomatis ngisi sisa karena StretchLastSection, atau kita set juga:
            self.table.setColumnWidth(4, int(remaining * 0.4))
        else:
            # Fallback jika layar sempit
            self.table.setColumnWidth(0, 300)
            self.table.setColumnWidth(4, 200)

        self.table.setSortingEnabled(True)
        self.btn_run.setEnabled(True)
        self.btn_run.setText("🚀 MULAI RISET")
        self.input_keyword.setEnabled(True)
        self.lbl_status.setText(f"✅ Selesai. Ditemukan {len(data)} hasil.")

    def on_research_error(self, error_msg):
        self.btn_run.setEnabled(True)
        self.btn_run.setText("🚀 MULAI RISET")
        self.input_keyword.setEnabled(True)
        self.lbl_status.setText(f"❌ Error: {error_msg}")
        QMessageBox.critical(self, "Error", f"Terjadi kesalahan:\n{error_msg}")

    def open_link(self):
        row = self.table.currentRow()
        if row >= 0:
            url_item = self.table.item(row, 4)
            if url_item:
                url = url_item.text()
                if url.startswith("http"):
                    webbrowser.open(url)
                    self.lbl_status.setText(f"🔗 Membuka: {url}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    window = MamenProApp()
    window.show()
    sys.exit(app.exec())