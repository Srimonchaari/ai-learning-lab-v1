# AI Learning Lab (V1)

A lightweight, CLI-first learning orchestrator that helps a beginner progress toward **AI Systems Engineer** skills through daily roadmap nodes and curated RSS reading suggestions.

## 1) What this project does

On each run, the app:
1. Loads a fixed learning roadmap from `roadmap.yaml`.
2. Loads learner progress from `data/progress.json`.
3. Selects the next eligible concept based on prerequisite completion.
4. Pulls fresh RSS items from curated feeds.
5. Filters items by concept keywords and removes duplicate links.
6. Prints a daily learning summary and (optionally) marks the concept complete.

This is intentionally **V1**: no web UI, no database, no email sender yet.

---

## 2) Repository structure

```text
ai-learning-lab-v1/
├── src/
│   ├── main.py        # CLI entrypoint and orchestration logic
│   ├── roadmap.py     # Roadmap loading + concept progression logic
│   ├── progress.py    # Progress file IO + completion updates
│   └── sources.py     # RSS fetch, keyword filtering, deduping
├── tests/
│   ├── test_roadmap.py
│   ├── test_progress.py
│   ├── test_sources.py
│   └── fixtures/sample_rss.xml
├── roadmap.yaml       # Curriculum definition
├── data/progress.json # Learner state (completed concept IDs)
├── requirements.txt
└── README.md
```

---

## 3) Core concepts and flow

### Roadmap model
- `roadmap.yaml` contains ordered levels.
- Each concept includes:
  - `id`
  - `title`
  - `category`
  - `prereqs`
  - `keywords`
  - `outcome`
  - `mini_project`

### Progress model
- Progress is stored as JSON:

```json
{
  "completed": ["python_basics"]
}
```

### Next concept selection
The selector walks concepts in roadmap order and picks the first concept that:
- is **not** already in `completed`, and
- has all `prereqs` satisfied.

### Content sourcing
`sources.py` fetches RSS entries, applies age filtering, then keeps only entries matching roadmap keywords in title/summary. Links are deduplicated.

---

## 4) Feed strategy in V1

`src/main.py` defines feed packs by category:
- **Foundations**: Python/software-engineering leaning feeds.
- **AI default**: AI/ML engineering feeds (AWS, Google Cloud AI/ML, arXiv CS tracks).

Runtime strategy:
1. Try category feeds with requested mode (`strict` or `broader`).
2. If strict mode returns no candidates, retry with broader category feeds.
3. If still empty, fallback to a global broader AI feed pack.

---

## 5) CLI usage

Run from repository root.

### Install dependencies
```bash
pip install -r requirements.txt
```

### Basic run
```bash
python src/main.py
```

### Useful flags
```bash
python src/main.py --help
```

Important options:
- `--mode {strict,broader}`: source breadth.
- `--dry-run`: preview without updating progress.
- `--mark-done`: append current concept ID to progress.
- `--max-age-days N`: ignore older feed items.
- `--limit-per-feed N`: cap items read from each feed.
- `--max-results N`: cap filtered output.
- `--list-feeds`: print active strict/broader feed lists for chosen concept category.

---

## 6) Testing

Run all tests:

```bash
pytest -q
```

Current test suite validates:
- roadmap parsing/validation/selection behavior,
- progress load/save/idempotent completion,
- source keyword filtering + deduplication,
- fixture RSS parsing sanity.

---

## 7) Current limitations (intentional for V1)

- No email dispatch yet (output is terminal-only).
- No persistent store beyond local JSON.
- Feed URLs are hardcoded in `main.py`.
- Keyword matching is simple regex word-boundary matching.
- No ranking/scoring beyond first-match order.

---

## 8) Suggested next upgrades

1. Move feed packs into `feeds.yaml` for easier maintenance.
2. Add source ingestion pipeline with scoring/ranking.
3. Add email sender (Outlook/SMTP) for daily delivery.
4. Add optional UI/API surface.
5. Add retrieval layer (RAG-ready content cache + citations).

---

## 9) Quick start checklist

1. `pip install -r requirements.txt`
2. `python src/main.py --dry-run`
3. Review selected concept and suggested sources.
4. When complete: `python src/main.py --mark-done`
5. Repeat daily.

This keeps the learning loop simple, deterministic, and easy to extend.
