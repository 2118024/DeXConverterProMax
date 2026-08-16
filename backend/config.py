"""
Konfigurasi terpusat untuk aplikasi konversi dokumen.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Direktori penyimpanan file sementara (upload & hasil konversi)
TEMP_DIR = BASE_DIR / "temp_files"
TEMP_DIR.mkdir(exist_ok=True)

# Batas ukuran file maksimal (dalam bytes) -> 10 MB
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

# Ekstensi yang diizinkan per mode konversi
ALLOWED_EXTENSIONS = {
    "pdf2word": {".pdf"},
    "word2pdf": {".docx"},
}

# Umur maksimal file sementara sebelum dihapus otomatis oleh sweeper (menit)
FILE_LIFETIME_MINUTES = int(os.environ.get("FILE_LIFETIME_MINUTES", 15))

# Interval pengecekan sweeper (detik)
SWEEP_INTERVAL_SECONDS = 60

# Timeout proses konversi LibreOffice (detik)
LIBREOFFICE_TIMEOUT_SECONDS = 120
