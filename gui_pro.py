import sys
import os
import random
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                               QListWidget, QListWidgetItem, QComboBox, QFrame,
                               QScrollArea, QSplitter, QMessageBox, QCheckBox)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QColor, QPalette, QPixmap, QFont, QClipboard, QIcon

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

# --- CONFIG & STYLING ---
STYLE_SHEET = """
    QMainWindow { background-color: #121212; color: #E0E0E0; }
    
    /* Top Bar */
    QFrame#TopBar { background-color: #1E1E1E; border-bottom: 1px solid #333; padding: 10px; }
    QLabel#Logo { font-size: 18px; font-weight: bold; color: #4facfe; }
    
    /* Controls */
    QComboBox { 
        background-color: #2C2C2C; color: white; padding: 8px; border-radius: 6px; border: 1px solid #444; min-width: 100px;
    }
    QPushButton#BtnRun {
        background-color: #4facfe; color: black; font-weight: bold; border-radius: 6px; padding: 8px 20px;
    }
    QPushButton#BtnRun:hover { background-color: #00f2fe; }
    QPushButton#BtnRun:disabled { background-color: #444; color: #888; }

    /* Trend Card in List */
    QWidget#TrendCard { background-color: #1E1E1E; border-radius: 8px; border: 1px solid #333; }
    QWidget#TrendCard:hover { background-color: #252525; border: 1px solid #4facfe; }
    QLabel#Rank { font-size: 24px; font-weight: bold; color: #666; }
    QLabel#Keyword { font-size: 16px; font-weight: bold; color: white; }
    QLabel#Meta { font-size: 12px; color: #AAA; }
    QLabel#ScoreHot { background-color: #FF4B4B; color: white; border-radius: 4px; padding: 2px 6px; font-size: 10px; font-weight: bold; }
    QLabel#ScoreWarm { background-color: #FFB74D; color: black; border-radius: 4px; padding: 2px 6px; font-size: 10px; font-weight: bold; }

    /* Detail Panel */
    QScrollArea { border: none; background-color: #121212; }
    QWidget#DetailContent { background-color: #121212; }
    
    /* Insight Sections */
    QFrame#Section { background-color: #1E1E1E; border-radius: 8px; padding: 15px; margin-bottom: 10px; border: 1px solid #333; }
    QLabel#SectionTitle { color: #4facfe; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    QLabel#MainValue { font-size: 14px; color: white; line-height: 1.4; }
    QLabel#Highlight { color: #FFD700; font-weight: bold; }
    
    QPushButton#ActionBtn {
        background-color: #333; color: white; border: 1px solid #555; border-radius: 4px; padding: 5px 10px; font-size: 11px;
    }
    QPushButton#ActionBtn:hover { background-color: #444; border-color: #777; }
"""

# --- WORKER THREAD (BACKEND) ---
class ResearchWorker(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, platform, keyword):
        super().__init__()
        self.platform = platform
        self.keyword = keyword

    def run(self):
        try:
            # Headless Mode AKTIF agar tidak mengganggu
            p, browser, page = launch_browser(headless=True)
            
            data = []
            if self.platform == "YouTube Shorts" or self.platform == "YouTube Long":
                # Logic: Collector sama, nanti filter durasi di GUI simulation
                data = collect_youtube_trends(page, self.keyword, max_videos=15)
                out_dir = "data/youtube"
            else:
                data = collect_tiktok_trends(page, self.keyword, max_videos=15)
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

