# config.py

import os
from dotenv import load_dotenv

load_dotenv()  # load .env file

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY tidak ditemukan di file .env")

MAX_RESULTS = 20
REGION_CODE = "ID"
OUTPUT_DIR = "output"
