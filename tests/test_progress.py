from pathlib import Path
import pytest

from src.progress import load_progress, save_progress, mark_completed, completed_ids


def test_load_progress_default_when_missing(tmp_path: Path):
    p = tmp_path / "progress.json"
    data = load_progress(p)
    assert data["completed"] == []


def test_save_and_load_progress_roundtrip(tmp_path: Path):
    p = tmp_path / "progress.json"
    original = {"completed": ["a", "b"]}
    save_progress(p, original)
    loaded = load_progress(p)
    assert loaded == original


def test_load_progress_invalid_format(tmp_path: Path):
    p = tmp_path / "progress.json"
    p.write_text('{"done": ["a"]}', encoding="utf-8")
    with pytest.raises(ValueError):
        load_progress(p)


def test_mark_completed_idempotent():
    progress = {"completed": []}
    mark_completed(progress, "a")
    mark_completed(progress, "a")
    assert progress["completed"] == ["a"]
    assert completed_ids(progress) == ["a"]
