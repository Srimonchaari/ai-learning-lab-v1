# Synapz — AI Learning Orchestration Engine

I built Synapz to solve a specific problem: people learning AI engineering have no structured path from "I've read about transformers" to "I can build and evaluate a RAG pipeline in production." Most learning resources optimize for content volume. Synapz optimizes for progression integrity.

---

## What it does

Synapz is a CLI-driven orchestration system that:

1. Maintains a prerequisite-aware curriculum in a declarative YAML roadmap
2. Selects the next eligible concept based on completion history (DAG traversal)
3. Fetches relevant, recent content from curated RSS feeds (arXiv, AWS ML Blog, HuggingFace, etc.)
4. Filters candidates by keyword relevance and deduplicates by URL
5. Outputs a structured daily learning unit: concept brief, mini project, interview challenge

---

## Architecture

Single-direction data flow across three layers:

```
Learner state (progress.json)
     +
Curriculum (roadmap.yaml)
          │
          ▼
  Roadmap Engine     →  select_next_concept() traverses the prerequisite
          │              graph; skips completed nodes, enforces prereqs
          ▼
  Feed Ingestion     →  feedparser over curated RSS packs
          │              age-filtered (configurable window), capped per feed
          ▼
  Relevance Filter   →  regex keyword matching on title+summary
          │              URL deduplication via seen-set
          ▼
  Daily Unit Output
```

---

## Key design decisions

**Deterministic concept selection over ML-based recommendation**
A topological traversal of the prerequisite graph is more debuggable, trustworthy, and auditable than a scoring model at V1 scale. ML-based ranking would optimize for engagement signals that don't exist yet.

**Three-tier fallback fetch strategy**
When strict feeds return zero relevant candidates, the system falls back to category-broader feeds, then to a global AI feed pool. This prevents silent failures without degrading curriculum integrity — the concept node stays fixed; only the source pool widens.

**Keyword matching over embedding similarity**
Regex matching is fast, deterministic, and interpretable. Cosine similarity over embeddings would add latency and infrastructure overhead for marginal recall improvement at this scale. The upgrade point is when keyword precision demonstrably degrades.

**Progress state in flat JSON**
Single-user V1 doesn't need a database. A flat JSON file is portable, auditable, and version-controllable. Migration cost later is low.

---

## Trade-offs explicitly accepted

| Decision | What I gave up |
|---|---|
| YAML roadmap | Dynamic curriculum generation |
| RSS-only ingestion | Paywalled and high-quality non-RSS sources |
| Keyword filtering | Semantic recall across paraphrased content |
| CLI-only interface | Lower barrier to non-developer users |
| Flat JSON state | Multi-user support, concurrent writes |

---

## Repository structure

```
ai-learning-lab-v1/
├── src/
│   ├── main.py        # CLI entry point, feed packs, fallback strategy
│   ├── roadmap.py     # Roadmap load, DAG traversal, concept selection
│   ├── progress.py    # Progress read/write, completion helper
│   └── sources.py     # Feed fetch, age filter, keyword match, dedup
├── tests/             # Unit tests: roadmap, progress, source filtering
├── data/progress.json # Learner state
├── roadmap.yaml       # Curriculum definition with prerequisites
└── docs/index.html    # GitHub Pages project page
```

---

## How to run

```bash
pip install -r requirements.txt

# Default: strict mode, 30-day window, 10 results
python src/main.py

# Widen source pool
python src/main.py --mode broader

# Advance progress after completing today's concept
python src/main.py --mark-done

# Inspect without writing state
python src/main.py --dry-run

# Audit feed configuration for current concept
python src/main.py --list-feeds
```

All flags:

| Flag | Effect |
|---|---|
| `--mode {strict,broader}` | Source breadth for current concept category |
| `--dry-run` | Print output without persisting progress |
| `--mark-done` | Append current concept to completed list |
| `--max-age-days N` | Ignore feed entries older than N days |
| `--limit-per-feed N` | Cap entries fetched per feed URL |
| `--max-results N` | Cap filtered output results |
| `--list-feeds` | Print feed packs for selected concept category |

---

## Tests

```bash
pytest -q
```

Covers roadmap parsing and concept selection, progress persistence, and source filtering and deduplication.

---

## What's next

In priority order:

1. Externalize feed definitions to `feeds.yaml` (currently hardcoded in `main.py`)
2. Source quality scoring: recency + domain authority signals
3. Lesson generation via structured LLM output (concept → project → challenge)
4. Email delivery integration
5. Learner analytics: completion trends, topic heatmap, streak tracking
6. Web admin UI for roadmap and feed governance
