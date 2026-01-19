ROADMAP 7 HARI — CONTENT TREND RESEARCH TOOL
HARI 1 — Definisi output & setup dasar

Tujuan: tahu apa yang ingin kamu lihat setiap hari, lalu siapkan environment.

Yang harus diputuskan (WAJIB)

Platform: YouTube (utama), TikTok (menyusul)

Output minimal:

Judul

Views

Upload time

Channel

Thumbnail (URL + screenshot)

Timestamp pengambilan

Format output:

CSV

Folder screenshot

Task teknis

Install Python

Install Playwright (Python)

Download browser Playwright

Buat struktur folder proyek

Deliverable hari 1:

Project bisa dijalankan

Browser Playwright bisa terbuka

HARI 2 — Launcher browser & utilitas dasar

Tujuan: punya browser controller yang stabil dan bisa dipakai ulang.

Yang dibuat

Browser launcher:

Headful (ada UI)

SlowMo ringan

User agent default

Helper:

Delay natural

Scroll helper

Screenshot helper

Prinsip penting

Jangan paralel

Jangan headless dulu

Jangan login akun

Deliverable hari 2:

Script yang bisa:

Buka browser

Buka URL

Screenshot halaman

HARI 3 — YouTube search collector (inti manfaat)

Tujuan: ambil data tren dari hasil search YouTube.

Alur yang dibuat

Buka YouTube

Ketik keyword

Scroll 2–3 layar

Ambil 20–30 video teratas

Ambil:

Judul

Views

Upload time

Channel

Thumbnail URL

Catatan penting

Ambil apa yang terlihat di UI

Jangan klik video dulu

Fokus stabilitas selector

Deliverable hari 3:

CSV YouTube search trend

Data sudah bisa dianalisa

HARI 4 — Screenshot thumbnail & snapshot visual

Tujuan: visual trend (ini yang sering dilupakan tapi sangat berguna).

Yang ditambahkan

Screenshot:

Card video

Thumbnail saja (crop jika perlu)

Folder per tanggal:

screenshots/
  2026-01-19/
    youtube/
      keyword_x/

Manfaat nyata

Bandingkan gaya thumbnail

Lihat pola warna & teks

Referensi visual cepat

Deliverable hari 4:

CSV + folder screenshot rapi

Bisa browsing thumbnail tanpa buka YouTube

HARI 5 — TikTok collector (versi aman & ringan)

Tujuan: deteksi tren TikTok tanpa agresif.

Scope TikTok (JANGAN BERLEBIHAN)

Trending page ATAU search ringan

Scroll terbatas

Ambil:

Caption

View count

Creator

Snapshot visual

Prinsip TikTok

Lebih sensitif

Lebih visual

Jangan scraping dalam

Deliverable hari 5:

CSV TikTok trend

Screenshot feed TikTok

HARI 6 — Storage, history & perbandingan

Tujuan: bikin alat ini “cerdas” karena punya sejarah data.

Yang dibuat

SQLite sederhana

Simpan:

Date

Platform

Keyword

Views

Script perbandingan:

Hari ini vs kemarin

Deteksi video “naik cepat”

Insight mulai muncul

Topik yang berulang

Channel kecil tapi views besar

Jam upload dominan

Deliverable hari 6:

Database historis

Data tidak overwrite

HARI 7 — Automation & workflow harian

Tujuan: jadi alat kerja, bukan eksperimen.

Yang dilakukan

Config file:

Keyword

Platform

Limit video

Runner tunggal:

python runner.py


Jadwalkan:

Cron / Task Scheduler

Dokumentasi kecil:

Cara pakai

Cara baca hasil

Deliverable hari 7:

Sekali klik → riset jalan

Dipakai harian < 10 menit