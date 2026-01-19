import sys
import os
import shutil
import webbrowser
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                               QTableWidget, QTableWidgetItem, QHeaderView, 
                               QComboBox, QMessageBox, QAbstractItemView, QMenu, QFileDialog)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QColor, QPalette, QPixmap, QAction

# --- Import Module Project ---
try:
    from browser.launcher import launch_browser
    from collectors.youtube import collect_youtube_trends
    from collectors.tiktok import collect_tiktok_trends
    from storage.export_csv import export_to_csv
    from utils.time import utc_today
except ImportError as e:
    print(f"Error Import: {e}")
    sys.exit(1)

# --- Worker Thread (Backend Riset) ---
class ResearchWorker(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, platform, keyword):
        super().__init__()
        self.platform = platform
        self.keyword = keyword

    def run(self):
        try:
            # Gunakan headless=True agar browser tidak mengganggu (invisible)
            p, browser, page = launch_browser(headless=True)
            
            data = []
            if self.platform == "YouTube":
                data = collect_youtube_trends(page, self.keyword, max_videos=20)
                out_dir = "data/youtube"
            else:
                data = collect_tiktok_trends(page, self.keyword, max_videos=20)
                out_dir = "data/tiktok"

            # Simpan CSV otomatis
            if data:
                safe_keyword = self.keyword.replace(" ", "-")
                date = utc_today()
                export_to_csv(data, out_dir, f"{date}_{safe_keyword}.csv")

            browser.close()
            p.stop()
            self.finished.emit(data)

        except Exception as e:
            self.error.emit(str(e))

# --- Numeric Item untuk Sorting Angka ---
class NumericTableItem(QTableWidgetItem):
    def __lt__(self, other):
        try:
            val_self = float(self.text().replace(',', '').replace('.', ''))
            val_other = float(other.text().replace(',', '').replace('.', ''))
            return val_self < val_other
        except ValueError:
            return super().__lt__(other)