# --- WIDGET: TREND CARD (ITEM LIST) ---
class TrendCardWidget(QWidget):
    def __init__(self, rank, data):
        super().__init__()
        self.setObjectName("TrendCard")
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 1. Rank
        lbl_rank = QLabel(f"#{rank}")
        lbl_rank.setObjectName("Rank")
        lbl_rank.setFixedWidth(40)
        
        # 2. Info Tengah
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        title_text = data.get('title', 'Unknown Topic')
        # Potong judul jika terlalu panjang
        if len(title_text) > 50: title_text = title_text[:50] + "..."
        
        lbl_keyword = QLabel(title_text)
        lbl_keyword.setObjectName("Keyword")
        lbl_keyword.setWordWrap(True)

        # Simulasi Data Growth & Format (Karena scraper belum ambil ini)
        views = data.get('views', 0) or 0
        growth_pct = random.randint(120, 500) # Dummy logic untuk demo
        duration_mock = f"{random.randint(15, 59)}s" 
        
        lbl_meta = QLabel(f"🎬 Shorts | ⏱ {duration_mock} | ⬆️ +{growth_pct}% / 24 jam")
        lbl_meta.setObjectName("Meta")
        
        info_layout.addWidget(lbl_keyword)
        info_layout.addWidget(lbl_meta)

        # 3. Score (Kanan)
        score_layout = QVBoxLayout()
        trend_score = random.randint(40, 99) # Mock score
        
        lbl_badge = QLabel("HOT" if trend_score > 75 else "WARM")
        lbl_badge.setObjectName("ScoreHot" if trend_score > 75 else "ScoreWarm")
        lbl_badge.setAlignment(Qt.AlignCenter)
        
        lbl_score_val = QLabel(f"{trend_score}")
        lbl_score_val.setStyleSheet("color: #666; font-size: 18px; font-weight: bold;")
        lbl_score_val.setAlignment(Qt.AlignCenter)

        score_layout.addWidget(lbl_badge)
        score_layout.addWidget(lbl_score_val)

        # Assembly
        layout.addWidget(lbl_rank)
        layout.addLayout(info_layout, stretch=1)
        layout.addLayout(score_layout)
        
        self.setLayout(layout)

