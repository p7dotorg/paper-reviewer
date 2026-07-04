"""DRL graph — dataset scan → opportunity score → OKF bundle.

  init → (Send per source) → scan_source → merge → prescore
       → (Send per kept dataset) → score_one → catalog → digest → END

Same fan-out shape as the reviewer graph; `graph` is registered as a second
entry in langgraph.json alongside `redink`.
"""
import operator
from typing import Annotated, Optional
from typing_extensions import TypedDict

from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from redink_core.drl.nodes import (
    scan_source, merge, prescore, score_one, catalog, digest,
)

DEFAULT_SOURCES = ["hf"]


class DRLState(TypedDict, total=False):
    query: str                                  # search term ("" = broad)
    sources: list[str]                          # e.g. ["hf"]
    limit: int                                  # per-source cap
    raw: Annotated[list[dict], operator.add]    # scanned records (fan-in)
    merged: list[dict]                           # deduped + pre-scored
    scored: Annotated[list[dict], operator.add] # per-dataset LLM scores (fan-in)
    catalog: Optional[dict]
    digest: Optional[str]


def init(state: DRLState):
    return {
        "query": state.get("query", ""),
        "sources": state.get("sources") or DEFAULT_SOURCES,
        "limit": state.get("limit", 50),
    }


def route_to_sources(state: DRLState) -> list[Send]:
    return [Send("scan_source", {"source": s, "query": state["query"], "limit": state["limit"]})
            for s in state["sources"]]


def route_to_scorers(state: DRLState) -> list[Send]:
    return [Send("score_one", {"dataset": d}) for d in state.get("merged", [])]


builder = StateGraph(DRLState)
builder.add_node("init", init)
builder.add_node("scan_source", scan_source)
builder.add_node("merge", merge)
builder.add_node("prescore", prescore)
builder.add_node("score_one", score_one)
builder.add_node("catalog", catalog)
builder.add_node("digest", digest)

builder.add_edge(START, "init")
builder.add_conditional_edges("init", route_to_sources, ["scan_source"])
builder.add_edge("scan_source", "merge")
builder.add_edge("merge", "prescore")
builder.add_conditional_edges("prescore", route_to_scorers, ["score_one"])
builder.add_edge("score_one", "catalog")
builder.add_edge("catalog", "digest")
builder.add_edge("digest", END)

graph = builder.compile()
graph_runner = graph  # no interrupts in DRL yet
