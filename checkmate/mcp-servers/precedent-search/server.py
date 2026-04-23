"""
Checkmate precedent-search MCP server.

Loads a precedents.jsonl corpus at startup (built offline by
scripts/build-precedent-index.py against the Spare General Drive folder)
and exposes a `search_precedents` tool that returns the top-k matching
precedent rows for a given requirement text.

Pure stdlib except for the `mcp` package. TF-IDF + cosine similarity
implemented inline so there are no heavy dependencies at runtime.

Environment:
  CHECKMATE_PRECEDENTS_PATH  path to precedents.jsonl (required)

The precedents.jsonl format is one JSON object per line, each with:
  {
    "id":             stable identifier (file_id + row_ref)
    "source_file":    "Laramie RFP - Spare EAM Response Matrix (Updated)"
    "source_row":     "3.1.3"
    "agency":         "City of Laramie"
    "year":           2026
    "requirement":    "Enable preventive maintenance scheduling by time, mileage, or hours."
    "verdict":        "Y"
    "comment":        "PM schedules can be set by calendar interval..."
    "url":            "https://docs.google.com/spreadsheets/d/..."  (optional)
  }
"""
from __future__ import annotations

import asyncio
import json
import math
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
from mcp.types import Tool, TextContent


# ---------------------------------------------------------------------------
# TF-IDF index (pure stdlib; no sklearn dependency)
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    if not text:
        return []
    return _TOKEN_RE.findall(text.lower())


@dataclass
class Precedent:
    id: str
    source_file: str
    source_row: str
    agency: str
    year: int | None
    requirement: str
    verdict: str
    comment: str
    url: str | None = None


class PrecedentIndex:
    """TF-IDF cosine-similarity index over precedent requirement texts."""

    def __init__(self, precedents: list[Precedent]) -> None:
        self.precedents = precedents
        self.tokens: list[list[str]] = [_tokenize(p.requirement) for p in precedents]
        self.N = len(precedents)
        df: Counter[str] = Counter()
        for toks in self.tokens:
            for term in set(toks):
                df[term] += 1
        self.idf: dict[str, float] = {
            term: math.log((self.N + 1) / (freq + 1)) + 1.0
            for term, freq in df.items()
        }
        self.doc_vectors: list[dict[str, float]] = [self._vectorize(t) for t in self.tokens]
        self.doc_norms: list[float] = [self._norm(v) for v in self.doc_vectors]

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        return {term: count * self.idf.get(term, 0.0) for term, count in tf.items()}

    @staticmethod
    def _norm(v: dict[str, float]) -> float:
        return math.sqrt(sum(w * w for w in v.values()))

    def _cosine(
        self,
        v1: dict[str, float],
        v2: dict[str, float],
        n1: float,
        n2: float,
    ) -> float:
        if n1 == 0.0 or n2 == 0.0:
            return 0.0
        if len(v1) > len(v2):
            v1, v2 = v2, v1
        dot = sum(w * v2.get(term, 0.0) for term, w in v1.items())
        return dot / (n1 * n2)

    def search(
        self,
        query: str,
        top_k: int = 3,
        min_similarity: float = 0.3,
    ) -> list[tuple[Precedent, float]]:
        q_tokens = _tokenize(query)
        if not q_tokens:
            return []
        q_vec = self._vectorize(q_tokens)
        q_norm = self._norm(q_vec)
        scored: list[tuple[int, float]] = []
        for i, (dv, dn) in enumerate(zip(self.doc_vectors, self.doc_norms)):
            sim = self._cosine(q_vec, dv, q_norm, dn)
            if sim >= min_similarity:
                scored.append((i, sim))
        scored.sort(key=lambda t: t[1], reverse=True)
        return [(self.precedents[i], sim) for i, sim in scored[:top_k]]


# ---------------------------------------------------------------------------
# Corpus loading
# ---------------------------------------------------------------------------


