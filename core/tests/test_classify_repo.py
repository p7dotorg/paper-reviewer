from redink_core.nodes_classify import _repo_candidates_block


def test_block_lists_github_urls_from_full_text():
    paper = (
        "Intro. " + "x" * 30000 +
        " Our implementation is available at https://github.com/lmcinnes/umap "
        " and we compare against https://github.com/KlugerLab/FIt-SNE here."
    )
    block = _repo_candidates_block(paper)
    assert "github.com/lmcinnes/umap" in block
    assert "github.com/KlugerLab/FIt-SNE" in block
    # instrui o LLM a escolher o oficial, ignorar baselines
    assert "OFICIAL" in block


def test_block_empty_when_no_repo():
    assert _repo_candidates_block("sem repositórios aqui") == ""


def test_block_dedups_repeated_urls():
    paper = "veja https://github.com/a/b aqui e de novo https://github.com/a/b ali"
    block = _repo_candidates_block(paper)
    # uma única linha de item (o contexto pode ecoar a URL, por isso conta-se o bullet)
    assert block.count("- https://github.com/a/b") == 1


def test_block_strips_trailing_punctuation():
    block = _repo_candidates_block("code available at (https://github.com/foo/bar).")
    # o item da lista deve terminar em .../bar, sem o ') ' ou '.' colado
    assert "- https://github.com/foo/bar " in block
