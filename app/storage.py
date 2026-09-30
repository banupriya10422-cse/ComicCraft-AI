from threading import Lock
from typing import Optional

from .schemas import ComicRecord


_records: dict[str, ComicRecord] = {}

_lock = Lock()


def save_comic(record: ComicRecord) -> None:

    with _lock:
        _records[record.comic_id] = record


def get_comic(comic_id: str) -> Optional[ComicRecord]:

    with _lock:
        return _records.get(comic_id)