def _load_precedents(path: Path) -> list[Precedent]:
    if not path.exists():
        raise FileNotFoundError(
            f"Precedent corpus not found at {path}. "
            "Run scripts/build-precedent-index.py to generate it."
        )
    precedents: list[Precedent] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, raw in enumerate(f, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {e}") from e
            try:
                precedents.append(
                    Precedent(
                        id=str(obj["id"]),
                        source_file=str(obj["source_file"]),
                        source_row=str(obj["source_row"]),
                        agency=str(obj.get("agency", "")),
                        year=int(obj["year"]) if obj.get("year") is not None else None,
                        requirement=str(obj.get("requirement", "")),
                        verdict=str(obj.get("verdict", "")),
                        comment=str(obj.get("comment", "")),
                        url=(str(obj["url"]) if obj.get("url") else None),
                    )
                )
            except (KeyError, TypeError, ValueError) as e:
                raise ValueError(f"{path}:{line_no}: malformed precedent: {e}") from e
    if not precedents:
        raise ValueError(
            f"Precedent corpus at {path} is empty. "
            "Re-run scripts/build-precedent-index.py."
        )
    return precedents


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

server: Server = Server("checkmate-precedents")
_INDEX: PrecedentIndex | None = None


def _ensure_index() -> PrecedentIndex:
    global _INDEX
    if _INDEX is not None:
        return _INDEX
    path_str = os.environ.get("CHECKMATE_PRECEDENTS_PATH")
    if not path_str:
        raise RuntimeError(
            "CHECKMATE_PRECEDENTS_PATH environment variable is not set. "
            "The plugin's .mcp.json should configure it."
        )
    path = Path(path_str).expanduser()
    precedents = _load_precedents(path)
    _INDEX = PrecedentIndex(precedents)
    print(
        f"[checkmate-precedents] loaded {len(precedents)} precedent rows from {path}",
        file=sys.stderr,
    )
    return _INDEX


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_precedents",
            description=(
                "Search Spare's past-RFP precedent corpus for rows matching a given "
                "requirement text. Returns the top-k nearest matches by TF-IDF cosine "
                "similarity over the requirement texts. Every row drafted by the "
                "fill-rfp-matrix skill MUST call this tool first and cite the returned "
                "precedents; this is how Rule 2 (source every row live) is enforced "
                "programmatically."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "requirement_text": {
                        "type": "string",
                        "description": (
                            "The requirement text from the matrix row being drafted. "
                            "Pass the full requirement, not a summary."
                        ),
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Maximum number of precedents to return. Default 3.",
                        "default": 3,
                        "minimum": 1,
                        "maximum": 20,
                    },
                    "min_similarity": {
                        "type": "number",
                        "description": (
                            "Minimum cosine-similarity threshold. Default 0.3. "
                            "If no matches meet the threshold, the verdict for the "
                            "row should be 'I' (Need More Info) with reasoning "
                            "naming what was searched."
                        ),
                        "default": 0.3,
                        "minimum": 0.0,
                        "maximum": 1.0,
                    },
                },
                "required": ["requirement_text"],
            },
        ),
        Tool(
            name="corpus_stats",
            description=(
                "Return summary statistics about the loaded precedent corpus: "
                "total rows, unique source files, agencies represented, year range. "
                "Useful for a grounding note at the start of a matrix fill."
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    try:
        index = _ensure_index()
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=json.dumps({"error": f"Precedent corpus unavailable: {e}"}),
            )
        ]

    if name == "search_precedents":
        return _handle_search(index, arguments)
    if name == "corpus_stats":
        return _handle_stats(index)
    return [
        TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))
    ]


def _handle_search(index: PrecedentIndex, args: dict[str, Any]) -> list[TextContent]:
    query = args.get("requirement_text", "")
    if not isinstance(query, str) or not query.strip():
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"error": "requirement_text must be a non-empty string"}
                ),
            )
        ]
    top_k = int(args.get("top_k", 3))
    min_sim = float(args.get("min_similarity", 0.3))
    matches = index.search(query, top_k=top_k, min_similarity=min_sim)
    if not matches:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "query": query,
                        "top_k": top_k,
                        "min_similarity": min_sim,
                        "matches": [],
                        "verdict_hint": "I",
                        "reasoning": (
                            "No precedent row in the corpus met the minimum "
                            f"similarity threshold of {min_sim} for this requirement. "
                            "Per Rule 2 the verdict should be 'I' (Need More Info) "
                            "with reasoning naming what was searched."
                        ),
                    }
                ),
            )
        ]
    result = {
        "query": query,
        "top_k": top_k,
        "min_similarity": min_sim,
        "matches": [
            {
                "similarity": round(sim, 3),
                "source_file": p.source_file,
                "source_row": p.source_row,
                "agency": p.agency,
                "year": p.year,
                "requirement": p.requirement,
                "verdict": p.verdict,
                "comment": p.comment,
                "url": p.url,
                "citation": f"{p.source_file} row {p.source_row} ({p.agency} {p.year})",
            }
            for p, sim in matches
        ],
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


def _handle_stats(index: PrecedentIndex) -> list[TextContent]:
    files = sorted({p.source_file for p in index.precedents})
    agencies = sorted({p.agency for p in index.precedents if p.agency})
    years = sorted({p.year for p in index.precedents if p.year is not None})
    verdict_counts: Counter[str] = Counter(p.verdict for p in index.precedents)
    stats = {
        "total_rows": len(index.precedents),
        "unique_source_files": len(files),
        "source_files": files,
        "agencies": agencies,
        "year_range": [years[0], years[-1]] if years else None,
        "verdict_distribution": dict(verdict_counts.most_common()),
    }
    return [TextContent(type="text", text=json.dumps(stats, indent=2))]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def _run() -> None:
    async with stdio_server() as (read, write):
        await server.run(
            read,
            write,
            InitializationOptions(
                server_name="checkmate-precedents",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main() -> None:
    try:
        _ensure_index()
    except Exception as e:
        print(
            f"[checkmate-precedents] startup warning: {e}",
            file=sys.stderr,
        )
    asyncio.run(_run())


if __name__ == "__main__":
    main()