# --- MAIN GUI ---
class MamenDecisionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mamen Content Decision System")
        self.resize(1280, 800)
        self.setStyleSheet(STYLE_SHEET)
        
        # Simpan data
        self.current_data = []

        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. TOP BAR
        self.setup_top_bar(main_layout)

        # 2. SPLITTER (LIST vs DETAIL)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background-color: #333; }")

        # LEFT: Trend List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("QListWidget { background-color: #121212; border: none; padding: 10px; }")
        self.list_widget.setSpacing(10)
        self.list_widget.itemClicked.connect(self.load_detail)
        
        # RIGHT: Detail Panel (Scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.detail_container = QWidget()
        self.detail_container.setObjectName("DetailContent")
        self.detail_layout = QVBoxLayout(self.detail_container)
        self.detail_layout.setContentsMargins(20, 20, 20, 20)
        self.detail_layout.setSpacing(15)
        
        # Placeholder Content untuk Detail
        self.lbl_placeholder = QLabel("👈 Pilih Tren di kiri untuk analisa & strategi.")
        self.lbl_placeholder.setStyleSheet("color: #555; font-size: 14px; margin-top: 50px;")
        self.lbl_placeholder.setAlignment(Qt.AlignCenter)
        self.detail_layout.addWidget(self.lbl_placeholder)

        scroll.setWidget(self.detail_container)

        splitter.addWidget(self.list_widget)
        splitter.addWidget(scroll)
        splitter.setSizes([450, 830]) # Rasio awal
        splitter.setCollapsible(0, False)
        
        main_layout.addWidget(splitter)

    def setup_top_bar(self, parent_layout):
        bar = QFrame()
        bar.setObjectName("TopBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 5, 10, 5)

        lbl_logo = QLabel("MAMEN DECISION")
        lbl_logo.setObjectName("Logo")

        # Inputs
        self.combo_platform = QComboBox()
        self.combo_platform.addItems(["YouTube Shorts", "YouTube Long", "TikTok"])
        
        self.combo_niche = QComboBox()
        self.combo_niche.addItems(["General", "Music", "Gaming", "Education", "Storytelling"])

        # Kita pakai text input untuk keyword sebagai 'Topic Starter'
        # Karena scraper butuh input awal.
        self.input_topic = QLineEdit()
        self.input_topic.setPlaceholderText("Topik dasar (cth: ai tools)")
        self.input_topic.setStyleSheet("background-color: #2C2C2C; padding: 8px; border: 1px solid #444; color: white; border-radius: 6px;")

        self.btn_run = QPushButton("⚡ ANALISA TREND")
        self.btn_run.setObjectName("BtnRun")
        self.btn_run.setCursor(Qt.PointingHandCursor)
        self.btn_run.clicked.connect(self.start_analysis)
        
        # Status Label Kecil
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: #888; margin-left: 10px;")

        layout.addWidget(lbl_logo)
        layout.addStretch()
        layout.addWidget(self.combo_platform)
        layout.addWidget(self.combo_niche)
        layout.addWidget(self.input_topic)
        layout.addWidget(self.btn_run)
        
        parent_layout.addWidget(bar)

    def start_analysis(self):
        topic = self.input_topic.text().strip()
        if not topic:
            QMessageBox.warning(self, "Input Kosong", "Masukkan topik dasar dulu.")
            return

        self.btn_run.setEnabled(False)
        self.btn_run.setText("⏳ SCOUTING...")
        self.list_widget.clear()
        self.clear_detail_panel()
        self.detail_layout.addWidget(self.lbl_placeholder)
        self.lbl_status.setText(f"Mencari data untuk '{topic}'...")

        # Jalankan Thread
        self.worker = ResearchWorker(self.combo_platform.currentText(), topic)
        self.worker.finished.connect(self.on_data_ready)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_data_ready(self, data):
        self.current_data = data
        self.btn_run.setEnabled(True)
        self.btn_run.setText("⚡ ANALISA TREND")
        self.lbl_status.setText(f"Selesai. {len(data)} tren ditemukan.")

        if not data:
            QMessageBox.information(self, "Kosong", "Tidak ditemukan data baru.")
            return

        # Populate List Widget
        for i, item in enumerate(data, start=1):
            list_item = QListWidgetItem(self.list_widget)
            card = TrendCardWidget(i, item)
            
            # Sesuaikan tinggi card
            list_item.setSizeHint(card.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, card)

    def on_error(self, msg):
        self.btn_run.setEnabled(True)
        self.btn_run.setText("⚡ ANALISA TREND")
        QMessageBox.critical(self, "Error", msg)

    def clear_detail_panel(self):
        # Hapus semua widget di detail panel
        while self.detail_layout.count():
            child = self.detail_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def load_detail(self, item):
        # Ambil data dari index list
        idx = self.list_widget.row(item)
        data = self.current_data[idx]
        
        self.clear_detail_panel()
        
        # --- LOGIC GENERATOR INSIGHT (MOCKUP CERDAS) ---
        # Karena scraper belum punya AI, kita gunakan logika berbasis keyword/data
        title = data.get('title', '')
        views = data.get('views', 0)
        channel = data.get('channel', 'Creator')
        
        # 1. SECTION A: INSIGHT CEPAT
        sec_a = QFrame()
        sec_a.setObjectName("Section")
        lay_a = QVBoxLayout(sec_a)
        
        hot_status = "HOT 🔥" if views and views > 100000 else "RISING 🚀"
        lay_a.addWidget(QLabel("STATUS TREN"))
        lbl_status = QLabel(f"{hot_status} • Umur: < 24 Jam • Kompetisi: Sedang")
        lbl_status.setObjectName("MainValue")
        lay_a.addWidget(lbl_status)
        self.detail_layout.addWidget(sec_a)

        # 2. SECTION B: FORMAT REKOMENDASI (Actionable)
        sec_b = QFrame()
        sec_b.setObjectName("Section")
        lay_b = QVBoxLayout(sec_b)
        
        lay_b.addWidget(QLabel("STRATEGI EKSEKUSI"))
        
        # Logika Hook Sederhana
        hook_idea = f"Stop scroll! Lihat kenapa {channel} bisa dapet {views} views..."
        if "cara" in title.lower():
            hook_idea = "JANGAN SALAH LAGI! Ini cara yang bener..."
        elif "vs" in title.lower():
            hook_idea = "HASILNYA DILUAR DUGAAN! Ternyata..."
            
        content = (
            f"<b>Format:</b> Shorts / Reels (9:16)\n"
            f"<b>Durasi Ideal:</b> 25 – 35 detik\n"
            f"<b>Hook (3s Pertama):</b> <span style='color:#FFD700'>\"{hook_idea}\"</span>\n"
            f"<b>Structure:</b> Hook -> Masalah -> Solusi Cepat -> Call to Action"
        )
        lbl_exec = QLabel(content)
        lbl_exec.setObjectName("MainValue")
        lbl_exec.setWordWrap(True)
        lay_b.addWidget(lbl_exec)
        self.detail_layout.addWidget(sec_b)

        # 3. SECTION C: POLA JUDUL (ATM)
        sec_c = QFrame()
        sec_c.setObjectName("Section")
        lay_c = QVBoxLayout(sec_c)
        lay_c.addWidget(QLabel("TEMPLATE JUDUL (ATM)"))
        
        clean_title = title.split('|')[0].strip()[:20] # Ambil kata kunci
        templates = [
            f"RAHASIA {clean_title} YANG JARANG ORANG TAU",
            f"KENAPA {clean_title} BISA SEKEREN INI?",
            f"JANGAN COBA {clean_title} SEBELUM NONTON INI"
        ]
        
        for t in templates:
            lbl_t = QLabel(f"• {t}")
            lbl_t.setStyleSheet("color: #E0E0E0; margin-bottom: 2px;")
            lay_c.addWidget(lbl_t)
            
        btn_copy = QPushButton("📋 Copy Template")
        btn_copy.setObjectName("ActionBtn")
        btn_copy.clicked.connect(lambda: QApplication.clipboard().setText("\n".join(templates)))
        lay_c.addWidget(btn_copy)
        
        self.detail_layout.addWidget(sec_c)

        # 4. SECTION D: THUMBNAIL GUIDE (Visual Rule)
        sec_d = QFrame()
        sec_d.setObjectName("Section")
        lay_d = QVBoxLayout(sec_d)
        lay_d.addWidget(QLabel("VISUAL THUMBNAIL RULE"))
        
        # Tampilkan Gambar Asli jika ada
        img_path = data.get('screenshot')
        if img_path and os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(300, 169, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl_img = QLabel()
            lbl_img.setPixmap(pix)
            lbl_img.setStyleSheet("border: 1px solid #444; margin-bottom: 10px;")
            lay_d.addWidget(lbl_img)
        
        rule_text = (
            "• <b>Ekspresi:</b> Wajah Zoom-in (Kaget/Serius)\n"
            "• <b>Teks:</b> Maksimal 3 kata, Warna Kuning/Merah\n"
            "• <b>Kontras:</b> High Contrast, Background Gelap"
        )
        lbl_rule = QLabel(rule_text)
        lbl_rule.setObjectName("MainValue")
        lay_d.addWidget(lbl_rule)
        self.detail_layout.addWidget(sec_d)

        # 5. SECTION E: TIMING
        sec_e = QFrame()
        sec_e.setObjectName("Section")
        lay_e = QVBoxLayout(sec_e)
        lay_e.addWidget(QLabel("WAKTU UPLOAD TERBAIK"))
        lbl_time = QLabel("⏰ 18:30 - 20:00 WIB (Peak Traffic)")
        lbl_time.setObjectName("MainValue")
        lay_e.addWidget(lbl_time)
        self.detail_layout.addWidget(sec_e)
        
        self.detail_layout.addStretch()

# --- ENTRY POINT ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set Fusion Style (Dark Base)
    app.setStyle("Fusion")
    
    window = MamenDecisionApp()
    window.show()
    sys.exit(app.exec())