"""
Mekanisme pembersihan otomatis file sementara.

Dua lapis proteksi privasi/storage:
1. Immediate delete: file dihapus segera setelah berhasil diunduh
   (dipicu dari endpoint download via BackgroundTask di main.py).
2. Sweeper thread: jaring pengaman untuk file yang TIDAK PERNAH diunduh
   (user menutup tab, koneksi putus, dll) — dihapus paksa setelah
   FILE_LIFETIME_MINUTES.
"""
import logging
import threading
import time
from pathlib import Path

from config import TEMP_DIR, FILE_LIFETIME_MINUTES, SWEEP_INTERVAL_SECONDS

logger = logging.getLogger("cleanup")

_stop_event = threading.Event()


def _sweep_once() -> None:
    cutoff = time.time() - (FILE_LIFETIME_MINUTES * 60)
    for path in TEMP_DIR.glob("*"):
        try:
            if path.is_file() and path.stat().st_mtime < cutoff:
                path.unlink(missing_ok=True)
                logger.info("Sweeper menghapus file kedaluwarsa: %s", path.name)
        except OSError as e:
            logger.warning("Gagal menghapus %s: %s", path.name, e)


def _sweep_loop() -> None:
    while not _stop_event.is_set():
        _sweep_once()
        _stop_event.wait(SWEEP_INTERVAL_SECONDS)


def start_cleanup_thread() -> threading.Thread:
    thread = threading.Thread(target=_sweep_loop, name="temp-file-sweeper", daemon=True)
    thread.start()
    logger.info(
        "Sweeper aktif: file di %s akan dihapus otomatis setelah %s menit.",
        TEMP_DIR, FILE_LIFETIME_MINUTES,
    )
    return thread


def stop_cleanup_thread() -> None:
    _stop_event.set()


def safe_delete(*paths: Path) -> None:
    """Hapus satu atau lebih file, abaikan jika sudah tidak ada."""
    for p in paths:
        try:
            if p and p.exists():
                p.unlink()
        except OSError as e:
            logger.warning("Gagal menghapus %s: %s", p, e)