# --- Main App ---
class MamenProApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mamen Research Pro (With Visuals)")
        self.resize(1300, 800)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # UI Setup
        self.setup_controls()
        self.setup_table()
        
        # Status Bar
        self.lbl_status = QLabel("Siap mencari bahan konten...")
        self.lbl_status.setStyleSheet("color: #aaa; font-style: italic;")
        self.main_layout.addWidget(self.lbl_status)
        
        # Variabel untuk menyimpan data mentah (untuk akses path gambar saat klik kanan)
        self.current_data = []

    def setup_controls(self):
        layout = QHBoxLayout()
        
        lbl_title = QLabel("CONTENT RESEARCH")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: 900; color: #4facfe; letter-spacing: 1px;")
        
        self.input_keyword = QLineEdit()
        self.input_keyword.setPlaceholderText("Ketik Topik / Keyword...")
        self.input_keyword.setStyleSheet("""
            QLineEdit {
                padding: 12px; border-radius: 8px; border: 1px solid #444; 
                background-color: #2b2b2b; color: white; font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #4facfe; }
        """)
        self.input_keyword.returnPressed.connect(self.start_research)

        self.combo_platform = QComboBox()
        self.combo_platform.addItems(["YouTube", "TikTok"])
        self.combo_platform.setFixedWidth(130)
        self.combo_platform.setStyleSheet("""
            QComboBox {
                padding: 10px; border-radius: 8px; background-color: #333;
                color: white; border: 1px solid #444; font-weight: bold;
            }
        """)

        self.btn_run = QPushButton("🚀 CARI BAHAN")
        self.btn_run.setCursor(Qt.PointingHandCursor)
        self.btn_run.setStyleSheet("""
            QPushButton {
                background-color: #007bff; color: white; font-weight: bold;
                padding: 12px 25px; border-radius: 8px; border: none; font-size: 14px;
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
        
        # Definisikan Kolom: Visual (Thumbnail) sekarang di urutan pertama
        columns = ["Visual", "Judul Konten", "Views", "Channel/Creator", "Upload"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # Styling Tabel
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False) # Modern look
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setIconSize(QSize(160, 90)) # Ukuran icon default
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e; color: #ddd; font-size: 13px; border: none;
            }
            QHeaderView::section {
                background-color: #2d2d2d; color: white; padding: 12px; border: none; font-weight: bold; text-transform: uppercase;
            }
            QTableWidget::item { padding: 5px; border-bottom: 1px solid #333; }
            QTableWidget::item:selected { background-color: #2a3f5f; color: white; }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # Atur lebar awal kolom
        header.resizeSection(0, 180) # Visual (Lebar untuk thumbnail)
        header.resizeSection(1, 450) # Judul (Paling lebar)
        header.resizeSection(2, 120) # Views
        header.resizeSection(3, 180) # Channel
        header.setStretchLastSection(True)

        # Event: Double click buka link
        self.table.doubleClicked.connect(self.open_link)

        # Event: Klik Kanan (Context Menu)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        self.main_layout.addWidget(self.table)

    def start_research(self):
        keyword = self.input_keyword.text().strip()
        if not keyword:
            QMessageBox.warning(self, "Ups!", "Keyword belum diisi bos.")
            return

        self.btn_run.setEnabled(False)
        self.btn_run.setText("⏳ MENCARI...")
        self.input_keyword.setEnabled(False)
        self.lbl_status.setText(f"Sedang mengumpulkan data visual untuk: '{keyword}'...")
        self.table.setRowCount(0) 
        self.current_data = [] # Reset data

        self.worker = ResearchWorker(self.combo_platform.currentText(), keyword)
        self.worker.finished.connect(self.on_research_finished)
        self.worker.error.connect(self.on_research_error)
        self.worker.start()

    def on_research_finished(self, data):
        self.current_data = data # Simpan ke memori untuk akses context menu
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            # Tinggikan baris agar thumbnail muat (90px height)
            self.table.setRowHeight(row, 100)

            # 1. KOLOM VISUAL (THUMBNAIL)
            screenshot_path = item.get('screenshot')
            lbl_image = QLabel()
            lbl_image.setAlignment(Qt.AlignCenter)
            lbl_image.setStyleSheet("background-color: #000; border-radius: 4px;")
            
            if screenshot_path and os.path.exists(screenshot_path):
                pixmap = QPixmap(screenshot_path)
                # Scale gambar agar pas di kolom (KeepAspectRatio)
                scaled_pixmap = pixmap.scaled(160, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl_image.setPixmap(scaled_pixmap)
                lbl_image.setToolTip(f"Path: {screenshot_path}") # Tooltip lokasi file
            else:
                lbl_image.setText("No Image")
                lbl_image.setStyleSheet("color: #555; font-size: 10px; border: 1px dashed #444;")

            # Masukkan Widget QLabel ke dalam Cell Tabel
            self.table.setCellWidget(row, 0, lbl_image)

            # 2. JUDUL
            self.table.setItem(row, 1, QTableWidgetItem(item.get('title', '')))
            
            # 3. VIEWS (Numeric Sort)
            views_raw = item.get('views', 0) or 0
            views_display = f"{int(views_raw):,}" if views_raw else "0"
            self.table.setItem(row, 2, NumericTableItem(views_display))
            
            # 4. CHANNEL
            self.table.setItem(row, 3, QTableWidgetItem(item.get('channel', '')))
            
            # 5. UPLOAD TIME
            self.table.setItem(row, 4, QTableWidgetItem(str(item.get('upload_time', '-'))))

        self.table.setSortingEnabled(True)
        self.restore_ui_state()
        self.lbl_status.setText(f"✅ Selesai! {len(data)} konten ditemukan. Klik kanan untuk opsi download.")

    def on_research_error(self, error_msg):
        self.restore_ui_state()
        self.lbl_status.setText(f"❌ Error: {error_msg}")
        QMessageBox.critical(self, "Gagal", f"Terjadi kesalahan:\n{error_msg}")

    def restore_ui_state(self):
        self.btn_run.setEnabled(True)
        self.btn_run.setText("🚀 CARI BAHAN")
        self.input_keyword.setEnabled(True)

    def open_link(self):
        row = self.table.currentRow()
        if row >= 0:
            # Kita ambil URL dari self.current_data karena URL tidak ditampilkan di kolom visible
            # Pastikan urutan row tabel sinkron dengan data (jika sorting aktif, ini perlu hati-hati)
            # Karena sorting QTableWidget mengacak visual, kita ambil item Judul/URL tersembunyi.
            # CARA LEBIH AMAN:
            # Di sini kita ambil data dari item tersembunyi atau cari berdasarkan index visual
            pass
            # Sederhananya, jika user double click cell judul/channel, kita cari URL di data
            # Namun karena sorting GUI mengubah index, kita simpan URL di UserRole item JUDUL
            
    # --- FITUR KLIK KANAN (CONTEXT MENU) ---
    def show_context_menu(self, pos):
        # Cari baris yang diklik
        row = self.table.rowAt(pos.y())
        if row < 0: return

        # Mapping baris visual ke data asli agak rumit jika sudah disortir.
        # Strategi: Ambil path gambar dari Tooltip widget visual (trik praktis)
        widget = self.table.cellWidget(row, 0) # Kolom 0 adalah gambar
        path_gambar = widget.toolTip().replace("Path: ", "") if widget else ""

        # Ambil Judul
        item_judul = self.table.item(row, 1)
        judul = item_judul.text() if item_judul else "Unknown"

        menu = QMenu(self)
        
        # Action 1: Download / Simpan Gambar
        action_save = QAction("💾 Simpan Gambar Ke...", self)
        if not path_gambar or not os.path.exists(path_gambar):
            action_save.setEnabled(False)
            action_save.setText("💾 Gambar Tidak Tersedia")
        else:
            action_save.triggered.connect(lambda: self.download_image(path_gambar, judul))
        
        # Action 2: Buka Lokasi Folder
        action_open_folder = QAction("📂 Buka Folder Penyimpanan", self)
        if path_gambar and os.path.exists(path_gambar):
            action_open_folder.triggered.connect(lambda: self.open_folder(path_gambar))
        else:
            action_open_folder.setEnabled(False)

        # Action 3: Buka Link Video (Browser)
        action_open_web = QAction("🔗 Buka Video di Browser", self)
        # Mencari URL dari current_data yang cocok dengan Judul (simple lookup)
        url = next((d['url'] for d in self.current_data if d.get('title') == judul), None)
        if url:
            action_open_web.triggered.connect(lambda: webbrowser.open(url))
        else:
            action_open_web.setEnabled(False)

        menu.addAction(action_save)
        menu.addAction(action_open_folder)
        menu.addSeparator()
        menu.addAction(action_open_web)
        
        menu.exec(self.table.mapToGlobal(pos))

    def download_image(self, src_path, title):
        # Bersihkan nama file default
        clean_title = "".join(x for x in title if x.isalnum() or x in " -_")[:50]
        default_name = f"{clean_title}.jpg"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Simpan Thumbnail", 
            os.path.join(os.path.expanduser("~"), "Downloads", default_name),
            "Images (*.jpg *.png)"
        )

        if file_path:
            try:
                shutil.copy2(src_path, file_path)
                QMessageBox.information(self, "Sukses", f"Gambar berhasil disimpan di:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Gagal", f"Gagal menyimpan gambar: {e}")

    def open_folder(self, file_path):
        folder = os.path.dirname(file_path)
        try:
            os.startfile(folder) # Windows only
        except AttributeError:
            # Fallback untuk macOS/Linux
            import subprocess
            subprocess.call(["open", folder] if sys.platform == "darwin" else ["xdg-open", folder])

# --- Entry Point ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Dark Theme Palette
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    window = MamenProApp()
    window.show()
    sys.exit(app.exec())