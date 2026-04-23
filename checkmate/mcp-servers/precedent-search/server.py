"""
Checkmate precedent-search MCP server.

Pure-stdlib implementation of MCP JSON-RPC 2.0 over stdio. No third-party
dependencies. No pip install. Works on any Python 3.10+ that ships with
the OS or with Cowork's bundled interpreter.

Loads a precedents.jsonl corpus from a resolved path (see _resolve_path
below), indexes it with TF-IDF + cosine similarity, and exposes two
tools:

  - search_precedents(requirement_text, top_k=3, min_similarity=0.3)
  - corpus_stats()

The corpus is hot-reloaded on every tool call if the file's mtime has
changed since the last load. This lets the `fill-rfp-matrix` skill pull
a fresh corpus from Drive into the cache path at session start without
restarting the server.

Path resolution (first hit wins):
  1. $CHECKMATE_PRECEDENTS_PATH   (set by plugin .mcp.json)
  2. ~/.cache/checkmate/precedents.jsonl   (session cache written by
     fill-rfp-matrix's in-session rebuild step)
  3. $CLAUDE_PLUGIN_ROOT/data/precedents.jsonl   (bundled sample, used
     only for smoke tests; real runs expect #2 to be populated)

The server fails loudly when no path resolves to an existing, non-empty
corpus. Silent fallback to general knowledge would defeat the purpose.

MCP wire format (stdio transport):
  One JSON-RPC 2.0 object per line on stdin and stdout. No
  Content-Length framing. Stderr is used for human-readable logs only.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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
# Corpus loading with hot-reload
# ---------------------------------------------------------------------------


def _load_precedents(path: Path) -> list[Precedent]:
    if not path.exists():
        raise FileNotFoundError(
            f"Precedent corpus not found at {path}. "
            "Start fill-rfp-matrix to rebuild from Spare General."
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
            "Re-run fill-rfp-matrix to rebuild from Spare General."
        )
    return precedents


def _resolve_path() -> Path:
    """Find a usable corpus path. First hit wins."""
    candidates: list[Path] = []

    env_path = os.environ.get("CHECKMATE_PRECEDENTS_PATH")
    if env_path:
        candidates.append(Path(env_path).expanduser())

    candidates.append(Path.home() / ".cache" / "checkmate" / "precedents.jsonl")

    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        candidates.append(Path(plugin_root) / "data" / "precedents.jsonl")

    for c in candidates:
        if c.exists() and c.stat().st_size > 0:
            return c

    raise FileNotFoundError(
        "No precedent corpus found. Expected one of:\n  "
        + "\n  ".join(str(c) for c in candidates)
        + "\nStart fill-rfp-matrix to rebuild the corpus from Spare General."
    )


_INDEX: PrecedentIndex | None = None
_INDEX_PATH: Path | None = None
_INDEX_MTIME: float | None = None


def _ensure_index() -> PrecedentIndex:
    """Load or hot-reload the index.

    Hot-reload triggers when the resolved path or its mtime has changed
    since the last load. This lets the fill-rfp-matrix skill swap in a
    freshly-pulled corpus without restarting the MCP server.
    """
    global _INDEX, _INDEX_PATH, _INDEX_MTIME

    try:
        path = _resolve_path()
    except FileNotFoundError:
        if _INDEX is not None:
            # Corpus disappeared since last load; keep serving the old one
            # rather than blowing up mid-session.
            return _INDEX
        raise

    mtime = path.stat().st_mtime
    if _INDEX is None or _INDEX_PATH != path or _INDEX_MTIME != mtime:
        precedents = _load_precedents(path)
        _INDEX = PrecedentIndex(precedents)
        _INDEX_PATH = path
        _INDEX_MTIME = mtime
        _log(f"loaded {len(precedents)} precedent rows from {path}")
    return _INDEX


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------


def _search(args: dict[str, Any]) -> dict[str, Any]:
    index = _ensure_index()
    query = args.get("requirement_text", "")
    if not isinstance(query, str) or not query.strip():
        return {"error": "requirement_text must be a non-empty string"}
    top_k = int(args.get("top_k", 3))
    min_sim = float(args.get("min_similarity", 0.3))
    matches = index.search(query, top_k=top_k, min_similarity=min_sim)
    if not matches:
        return {
            "query": query,
            "top_k": top_k,
            "min_similarity": min_sim,
            "matches": [],
            "verdict_hint": "I",
            "reasoning": (
                "No precedent row in the corpus met the minimum similarity "
                f"threshold of {min_sim} for this requirement. Per Rule 2 the "
                "verdict should be 'I' (Need More Info) with reasoning naming "
                "what was searched."
            ),
        }
    return {
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


def _stats(_args: dict[str, Any]) -> dict[str, Any]:
    index = _ensure_index()
    files = sorted({p.source_file for p in index.precedents})
    agencies = sorted({p.agency for p in index.precedents if p.agency})
    years = sorted({p.year for p in index.precedents if p.year is not None})
    verdict_counts: Counter[str] = Counter(p.verdict for p in index.precedents)
    return {
        "total_rows": len(index.precedents),
        "unique_source_files": len(files),
        "source_files": files,
        "agencies": agencies,
        "year_range": [years[0], years[-1]] if years else None,
        "verdict_distribution": dict(verdict_counts.most_common()),
        "corpus_path": str(_INDEX_PATH) if _INDEX_PATH else None,
    }


# Tool schemas (returned from tools/list)
_TOOLS: list[dict[str, Any]] = [
    {
        "name": "search_precedents",
        "description": (
            "Search Spare's past-RFP precedent corpus for rows matching a given "
            "requirement text. Returns the top-k nearest matches by TF-IDF cosine "
            "similarity over the requirement texts. Every row drafted by the "
            "fill-rfp-matrix skill MUST call this tool first and cite the returned "
            "precedents; this is how Rule 2 (source every row live) is enforced "
            "programmatically."
        ),
        "inputSchema": {
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
    },
    {
        "name": "corpus_stats",
        "description": (
            "Return summary statistics about the loaded precedent corpus: "
            "total rows, unique source files, agencies represented, year range, "
            "and the path of the corpus file currently loaded. Useful for a "
            "grounding note at the start of a matrix fill."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
]


_HANDLERS = {
    "search_precedents": _search,
    "corpus_stats": _stats,
}


# ---------------------------------------------------------------------------
# JSON-RPC 2.0 / MCP stdio loop
# ---------------------------------------------------------------------------


# MCP protocol version this server implements. Clients negotiate this
# during initialize; we echo back whatever the client asked for if we
# support it, else our own.
_PROTOCOL_VERSION = "2024-11-05"

_SERVER_INFO = {
    "name": "checkmate-precedents",
    "version": "1.1.0",
}


def _log(msg: str) -> None:
    print(f"[checkmate-precedents] {msg}", file=sys.stderr, flush=True)


def _write(obj: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _respond(req_id: Any, result: Any) -> None:
    _write({"jsonrpc": "2.0", "id": req_id, "result": result})


def _error(req_id: Any, code: int, message: str, data: Any = None) -> None:
    err: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    _write({"jsonrpc": "2.0", "id": req_id, "error": err})


def _handle_initialize(req_id: Any, params: dict[str, Any]) -> None:
    client_protocol = params.get("protocolVersion") if isinstance(params, dict) else None
    _respond(
        req_id,
        {
            "protocolVersion": client_protocol or _PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": _SERVER_INFO,
        },
    )


def _handle_tools_list(req_id: Any, _params: dict[str, Any]) -> None:
    _respond(req_id, {"tools": _TOOLS})


def _handle_tools_call(req_id: Any, params: dict[str, Any]) -> None:
    name = params.get("name") if isinstance(params, dict) else None
    args = params.get("arguments", {}) if isinstance(params, dict) else {}
    handler = _HANDLERS.get(name or "")
    if handler is None:
        _error(req_id, -32601, f"Unknown tool: {name}")
        return
    try:
        result = handler(args or {})
    except FileNotFoundError as e:
        result = {"error": f"Precedent corpus unavailable: {e}"}
    except Exception as e:  # noqa: BLE001 — surface any failure as tool output
        result = {"error": f"{type(e).__name__}: {e}"}
    _respond(
        req_id,
        {
            "content": [
                {"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}
            ],
            "isError": "error" in result,
        },
    )


def _handle_ping(req_id: Any, _params: dict[str, Any]) -> None:
    _respond(req_id, {})


_METHODS = {
    "initialize": _handle_initialize,
    "tools/list": _handle_tools_list,
    "tools/call": _handle_tools_call,
    "ping": _handle_ping,
}


def _serve() -> None:
    # Warm up the index so startup errors surface in the logs immediately.
    try:
        _ensure_index()
    except Exception as e:  # noqa: BLE001 — logged, not fatal
        _log(f"startup warning: {e}")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            _log(f"malformed JSON from client: {e}")
            continue

        req_id = msg.get("id")
        method = msg.get("method")
        params = msg.get("params") or {}

        # Notifications have no id; we respond to requests only.
        if method is None:
            continue

        # Handle notifications silently.
        if req_id is None:
            # notifications/initialized and similar; no response expected
            continue

        handler = _METHODS.get(method)
        if handler is None:
            _error(req_id, -32601, f"Method not found: {method}")
            continue

        try:
            handler(req_id, params)
        except Exception as e:  # noqa: BLE001
            _log(f"handler error for {method}: {e}")
            _error(req_id, -32603, f"Internal error: {e}")


if __name__ == "__main__":
    _serve()
