from unittest.mock import patch

from redink_core.nodes_debate import debate
from redink_core.schemas import Finding, Rebuttal


def _crit(issue, grounded=False):
    return Finding(
        dimension="reproducibility" if grounded else "methodology",
        severity="critical", issue=issue, evidence="e", suggestion="s",
        grounded=grounded,
    )


def test_grounded_critical_bypasses_debate():
    grounded = _crit("não instala", grounded=True)
    textual = _crit("método frágil", grounded=False)
    state = {"findings": [grounded, textual], "paper": "corpo do paper"}

    # dedup: passthrough; _debate_one: sempre dismiss (mataria um crítico normal)
    dismiss = Rebuttal(ruling="dismiss", defense_summary="d", reasoning="r")
    with patch("redink_core.nodes_debate._dedup_findings", side_effect=lambda f, c: f), \
         patch("redink_core.nodes_debate._debate_one", return_value=dismiss) as m:
        out = debate(state)

    kept = out["deduped_findings"]
    # o grounded sobrevive intocado; o textual foi dismissado (removido)
    assert any(f.grounded and f.issue == "não instala" for f in kept)
    assert all(not (f.issue == "método frágil") for f in kept)
    # _debate_one só foi chamado para o finding NÃO-grounded
    assert m.call_count == 1


def test_grounded_finding_keeps_no_debate_outcome():
    grounded = _crit("repo vazio", grounded=True)
    state = {"findings": [grounded], "paper": "x"}
    with patch("redink_core.nodes_debate._dedup_findings", side_effect=lambda f, c: f):
        out = debate(state)
    kept = out["deduped_findings"]
    assert len(kept) == 1
    assert kept[0].debate_outcome is None
