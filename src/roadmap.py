from pathlib import Path
from typing import Dict, List
import yaml


def load_roadmap(path: Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f"Roadmap file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if "levels" not in data:
        raise ValueError("Invalid roadmap format: missing 'levels'")
    return data


def flatten_concepts(roadmap: Dict) -> List[Dict]:
    concepts: List[Dict] = []
    for level in roadmap["levels"]:
        for concept in level.get("concepts", []):
            c = concept.copy()
            c["level"] = level.get("name", "unknown")
            concepts.append(c)
    return concepts


def select_next_concept(concepts: List[Dict], completed: List[str]) -> Dict:
    for concept in concepts:
        cid = concept["id"]
        prereqs = concept.get("prereqs", [])
        if cid in completed:
            continue
        if all(p in completed for p in prereqs):
            return concept
    raise RuntimeError("No eligible next concept found (roadmap may be complete).")
