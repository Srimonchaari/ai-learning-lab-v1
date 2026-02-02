from pathlib import Path
import pytest

from src.roadmap import load_roadmap, flatten_concepts, select_next_concept


def test_load_roadmap_missing_file(tmp_path: Path):
    missing = tmp_path / "nope.yaml"
    with pytest.raises(FileNotFoundError):
        load_roadmap(missing)


def test_load_roadmap_invalid_format(tmp_path: Path):
    p = tmp_path / "bad.yaml"
    p.write_text("foo: bar\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_roadmap(p)


def test_flatten_concepts_adds_level():
    roadmap = {
        "levels": [
            {"name": "L0", "concepts": [{"id": "a", "title": "A"}]},
            {"name": "L1", "concepts": [{"id": "b", "title": "B"}]},
        ]
    }
    concepts = flatten_concepts(roadmap)
    assert len(concepts) == 2
    assert concepts[0]["level"] == "L0"
    assert concepts[1]["level"] == "L1"


def test_select_next_concept_respects_prereqs():
    concepts = [
        {"id": "a", "title": "A", "prereqs": []},
        {"id": "b", "title": "B", "prereqs": ["a"]},
        {"id": "c", "title": "C", "prereqs": ["b"]},
    ]

    # nothing completed -> picks a
    assert select_next_concept(concepts, [])["id"] == "a"

    # a completed -> picks b
    assert select_next_concept(concepts, ["a"])["id"] == "b"

    # a,b completed -> picks c
    assert select_next_concept(concepts, ["a", "b"])["id"] == "c"


def test_select_next_concept_raises_when_complete():
    concepts = [
        {"id": "a", "title": "A", "prereqs": []},
    ]
    with pytest.raises(RuntimeError):
        select_next_concept(concepts, ["a"])
