"""Shared helpers for all nodes — model factory, tool loop, arXiv ID extraction."""
import os
import re

from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI

from paper.tools import REVIEWER_TOOLS

_ARXIV_ID_RE = re.compile(r"(?:arXiv[:/])?(\d{4}\.\d{4,5})(?:v\d+)?", re.IGNORECASE)
_TOOL_MAP = {t.name: t for t in REVIEWER_TOOLS}


def extract_arxiv_id(text: str) -> str | None:
    m = _ARXIV_ID_RE.search(text[:2000])
    return m.group(1) if m else None


def make_model(model_env_key: str, default: str, structured_schema=None, max_tokens: int = None):
    kwargs = dict(
        model=os.getenv(model_env_key, default),
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        default_headers={"HTTP-Referer": "http://localhost:2024", "X-Title": "p7-reviewer"},
        temperature=0,
    )
    if max_tokens:
        kwargs["max_tokens"] = max_tokens
    m = ChatOpenAI(**kwargs)
    return m.with_structured_output(structured_schema) if structured_schema else m


def tool_loop(model_with_tools, messages: list, max_rounds: int = 5) -> str:
    """Run tool-calling loop until model stops or max_rounds hit."""
    response = None
    for _ in range(max_rounds):
        response = model_with_tools.invoke(messages)
        messages.append(response)
        if not getattr(response, "tool_calls", None):
            break
        for tc in response.tool_calls:
            tool = _TOOL_MAP.get(tc["name"])
            result = tool.invoke(tc["args"]) if tool else f"Unknown tool: {tc['name']}"
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
    return response.content if response else ""
