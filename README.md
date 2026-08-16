# Konversi PDF ⇄ Word

Aplikasi web full-stack untuk konversi dokumen PDF → Word dan Word → PDF.

## Struktur folder

```
pdf-word-converter/
├── backend/
│   ├── main.py            # FastAPI app + endpoint API + serve frontend
│   ├── converters.py      # Logika konversi (pdf2docx, LibreOffice)
│   ├── cleanup.py         # Sweeper penghapus file sementara otomatis
│   ├── config.py          # Konfigurasi (batas ukuran, ekstensi, dll)
│   ├── requirements.txt
│   └── temp_files/        # Dibuat otomatis saat runtime — JANGAN commit isinya
└── frontend/
    ├── index.html
    └── app.js
```

## Dependensi

### 1. Python packages
```bash
cd backend
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. LibreOffice (WAJIB untuk Word → PDF)

`python-docx` **tidak bisa** menghasilkan PDF — itu bukan bug, itu batas pustaka.
Konversi Word → PDF di server Linux memanggil LibreOffice headless via subprocess.
PDF → Word (via `pdf2docx`) TIDAK butuh LibreOffice, murni Python.

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install libreoffice --no-install-recommends
```

**macOS:**
```bash
brew install --cask libreoffice
```

**Windows:** unduh installer dari [libreoffice.org](https://www.libreoffice.org/download/) lalu
pastikan folder instalasi (mis. `C:\Program Files\LibreOffice\program`) ada di PATH sistem.

Cek instalasi:
```bash
soffice --version
```

Jika Anda hanya butuh PDF → Word, langkah ini boleh dilewati — endpoint Word → PDF
akan mengembalikan error yang jelas ("LibreOffice tidak ditemukan") alih-alih crash.

## Menjalankan aplikasi

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Buka **http://localhost:8000** di browser. Frontend disajikan langsung oleh FastAPI
dari folder `frontend/` — tidak perlu server terpisah.

## Cara kerja privasi & pembersihan file

1. File diunggah → disimpan di `backend/temp_files/` dengan nama acak (UUID).
2. Setelah konversi selesai, file input asli langsung dihapus.
3. File hasil dihapus **segera setelah diunduh** oleh user.
4. Fallback: thread sweeper berjalan tiap 60 detik, menghapus paksa file mana pun
   di `temp_files/` yang berumur lebih dari `FILE_LIFETIME_MINUTES` (default 15 menit) —
   ini menangani kasus user menutup tab sebelum sempat mengunduh.

Atur umur maksimal via environment variable:
```bash
FILE_LIFETIME_MINUTES=5 uvicorn main:app --port 8000
```

## Endpoint API

| Method | Path                     | Deskripsi                                      |
|--------|---------------------------|-------------------------------------------------|
| POST   | `/api/convert`            | Upload file (`multipart/form-data`: `mode`, `file`) → `{job_id, filename}` |
| GET    | `/api/download/{job_id}`  | Unduh hasil konversi, file dihapus setelahnya    |
| GET    | `/api/health`             | Cek status server + ketersediaan LibreOffice     |

`mode` bernilai `"pdf2word"` atau `"word2pdf"`.

## Batasan yang perlu diketahui (bukan disembunyikan)

- **Ukuran file maksimal 10 MB** — bisa diubah di `backend/config.py` (`MAX_FILE_SIZE_BYTES`),
  tapi ingat: LibreOffice headless punya batas memori/waktu praktis untuk file sangat besar.
- **Progress bar bersifat estimasi**, bukan pengukuran real-time dari server. Upload asli
  diukur (via `XMLHttpRequest.upload.progress`), tapi fase "memproses di server" disimulasikan
  karena endpoint ini sinkron. Untuk progress server yang benar-benar akurat, dibutuhkan
  job queue (Celery/RQ + Redis) dan WebSocket — di luar scope aplikasi single-file ini.
- **In-memory job registry**: cocok untuk single-process/demo. Jika Anda deploy dengan
  banyak worker (`uvicorn --workers N`) atau di belakang load balancer, registry ini
  tidak dibagi antar proses — gunakan Redis sebagai gantinya untuk produksi.
- **Tata letak dokumen kompleks** (tabel bersarang, font langka, WordArt) bisa berubah
  sedikit saat dikonversi — ini batas wajar konversi otomatis, bukan cacat implementasi.

## Deployment produksi (ringkas)

- Jalankan di belakang reverse proxy (nginx/Caddy) dengan HTTPS.
- Ganti `allow_origins=["*"]` di `main.py` dengan domain frontend Anda.
- Pertimbangkan rate limiting per-IP (mis. `slowapi`) untuk mencegah abuse endpoint upload.
- Jalankan LibreOffice dalam container terisolasi/sandbox — ia memproses file yang tidak
  dipercaya (untrusted input), jadi perlakukan sebagai permukaan serangan.
