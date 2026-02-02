import json
from pathlib import Path
from typing import List, Dict, Any

DEFAULT_PROGRESS = {"completed": []}

def load_progress(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return DEFAULT_PROGRESS.copy()
    data = json.loads(path.read_text(encoding="utf-8"))
    if "completed" not in data or not isinstance(data["completed"], list):
        raise ValueError("Invalid progress format: expected { completed: [] }")
    return data

def save_progress(path: Path, progress: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(progress, indent=2), encoding="utf-8")

def mark_completed(progress: Dict[str, Any], concept_id: str) -> None:
    if concept_id not in progress["completed"]:
        progress["completed"].append(concept_id)

def completed_ids(progress: Dict[str, Any]) -> List[str]:
    return list(progress["completed"])
