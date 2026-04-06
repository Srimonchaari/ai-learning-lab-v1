# Synapz — AI Learning Orchestration Engine

> A prerequisite-aware curriculum engine that ingests trusted technical sources and delivers one structured AI engineering learning unit per day — built for progression integrity, not content volume.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-pytest-green?style=flat-square)](https://pytest.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/status-V1%20active-brightgreen?style=flat-square)]()

---

## Table of Contents

- [The Problem](#the-problem)
- [How Synapz Solves It](#how-synapz-solves-it)
- [System Architecture](#system-architecture)
- [Component Reference](#component-reference)
- [Module Breakdown](#module-breakdown)
- [Key Engineering Decisions](#key-engineering-decisions)
- [Trade-offs](#trade-offs)
- [Quick Start](#quick-start)
- [CLI Reference](#cli-reference)
- [Example Output](#example-output)
- [Testing](#testing)
- [V2 Roadmap](#v2-roadmap)

---

## The Problem

Most AI learning resources fail in one of three ways:

| Problem | Root cause |
|---|---|
| **Topic scatter** | Learners jump between YouTube, papers, blogs, repos without a curriculum |
| **No prerequisite awareness** | Concepts are consumed before their foundations are solid |
| **Content without output** | Reading and watching don't translate into engineering muscle |

The result: learners accumulate passive knowledge but can't build or evaluate real AI systems.

---

## How Synapz Solves It

Synapz enforces three constraints simultaneously:

1. **Curriculum integrity** — a YAML roadmap defines concepts and their prerequisite graph. Nothing is unlocked until its dependencies are marked complete.
2. **Source quality** — content is pulled from curated, high-signal feeds (arXiv, AWS ML Blog, HuggingFace, Google Cloud AI). No algorithmic noise.
3. **Actionable output** — every run produces one unit: concept brief + mini project + interview challenge. Not a reading list.

---

## System Architecture

```
╔══════════════════════════════════════════════════════════════════╗
║                    SYNAPZ V1 — RUNTIME FLOW                     ║
╚══════════════════════════════════════════════════════════════════╝

  INPUT LAYER
  ┌──────────────────────┐     ┌───────────────────────┐
  │    roadmap.yaml      │     │  data/progress.json   │
  │                      │     │                       │
  │  levels:             │     │  {                    │
  │    - name: Foundations│     │    "completed": [     │
  │      concepts:       │     │      "py_basics",     │
  │        - id: py_basics│     │      "data_types"    │
  │          prereqs: [] │     │    ],                 │
  │        - id: numpy   │     │    "last_run": "..."  │
  │          prereqs:    │     │  }                    │
  │            - py_basics│     │                       │
  └──────────┬───────────┘     └─────────┬─────────────┘
             └──────────────┬────────────┘
                            │
                            ▼
  SELECTION LAYER
  ┌──────────────────────────────────────────────────────────┐
  │                   ROADMAP ENGINE  (roadmap.py)            │
  │                                                          │
  │   load_roadmap()        → parse and validate YAML        │
  │   flatten_concepts()    → linearize all levels           │
  │   select_next_concept() → traverse concept list:         │
  │                             skip if id in completed      │
  │                             skip if any prereq missing   │
  │                             return first eligible node   │
  │                                                          │
  │   Output: { id, title, category, keywords, mini_project }│
  └──────────────────────────┬───────────────────────────────┘
                             │  concept node + keywords
                             │
                             ▼
  INGESTION LAYER
  ┌──────────────────────────────────────────────────────────┐
  │                 FEED INGESTION  (sources.py)              │
  │                                                          │
  │   feeds_for(category, mode)                              │
  │     "foundations" → GeeksForGeeks, RealPython            │
  │     "ai / llm / rag / ..." → arXiv cs.AI/LG/CL,         │
  │                              AWS ML Blog, HuggingFace,    │
  │                              GCP AI Blog, PyTorch Blog    │
  │                                                          │
  │   fetch_feed_items(feeds, limit_per_feed, max_age_days)  │
  │     → feedparser.parse(url) per feed                     │
  │     → drop entries older than max_age_days window        │
  │     → cap at limit_per_feed entries per feed             │
  │     → return List[FeedItem]                              │
  └──────────────────────────┬───────────────────────────────┘
                             │  raw FeedItem list
                             │
                             ▼
  FILTERING LAYER — THREE-TIER FALLBACK
  ┌──────────────────────────────────────────────────────────┐
  │               FALLBACK STRATEGY  (main.py)               │
  │                                                          │
  │   Tier 1 → feeds_for(category, "strict")                 │
  │             filter_and_dedupe(items, keywords)           │
  │             if results: output ✓  strategy="primary"     │
  │                                                          │
  │   Tier 2 → feeds_for(category, "broader")    [if Tier 1  │
  │             filter_and_dedupe(items, keywords) returned  │
  │             if results: output ✓               nothing]  │
  │                              strategy="category_fallback"│
  │                                                          │
  │   Tier 3 → AI_BROADER (global pool)          [if Tier 2  │
  │             filter_and_dedupe(items, keywords) returned  │
  │             output regardless         strategy="global"] │
  └──────────────────────────┬───────────────────────────────┘
                             │  filtered, deduped List[FeedItem]
                             │
                             ▼
  OUTPUT LAYER
  ┌──────────────────────────────────────────────────────────┐
  │                   DAILY UNIT OUTPUT                       │
  │                                                          │
  │   === TODAY'S NODE ===                                   │
  │   ID:           rag_fundamentals                         │
  │   Title:        RAG — Retrieval-Augmented Generation     │
  │   Level:        Applied AI                               │
  │   Mini Project: Build a basic retriever over 10 docs     │
  │                                                          │
  │   === SOURCE CANDIDATES (Filtered) ===                   │
  │   1. "Retrieval-Augmented Generation for LLMs" — arXiv  │
  │   2. "RAG on AWS Bedrock" — AWS ML Blog                  │
  │   ...                                                    │
  └──────────────────────────────────────────────────────────┘
```

---

## Component Reference

| Module | Responsibility | Key functions |
|---|---|---|
| `roadmap.py` | Load and traverse the prerequisite graph | `load_roadmap`, `flatten_concepts`, `select_next_concept` |
| `sources.py` | Feed ingestion, age filtering, deduplication | `fetch_feed_items`, `filter_and_dedupe` |
| `progress.py` | Read/write learner completion state | `load_progress`, `save_progress`, `mark_completed` |
| `main.py` | CLI entry point, feed packs, fallback strategy | `feeds_for`, `fetch_candidates_with_fallback`, `main` |
| `roadmap.yaml` | Declarative curriculum with prerequisites | — |
| `data/progress.json` | Mutable learner state (completed concept IDs) | — |

---

## Module Breakdown

### `roadmap.py` — Prerequisite Graph Engine

The roadmap is a YAML file structured as an ordered list of levels, each containing concepts with optional prerequisite arrays.

```python
# Prerequisite enforcement — the core selection logic
def select_next_concept(concepts: List[Dict], completed: List[str]) -> Dict:
    for concept in concepts:
        cid = concept["id"]
        prereqs = concept.get("prereqs", [])
        if cid in completed:
            continue                              # already done
        if all(p in completed for p in prereqs):  # all deps satisfied
            return concept                        # first eligible node
    raise RuntimeError("No eligible next concept found.")
```

This is intentionally a linear scan with O(n) traversal. At curriculum scale (tens to hundreds of concepts), this is correct. The alternative — maintaining a topological sort externally — adds complexity without benefit.

---

### `sources.py` — Feed Ingestion and Filtering

Each feed item is parsed into a frozen `FeedItem` dataclass:

```python
@dataclass(frozen=True)
class FeedItem:
    title: str
    link: str
    published: Optional[datetime]   # UTC-aware when available
    summary: str
    source_feed: str
```

Keyword matching uses word-boundary regex to prevent false positives (e.g., "rage" matching "rag"):

```python
def _matches_keywords(text: str, keywords: Iterable[str]) -> bool:
    text_l = text.lower()
    for kw in keywords:
        if re.search(r"\b" + re.escape(kw.lower()) + r"\b", text_l):
            return True
    return False
```

Deduplication uses a URL seen-set — not title hashing — because the same article can appear under slightly different titles across feeds.

---

### `main.py` — Orchestration and Fallback Strategy

Feed packs are category-aware. The `foundations` category (Python basics, NumPy, data types) gets different feeds than AI-category concepts (RAG, LLMs, fine-tuning).

```
FOUNDATIONS_STRICT  = [GeeksForGeeks, RealPython]
FOUNDATIONS_BROADER = FOUNDATIONS_STRICT + [Python.org, GitHub Blog]

AI_STRICT  = [AWS ML Blog, GCP AI/ML, arXiv cs.AI, arXiv cs.LG, arXiv cs.CL]
AI_BROADER = AI_STRICT + [HuggingFace Blog, PyTorch Blog, GitHub Blog]
```

The three-tier fallback prevents the most common failure mode in content pipelines: silent empty results that look like success. Each tier is logged with its strategy name for observability.

---

### `progress.py` — State Management

Progress is stored as a JSON object with a `completed` array of concept IDs. Writing is atomic: the file is not partially updated on failure.

```json
{
  "completed": ["py_basics", "data_types", "numpy_intro"],
  "last_updated": "2025-04-06T09:14:22Z"
}
```

The flat structure is intentional. A database is not warranted for single-user V1 state that is always fully loaded. The entire file is read once per run.

---

## Key Engineering Decisions

### 1. Deterministic concept selection, not ML-based recommendation

**Considered:** Scoring concepts by recency + engagement + relevance using a small ML model.  
**Chose:** Topological DAG traversal — visit each concept in order, skip completed, enforce prereqs.  
**Why:** Scoring requires engagement signals that don't exist yet. A deterministic traversal is auditable, testable, and produces exactly the same result for the same state. ML ranking optimizes for a signal that isn't available — and would silently fail without any visible error.

---

### 2. Three-tier fallback over hard failure

**Considered:** Return an error when no relevant articles are found for a concept.  
**Chose:** A tiered fallback: strict → broader → global pool.  
**Why:** RSS feeds are unpredictable. A strict feed for "rag fundamentals" might have no entries this week. Hard failure would block learning. The fallback widens the source pool while keeping the concept node fixed — the learning objective never changes, only the supporting content degrades gracefully.

---

### 3. Keyword regex matching, not embedding similarity

**Considered:** Embed concept keywords and candidate summaries, score by cosine similarity.  
**Chose:** Regex word-boundary matching on title + summary.  
**Why:** At this scale, embedding similarity would add GPU/API cost, latency, and a non-deterministic component to what is otherwise a reproducible pipeline. Keyword precision is measurable and debuggable. The threshold for upgrading is clear: when keyword recall demonstrably fails across multiple concept categories.

---

### 4. Flat JSON state, not a database

**Considered:** SQLite or a lightweight database for progress tracking.  
**Chose:** A flat JSON file (`data/progress.json`).  
**Why:** Single-user V1 reads the entire state on every run. JSON is version-controllable, auditable, and portable. Adding a database would mean managing connections, schemas, and migrations for a file that will never have concurrent writers. The migration path to a database is straightforward when multi-user support is needed.

---

### 5. YAML curriculum, not a dynamic roadmap

**Considered:** Generate a roadmap dynamically from a knowledge graph or LLM.  
**Chose:** A static, human-authored YAML file.  
**Why:** Curriculum quality is not a problem that benefits from automation at V1. A human-reviewed ordering with explicit prerequisites is more trustworthy than a generated one. The YAML is version-controlled, diffable, and easy to extend. Dynamic generation adds complexity without improving learning outcomes.

---

## Trade-offs

| Decision | Capability gained | What was given up | When to revisit |
|---|---|---|---|
| YAML roadmap | Auditability, stability | Dynamic generation | When curriculum size exceeds 200 concepts |
| RSS ingestion | Zero-cost fresh content | Paywalled, curated sources | When feed precision degrades measurably |
| Keyword matching | Speed, interpretability | Semantic recall (paraphrased content) | When precision < threshold across categories |
| Flat JSON state | Portability, simplicity | Multi-user, concurrent writes | When adding second user or web layer |
| CLI-only interface | No infra overhead | Non-developer access | When building user-facing product |
| No lesson generation | Simpler, reproducible | AI-authored learning content | V2 — add structured LLM output step |

---

## Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/srimonchaari/ai-learning-lab-v1.git
cd ai-learning-lab-v1
pip install -r requirements.txt
```

### Run

```bash
# Default: strict feeds, 30-day window, 10 results
python src/main.py

# Widen source pool for the current concept
python src/main.py --mode broader

# Preview without persisting progress state
python src/main.py --dry-run

# Mark today's concept complete and advance progress
python src/main.py --mark-done

# Audit which feeds are active for the current concept
python src/main.py --list-feeds
```

---

## CLI Reference

| Flag | Default | Effect |
|---|---|---|
| `--mode {strict,broader}` | `strict` | Source breadth: strict uses minimal curated feeds; broader adds discovery feeds |
| `--dry-run` | `false` | Print output without writing to `progress.json` |
| `--mark-done` | `false` | Append current concept ID to completed list and save |
| `--max-age-days N` | `30` | Ignore feed entries published more than N days ago |
| `--limit-per-feed N` | `15` | Maximum entries to process per feed URL |
| `--max-results N` | `10` | Maximum filtered results to display |
| `--list-feeds` | `false` | Print strict and broader feed packs for the current concept's category |
| `--log-level {DEBUG,INFO,WARNING}` | `INFO` | Logging verbosity |

---

## Example Output

```
2025-04-06 09:14:22 | INFO | AI Learning Lab V1 starting
2025-04-06 09:14:22 | INFO | Mode=strict dry_run=False mark_done=False
2025-04-06 09:14:23 | INFO | Selected concept: rag_fundamentals | RAG — Retrieval-Augmented Generation
2025-04-06 09:14:23 | INFO | Category=ai Keywords=['rag', 'retrieval', 'augmented', 'generation', 'vector']
2025-04-06 09:14:25 | INFO | Fetch strategy=category_primary feeds=5 candidates=4

=== TODAY'S NODE ===
ID:          rag_fundamentals
Title:       RAG — Retrieval-Augmented Generation
Level:       Applied AI
Category:    ai
Mini Project: Build a basic retriever over a 10-document corpus using FAISS

=== SOURCE CANDIDATES (Filtered) ===
1. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
   https://arxiv.org/abs/2005.11401
   Published: 2025-03-28
   Feed: http://export.arxiv.org/rss/cs.AI

2. Build a RAG application using Amazon Bedrock
   https://aws.amazon.com/blogs/machine-learning/...
   Published: 2025-04-01
   Feed: https://aws.amazon.com/blogs/machine-learning/feed/
```

---

## Testing

```bash
pytest -q
```

### Test coverage

| Test file | What it covers |
|---|---|
| `tests/test_roadmap.py` | Roadmap YAML parsing, concept flattening, prereq enforcement, no-eligible-concept error |
| `tests/test_progress.py` | Progress load/save, mark_completed idempotency, missing file handling |
| `tests/test_sources.py` | Keyword matching (true positive, false positive, case), deduplication, age filtering |

Fixtures in `tests/fixtures/sample_rss.xml` provide a stable, offline RSS dataset for deterministic source tests.

---

## Repository Structure

```
ai-learning-lab-v1/
├── src/
│   ├── main.py          # CLI entry, feed packs, fallback strategy, orchestration
│   ├── roadmap.py       # YAML load, concept flatten, prereq-aware selection
│   ├── progress.py      # JSON read/write, mark_completed, completed_ids
│   └── sources.py       # FeedItem dataclass, fetch, age filter, keyword match, dedup
├── tests/
│   ├── test_roadmap.py
│   ├── test_progress.py
│   ├── test_sources.py
│   └── fixtures/
│       └── sample_rss.xml
├── data/
│   └── progress.json    # Mutable learner state
├── roadmap.yaml         # Curriculum: levels, concepts, prerequisites, keywords
├── requirements.txt
└── docs/
    └── index.html       # GitHub Pages portfolio page
```

---

## V2 Roadmap

Priority order with rationale:

| Priority | Feature | Why |
|---|---|---|
| 1 | Externalize feeds to `feeds.yaml` | Eliminate hardcoded URLs in `main.py`; enable feed management without code changes |
| 2 | Source quality scoring | Score by recency + domain authority; rank candidates, not just filter them |
| 3 | Structured lesson generation | LLM-powered: concept node → lesson + project + challenge with constrained output schema |
| 4 | Email delivery integration | Daily push via Resend/SendGrid; reduces friction to zero for the learner |
| 5 | Learner analytics | Completion trends, topic heatmap, streak tracking — needed before any personalization layer |
| 6 | Web admin UI | Roadmap governance and feed management via API; prerequisite for multi-user support |
| 7 | Embedding-based retrieval | Upgrade from keyword matching when recall degrades; requires evaluation benchmark first |

---

## License

MIT
