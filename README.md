# Synapz — From Skills to Salary

> Daily, structured AI Engineering learning delivered by email, grounded in trusted sources and roadmap-first progression.

## Why we built this

Most AI learners struggle with one of three problems:
- **Overwhelm:** too much scattered content across blogs, papers, videos, and repos.
- **No progression:** learning random topics without prerequisites.
- **No output:** consuming content but not building real engineering skills.

**Synapz** solves this with a simple product idea:
1. Keep a deterministic skill roadmap.
2. Fetch fresh but controlled learning sources.
3. Extract one focused learning unit daily.
4. Deliver concise lesson + mini project + interview challenge by email.

This repo is the **V1 orchestration engine** for that workflow.

---

## Who benefits

### Primary users
- Students and fresh graduates targeting AI Engineer / ML Engineer roles.
- Backend or full-stack developers transitioning into AI systems work.
- Self-learners who need structured daily direction.

### Secondary users
- Bootcamps and training programs that need curriculum scaffolding.
- Engineering managers enabling internal AI upskilling tracks.

### Business value
- Better learning consistency and completion rates.
- Faster transition from theory to deployable AI engineering tasks.
- Repeatable, low-cost delivery of curated daily learning.

---

## Market opportunity (problem framing)

The market need is driven by:
- High demand for production-ready AI engineering talent.
- Skills gap between prompt usage and systems-level AI implementation.
- Need for affordable, structured upskilling vs expensive long-form programs.

Synapz positions itself as a **structured AI upskilling system**: practical, daily, source-grounded, and project-driven.

---

## Product idea at a glance

The concept (based on your architecture board) is:

1. **Trusted Sources**
   - Tech docs (Open Source, AWS, etc.)
   - Research papers/blogs (arXiv and selected engineering blogs)
   - Code repos/examples (GitHub)
   - Standards/security sources (NIST, OWASP)

2. **Smart Ingestion**
   - Pull latest content via RSS/API fetchers.

3. **Curriculum & Extraction**
   - Map content to roadmap concepts and prerequisites.

4. **Lesson Creation & Delivery**
   - Generate one “AI Engineering Unit”:
     - Short concept
     - Hands-on mini project
     - Reflection prompt
     - Interview challenge

5. **Email Delivery**
   - Send daily unit to learner inbox.

---

## Current V1 scope in this repo

Implemented now:
- Fixed roadmap in `roadmap.yaml`.
- Progress tracking in `data/progress.json`.
- Next-concept selection with prerequisite gating.
- RSS feed fetching and keyword-based filtering.
- CLI runner for daily unit candidate selection.

Not yet implemented:
- Auto lesson generation blocks.
- Email sender integration.
- UI dashboard and analytics.
- Advanced ranking / source quality scoring.

---

## Repository structure

```text
ai-learning-lab-v1/
├── src/
│   ├── main.py          # CLI orchestration + feed fallback strategy
│   ├── roadmap.py       # Roadmap load, flatten, next concept selection
│   ├── progress.py      # Progress read/write + completion helper
│   └── sources.py       # RSS fetch + keyword filter + dedupe
├── tests/
│   ├── test_roadmap.py
│   ├── test_progress.py
│   ├── test_sources.py
│   └── fixtures/sample_rss.xml
├── data/progress.json
├── roadmap.yaml
├── docs/
│   ├── index.html       # GitHub Pages landing page
│   └── styles.css       # Visual styling for product page
├── requirements.txt
└── README.md
```

---

## Architecture (V1 runtime flow)

1. Load roadmap (`roadmap.yaml`).
2. Load completed concept IDs (`data/progress.json`).
3. Select next eligible concept (prereqs satisfied, not completed).
4. Resolve category-specific feed pack (`strict` / `broader`).
5. Fetch and age-filter RSS entries.
6. Filter entries by concept keywords and deduplicate links.
7. Print daily node + candidate sources.
8. Optionally mark concept complete (`--mark-done`).

This preserves curriculum integrity and avoids trend-chasing random topics.

---

## How to run

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Execute daily runner

```bash
python src/main.py
```

### 3) Useful CLI options

```bash
python src/main.py --help
```

Flags:
- `--mode {strict,broader}`: source breadth.
- `--dry-run`: no progress updates.
- `--mark-done`: append current concept to completed list.
- `--max-age-days N`: ignore old feed entries.
- `--limit-per-feed N`: cap entries per feed.
- `--max-results N`: cap filtered results.
- `--list-feeds`: print feed packs for selected concept category.

---

## GitHub Pages (new docs site)

A dedicated landing page is now available in:
- `docs/index.html`
- `docs/styles.css`

### Enable in GitHub
1. Go to repository **Settings → Pages**.
2. Set source to **Deploy from a branch**.
3. Select branch (e.g., `main`) and folder **`/docs`**.
4. Save and open generated Pages URL.

The page includes:
- Product positioning and value proposition.
- Beneficiaries + market section.
- Architecture blocks and workflow timeline.
- Clear CTA and project purpose narrative.

---

## Testing

```bash
pytest -q
```

The suite validates roadmap parsing/selection, progress persistence, and source filtering behavior.

---

## Optimization roadmap (next)

1. Move feed definitions to `feeds.yaml`.
2. Add source scoring (recency, authority, concept relevance).
3. Add lesson generation templates.
4. Add email delivery provider integration.
5. Add learner analytics (completion, streaks, topic heatmap).
6. Add web admin UI/API for roadmap and source governance.

---

## Purpose summary

Synapz exists to convert **daily effort into career-ready AI engineering capability** by combining curriculum discipline, trusted sources, and practical execution loops.
