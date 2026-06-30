"""reviewer and figure_reviewer nodes."""
from langchain_core.messages import HumanMessage, SystemMessage

from paper.nodes_helpers import make_model, tool_loop, extract_arxiv_id
from paper.prompts import build_reviewer_prompt, FINDING_SCHEMA_PROMPT
from paper.schemas import Finding, FindingsList
from paper.tools import REVIEWER_TOOLS, extract_figures

_TOOL_INSTRUCTIONS = {
    "citations": (
        "Você tem 3 ferramentas:\n"
        "• search_papers(query) — busca no arXiv pelo título ou autores da referência\n"
        "• get_paper(arxiv_id) — lê o abstract de um paper arXiv para confirmar conteúdo\n"
        "• verify_doi(doi) — confirma publicação via Crossref (para papers fora do arXiv)\n\n"
        "Estratégia: para cada referência suspeita, tente search_papers primeiro. "
        "Se não achar e a referência tiver DOI, use verify_doi. "
        "Verifique no mínimo 5 referências — priorize títulos vagos ou autores desconhecidos."
    ),
    "novelty": (
        "Você tem 3 ferramentas:\n"
        "• search_papers(query) — busca no arXiv por método, problema ou baseline\n"
        "• get_paper(arxiv_id) — lê o abstract para comparar com as claims do paper\n"
        "• verify_doi(doi) — verifica papers de conferências fora do arXiv\n\n"
        "Estratégia: faça pelo menos 3 buscas com queries diferentes "
        "(nome do método, problema central, baseline principal). "
        "Para cada resultado relevante, leia o abstract com get_paper e compare com as claims."
    ),
}

_CONCISENESS = "\n\nIMPORTANTE: Máximo 4 findings, cada um com no máximo 3 frases."


def _structured_findings(analysis_text: str, dim: str, persona: str) -> list[Finding]:
    structured = make_model("STRUCTURED_MODEL", "openai/gpt-4o-mini", FindingsList, max_tokens=4000)
    result = structured.invoke([
        SystemMessage(content=(
            "Converta a análise em findings estruturados. "
            "Severity: critical, major ou minor. Máximo 4 findings. "
            f"O campo dimension deve ser sempre '{dim}'. "
            f"O campo persona deve ser sempre '{persona}'."
        )),
        HumanMessage(content=f"Dimensão: {dim}\nPersona: {persona}\n\nAnálise:\n{analysis_text[:5000]}"),
    ])
    findings = result.findings if isinstance(result, FindingsList) else []
    for f in findings:
        f.persona = persona
    if not findings:
        findings = [Finding(
            dimension=dim, persona=persona, severity="minor",
            issue="Análise não retornou findings estruturados.",
            evidence=analysis_text[:200],
            suggestion="Revisar manualmente esta dimensão.",
        )]
    return findings


def reviewer(state):
    dim = state["dimension"]
    persona = state.get("persona", "skeptic")
    clf = state["classification"]
    paper = state["paper"]
    system_prompt = build_reviewer_prompt(dim, persona)
    header = (
        f"Área: {clf.area} | Tipo: {clf.paper_type}\n"
        f"Claims: {'; '.join(clf.claims)}\nPersona: {persona}"
    )

    if dim in ("citations", "novelty"):
        model = make_model("REVIEWER_MODEL", "google/gemini-2.5-flash", max_tokens=4000)
        model_with_tools = model.bind_tools(REVIEWER_TOOLS)
        messages = [
            SystemMessage(content=f"{system_prompt}\n\n{_TOOL_INSTRUCTIONS[dim]}\n\n{FINDING_SCHEMA_PROMPT}{_CONCISENESS}"),
            HumanMessage(content=f"{header}\n\nCitações extraídas: {'; '.join(clf.citations[:20])}\n\nPAPER:\n{paper}"),
        ]
        analysis_text = tool_loop(model_with_tools, messages, max_rounds=6)
    else:
        model = make_model("REVIEWER_MODEL", "google/gemini-2.5-flash", max_tokens=3000)
        response = model.invoke([
            SystemMessage(content=system_prompt + "\n\n" + FINDING_SCHEMA_PROMPT + _CONCISENESS),
            HumanMessage(content=f"{header}\n\nPAPER:\n{paper}"),
        ])
        analysis_text = response.content

    return {"findings": _structured_findings(analysis_text, dim, persona)}


def figure_reviewer(state):
    """Vision node — fetches ar5iv figures and runs image analysis."""
    clf = state["classification"]
    paper = state["paper"]
    arxiv_id = extract_arxiv_id(paper)
    figures = extract_figures(arxiv_id) if arxiv_id else []

    if not figures:
        return {"findings": [Finding(
            dimension="figures", persona="skeptic", severity="minor",
            issue="Figuras não disponíveis (paper não está no ar5iv ou sem arXiv ID).",
            evidence="ar5iv retornou lista vazia.",
            suggestion="Verifique manualmente os gráficos do PDF original.",
        )]}

    system_prompt = build_reviewer_prompt("figures", "skeptic")
    vision_content = []
    for fig in figures:
        vision_content.append({"type": "image_url", "image_url": {"url": fig["url"]}})
        if fig["caption"]:
            vision_content.append({"type": "text", "text": f"[Caption: {fig['caption']}]"})
    vision_content.append({"type": "text", "text": (
        f"{system_prompt}\n\n{FINDING_SCHEMA_PROMPT}{_CONCISENESS}\n\n"
        f"Área: {clf.area} | Tipo: {clf.paper_type}\n"
        f"Claims: {'; '.join(clf.claims)}\n\n"
        f"Analise as {len(figures)} figuras. Detecte desonestidade visual, "
        "cherry-picking, ausência de barras de erro, eixos truncados, captions enganosas."
    )})

    model = make_model("FIGURE_MODEL", "google/gemini-2.5-flash", max_tokens=3000)
    analysis_text = model.invoke([HumanMessage(content=vision_content)]).content
    return {"findings": _structured_findings(analysis_text, "figures", "skeptic")}
