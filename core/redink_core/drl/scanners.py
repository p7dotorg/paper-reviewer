"""Dataset source scanners. Increment 1: HuggingFace (public API, no auth).
Kaggle and Papers With Code land in later increments."""
import httpx

_HF_API = "https://huggingface.co/api/datasets"


def _normalize_hf(d: dict) -> dict:
    return {
        "source": "hf",
        "id": d.get("id", ""),
        "title": (d.get("cardData") or {}).get("pretty_name") or d.get("id", ""),
        "url": f"https://huggingface.co/datasets/{d.get('id','')}",
        "description": (d.get("description") or "").strip(),
        "tags": d.get("tags", []) or [],
        "downloads": d.get("downloads", 0) or 0,
        "likes": d.get("likes", 0) or 0,
        "last_modified": d.get("lastModified", ""),
        "gated": bool(d.get("gated")),
        "private": bool(d.get("private")),
        "disabled": bool(d.get("disabled")),
    }


def scan_hf(query: str = "", limit: int = 50) -> list[dict]:
    """Fetch datasets from HuggingFace, most-downloaded first."""
    params = {"limit": limit, "full": "true", "sort": "downloads", "direction": -1}
    if query:
        params["search"] = query
    try:
        r = httpx.get(_HF_API, params=params, timeout=25)
        if r.status_code != 200:
            return []
        return [_normalize_hf(d) for d in r.json()]
    except Exception:
        return []


SCANNERS = {"hf": scan_hf}
