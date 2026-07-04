# Changelog

All notable changes to redink. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); dates are release-day.

## 0.2.0

The verdict became trustworthy. redink went from a stamp that failed almost
everything to a reviewer whose PASS/REVISE/FAIL tracks real peer-review
outcomes — and every step of that is measured against 300 ICLR papers, not
eyeballed. Also gained a second flow (dataset research) and a config surface.

### Added — calibrated verdict

- Adversarial **debate** on every critical finding: a defender argues the
  author's side from the paper text, a judge rules sustained / downgraded /
  dismissed. Criticals nobody can uphold die before they reach the verdict.
- **Judge panel** — three lenses (rigor, contribution, era-appropriate
  standards) vote the verdict, replacing threshold arithmetic.
- **Calibration anchors** in the judge: reference papers with real
  finding-profiles and the verdict their rating implies. Dropped over-FAIL from
  82% to ~37% and made the verdict discriminate — rejected papers now FAIL ~4x
  more than accepted ones (54% vs 14%), where the baseline failed both alike.

### Added — measurement harness (`eval/`)

- `collect_asap.py` — labeled set from ASAP-Review (ICLR/NIPS papers + real
  reviews + decisions). The target is overlap with human-raised weaknesses, not
  predicting accept/reject (which is confounded by committee politics).
- `overlap_metric.py` — runs redink over each paper, an LLM judge scores recall
  of human weaknesses, noise rate, and verdict-vs-rating. Findings recall ≈ 0.73.
- `rejudge.py` / `confirm_calibration.py` — cheap re-judge over cached findings
  to A/B and confirm the production judge without re-running the pipeline.

### Added — dataset research loop (`drl`)

- Second LangGraph graph: scan → merge → prescore → score → catalog → digest,
  registered alongside `redink` in `langgraph.json`.
- Scanners for **HuggingFace, Kaggle, and OpenML**. Papers With Code was
  dropped — its API now redirects to Hugging Face.
- Writes an **Open Knowledge Format** bundle (portable markdown concepts).
- Analysis commands: `/rank` (opportunity PageRank), `/gaps`, `/spikes`,
  `/wiki` — reading the bundle frontmatter at query time, no DB.

### Added — CLI & config

- Unified chat: dataset commands live inside the `redink` REPL next to the
  review commands.
- Autocomplete (slash commands, `/rerun` dimensions, `/wiki` slugs, `/scan`
  sources), persistent history, ghost-text suggestions, a status bar.
- Central config: `/config [papers|datasets]` and a `redink setup` wizard over
  a single registry; `.env` writes preserve comments and unmanaged keys.

### Changed

- Findings output is standardized to **English** (internal prompts are
  Portuguese; models were code-switching mid-report).
- Reviewer excerpt raised from 20k to 60k chars with an explicit truncation
  notice, so "missing" sections in the omitted tail aren't reported as flaws.
- Two-pass semantic dedup (per-dimension then global) before any severity count.
- Dropped PDF annotation — the interactive HTML report is the only output.

### Fixed

- **Evidence verification**: a finding whose evidence quote can't be found in
  the paper drops to `minor` — kills hallucinated criticals.
- **Temporal filter** on novelty search: results published after the paper are
  filtered in code (no more 2024 papers cited as prior work for a 2017 paper).
- **Rebuttal judge** now requires the defense to *refute* with a quote, not
  merely recontextualize ("it's just a summary") — this unlocked a working FAIL.
- **Tables preserved** as pipe rows through fetch; **abstract-only** ar5iv
  renders are detected and flagged instead of reviewed as if complete.
- **max_tokens capped** by default — uncapped calls made providers reserve
  credit for a 65k-token ceiling, causing spurious 402s.
- Retries transient OpenRouter 429s; classify moved off a rate-limited model.

## 0.1.0

- Interactive, self-contained HTML annotation report (WIRED-style editorial
  layout, academic header, MathJax, margin notes, spotlight detail panel).
- STORM-style multi-persona reviewer over an arXiv/GitHub/local paper.
