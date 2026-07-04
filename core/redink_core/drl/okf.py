"""Write an Open Knowledge Format (OKF) bundle — a directory of markdown
concepts with YAML frontmatter. Spec: GoogleCloudPlatform/knowledge-catalog
okf/SPEC.md. We standardize only the small required surface: `type` frontmatter,
reserved index.md / log.md, concept-id = path-minus-.md.
"""
import os
import re
from datetime import datetime, timezone
from pathlib import Path

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def bundle_dir() -> Path:
    return Path(os.getenv("DRL_BUNDLE", "bundle"))


def slugify(text: str) -> str:
    return _SLUG_RE.sub("-", text.lower()).strip("-")[:80] or "unnamed"


def _yaml_scalar(v) -> str:
    s = str(v)
    # quote if it could be misread as YAML
    if s == "" or any(c in s for c in ":#[]{}&*!|>'\"%@`") or s != s.strip():
        return '"' + s.replace('"', '\\"') + '"'
    return s


def _frontmatter(fields: dict) -> str:
    lines = ["---"]
    for k, v in fields.items():
        if v is None or v == "":
            continue
        if isinstance(v, (list, tuple)):
            if not v:
                continue
            inner = ", ".join(_yaml_scalar(x) for x in v)
            lines.append(f"{k}: [{inner}]")
        else:
            lines.append(f"{k}: {_yaml_scalar(v)}")
    lines.append("---")
    return "\n".join(lines)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_concept(concept_id: str, type: str, body: str,
                  title: str = "", description: str = "", resource: str = "",
                  tags=None, extra: dict = None, root: Path = None) -> Path:
    """Write one OKF concept. concept_id is the path within the bundle
    without .md (e.g. 'datasets/lener-br')."""
    root = root or bundle_dir()
    fields = {"type": type, "title": title, "description": description,
              "resource": resource, "tags": list(tags or []),
              "timestamp": now_iso()}
    if extra:
        fields.update(extra)
    path = root / f"{concept_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_frontmatter(fields) + "\n\n" + body.strip() + "\n", encoding="utf-8")
    return path


def append_log(message: str, root: Path = None) -> None:
    """Append to the reserved log.md (OKF §7)."""
    root = root or bundle_dir()
    root.mkdir(parents=True, exist_ok=True)
    log = root / "log.md"
    header = "" if log.exists() else "# Log\n\nChronological history of updates.\n\n"
    with log.open("a", encoding="utf-8") as f:
        f.write(f"{header}- `{now_iso()}` — {message}\n")


def _read_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def rebuild_index(root: Path = None) -> Path:
    """Regenerate the reserved index.md (OKF §6) — a directory listing of every
    concept grouped by top-level folder, with its title/description."""
    root = root or bundle_dir()
    root.mkdir(parents=True, exist_ok=True)
    groups: dict[str, list[tuple[str, dict]]] = {}
    for path in sorted(root.rglob("*.md")):
        if path.name in ("index.md", "log.md"):
            continue
        cid = str(path.relative_to(root).with_suffix(""))
        top = cid.split("/", 1)[0] if "/" in cid else "."
        groups.setdefault(top, []).append((cid, _read_frontmatter(path)))

    lines = ["# Index", "", "Catalog of every concept in this bundle.", ""]
    for top in sorted(groups):
        lines.append(f"## {top}" if top != "." else "## (root)")
        for cid, fm in sorted(groups[top]):
            title = fm.get("title") or cid.rsplit("/", 1)[-1]
            desc = fm.get("description", "")
            suffix = f" — {desc}" if desc else ""
            lines.append(f"- [{title}](/{cid}.md){suffix}")
        lines.append("")
    idx = root / "index.md"
    idx.write_text("\n".join(lines), encoding="utf-8")
    return idx
