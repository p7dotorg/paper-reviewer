from redink_core.graph import route_to_reviewers
from redink_core.schemas import Classification


def _state(dims, code_repo=None, github_url=None):
    clf = Classification(
        area="Machine Learning", paper_type="empirical",
        dimensions=dims, citations=[], claims=[], code_repo=code_repo,
    )
    s = {"classification": clf, "paper": "corpo"}
    if github_url:
        s["github_url"] = github_url
    return s


def _has_repro(sends):
    return any(getattr(s, "node", None) == "repro_check" for s in sends)


def test_no_repro_send_when_flag_off(monkeypatch):
    monkeypatch.delenv("REDINK_REPRO", raising=False)
    sends = route_to_reviewers(_state(["reproducibility"], code_repo="https://github.com/foo/bar"))
    assert not _has_repro(sends)


def test_repro_send_when_flag_and_code_repo(monkeypatch):
    monkeypatch.setenv("REDINK_REPRO", "1")
    sends = route_to_reviewers(_state(["reproducibility"], code_repo="https://github.com/foo/bar"))
    assert _has_repro(sends)
    repro = next(s for s in sends if s.node == "repro_check")
    assert repro.arg["code_repo"] == "https://github.com/foo/bar"


def test_no_repro_send_without_reproducibility_dim(monkeypatch):
    monkeypatch.setenv("REDINK_REPRO", "1")
    sends = route_to_reviewers(_state(["methodology"], code_repo="https://github.com/foo/bar"))
    assert not _has_repro(sends)


def test_no_repro_send_without_repo(monkeypatch):
    monkeypatch.setenv("REDINK_REPRO", "1")
    sends = route_to_reviewers(_state(["reproducibility"]))
    assert not _has_repro(sends)


def test_falls_back_to_github_url_input(monkeypatch):
    monkeypatch.setenv("REDINK_REPRO", "1")
    sends = route_to_reviewers(_state(
        ["reproducibility"], github_url="https://github.com/foo/bar"))
    assert _has_repro(sends)
    repro = next(s for s in sends if s.node == "repro_check")
    assert repro.arg["code_repo"] == "https://github.com/foo/bar"


def test_arxiv_url_is_not_used_as_repo(monkeypatch):
    monkeypatch.setenv("REDINK_REPRO", "1")
    sends = route_to_reviewers(_state(
        ["reproducibility"], github_url="https://arxiv.org/abs/1706.03762"))
    assert not _has_repro(sends)
