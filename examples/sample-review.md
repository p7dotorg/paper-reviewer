# redink: 1706.03762

<!--
Illustrative sample of `redink https://arxiv.org/abs/1706.03762` output
(Attention Is All You Need). Trimmed to a few findings per dimension. The
verdict, judge panel and debate outcomes reflect the calibrated pipeline:
a seminal paper with real, fixable weaknesses lands on REVISE — not FAIL —
because none of its criticals survive the author's rebuttal.
-->

============================================================
  VERDICT: REVISE
============================================================

The Transformer is a genuinely influential contribution, and the panel treats
it as such. The findings are real but fixable: a single model is compared
against ensembles, BLEU is reported without confidence intervals, the ablation
never removes self-attention itself, and the abstract's 41.8 EN-FR score
conflicts with 41.0 in the body. None of these invalidate the central
contribution — every critical was downgraded in debate once the author's side
was argued — so the verdict is major revision, not rejection. Judged by the
peer-review standards of 2017, confidence intervals on BLEU were not yet the
norm; the reproducibility and comparison issues are what a committee would ask
to see addressed.

  0 critical  ·  8 major  ·  6 minor

  Judge panel
  REVISE  rigor         Real methodological gaps (no CIs, uncontrolled comparison,
                        ablation doesn't isolate self-attention) that weaken but
                        do not invalidate the central claim.
  PASS    contribution  The Transformer architecture is a landmark; the flaws are
                        presentation and rigor, not validity.
  REVISE  standards     By 2017 norms a program committee would accept with
                        revisions — fair single-model comparison, variance,
                        reproducibility details.

  Consensus
  · BLEU improvements are reported as single point estimates with no confidence
    intervals or significance tests.
  · The +2 BLEU headline compares a single Transformer against ensemble
    baselines, not single models.

── METHODOLOGY ─────────────────────────────

  MAJOR  academic  ⚖ downgraded
  The ablation (Table 3) varies heads, dimensions and dropout but never removes
  the self-attention mechanism itself — so "attention is all you need" is not
  isolated from model capacity or the training recipe.
  Evidence  "To evaluate the importance of different components of the Transformer,
            we varied our base model in different ways…"
  Defense   The paper's claim is about the overall architecture; the ablation
            supports the design choices even without a no-attention control.
  Fix       Add a control that replaces self-attention with a recurrent/conv
            layer of matched capacity, holding the rest fixed.

  MAJOR  skeptic  ⚖ downgraded
  The FLOPs-based training-cost comparison mixes GPU generations (K80/K40/M40 vs
  P100) and uses theoretical peak, not measured utilization.
  Evidence  "We estimate the number of floating point operations … an estimate of
            the sustained single-precision floating-point capacity of each GPU."
  Fix       Report wall-clock on identical hardware, or measured FLOPs.

── STATISTICS ──────────────────────────────

  MAJOR  skeptic
  BLEU is reported without confidence intervals or significance tests; Table 3
  selects the best of 15+ configurations on the dev set with no multiple-
  comparison correction.
  Evidence  "Our model achieves 28.4 BLEU … improving over the existing best
            results, including ensembles, by over 2 BLEU."
  Fix       Report bootstrap CIs and a significance test; hold out a test set
            for the final number.

── WRITING ─────────────────────────────────

  MAJOR  academic  ⚖ downgraded
  The abstract claims a new single-model SOTA of 41.8 BLEU on EN-FR, but the
  body reports 41.0 for the same task — an internal inconsistency.
  Evidence  Abstract: "41.8"  vs  Section 6.1: "our big model achieves a BLEU
            score of 41.0"
  Fix       Reconcile the two numbers and state the evaluation setup.

── CONTRADICTIONS ─────────────────────────────────────────

  methodology
    SKEPTIC:  the single-vs-ensemble comparison is not apples-to-apples
    PRACTITIONER: the reported comparison is a valid demonstration of quality

── BLIND SPOTS ────────────────────────────────────────────
  · Behavior on long sequences where the O(n²) attention cost dominates.
  · Generalization beyond EN-DE / EN-FR translation and one parsing task.

============================================================
