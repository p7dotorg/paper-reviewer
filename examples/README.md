# examples

Concrete artifacts so you can see what redink produces without running it.

| File | What |
|---|---|
| [`sample-review.md`](sample-review.md) | A paper review — the verdict, judge-panel votes, findings with their debate outcomes, contradictions and blind spots. Illustrative excerpt of `redink https://arxiv.org/abs/1706.03762`, showing the calibrated **REVISE** on a seminal paper (0 criticals survive debate). |
| [`okf-concept.md`](okf-concept.md) | One `Dataset` concept from a `drl` scan — real [OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog) frontmatter + body. Note the opportunity score is **1/3 despite 1.1M downloads** ("the field is saturated") — the scorer judges opportunity, not popularity. |

A full review also writes a self-contained interactive `*.annotated.html`
(margin notes, click-to-expand detail panel, MathJax). A full `drl` scan writes
a directory of concepts like `okf-concept.md` plus `index.md` and `log.md`.
