"""
Logika inti konversi dokumen.

PDF -> Word ditangani oleh pustaka `pdf2docx` (murni Python, stabil untuk
tata letak umum: teks, tabel, gambar).

Word -> PDF TIDAK bisa dilakukan oleh `python-docx` (pustaka itu hanya
membaca/menulis struktur .docx, tidak punya mesin render PDF). Cara yang
stabil di server Linux adalah memanggil LibreOffice headless sebagai
subprocess. Ini butuh LibreOffice terpasang di sistem (lihat README).
"""
import shutil
import subprocess
from pathlib import Path

from config import LIBREOFFICE_TIMEOUT_SECONDS


class ConversionError(Exception):
    """Dilempar ketika konversi gagal karena alasan yang bisa dijelaskan ke user."""
    pass


def convert_pdf_to_docx(pdf_path: Path, docx_path: Path) -> None:
    """Konversi file PDF menjadi file DOCX menggunakan pdf2docx."""
    try:
        from pdf2docx import Converter
    except ImportError as e:
        raise ConversionError(
            "Modul pdf2docx belum terpasang di server. Jalankan: pip install -r requirements.txt"
        ) from e

    try:
        cv = Converter(str(pdf_path))
        cv.convert(str(docx_path))
        cv.close()
    except Exception as e:
        raise ConversionError(f"Gagal mengonversi PDF ke Word: {e}") from e

    if not docx_path.exists() or docx_path.stat().st_size == 0:
        raise ConversionError("Konversi menghasilkan file kosong. File PDF mungkin rusak atau terenkripsi.")


def convert_docx_to_pdf(docx_path: Path, output_dir: Path) -> Path:
    """
    Konversi file DOCX menjadi PDF memanggil LibreOffice headless.
    Mengembalikan path file PDF hasil konversi.
    """
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise ConversionError(
            "LibreOffice tidak ditemukan di server (binary 'soffice'/'libreoffice'). "
            "Ini adalah dependensi sistem, bukan pustaka pip — install dengan: "
            "sudo apt-get install libreoffice --no-install-recommends"
        )

    try:
        result = subprocess.run(
            [
                soffice,
                "--headless",
                "--norestore",
                "--convert-to", "pdf",
                "--outdir", str(output_dir),
                str(docx_path),
            ],
            capture_output=True,
            text=True,
            timeout=LIBREOFFICE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as e:
        raise ConversionError("Konversi timeout. File terlalu besar atau kompleks untuk diproses.") from e

    if result.returncode != 0:
        raise ConversionError(f"LibreOffice gagal mengonversi file: {result.stderr.strip() or 'unknown error'}")

    expected_pdf = output_dir / (docx_path.stem + ".pdf")
    if not expected_pdf.exists() or expected_pdf.stat().st_size == 0:
        raise ConversionError("Konversi tidak menghasilkan file PDF yang valid. File Word mungkin rusak.")

    return expected_pdf
