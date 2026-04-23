# checkmate-precedents MCP server

Deterministic per-row precedent lookup for the Checkmate plugin. Loads a
pre-built corpus of past Spare RFP answers and exposes a
`search_precedents` tool that returns the top-k TF-IDF matches for any
given requirement text.

This server is invoked automatically by Checkmate's `fill-rfp-matrix` and
`review-rfp-draft` skills. It is the mechanism by which Rule 2 (source
every row live) is enforced programmatically rather than through prose
instructions that the model can ignore.

## Prerequisites

- Python 3.10+
- `mcp>=1.0.0` (install from `requirements.txt`)
- A built `precedents.jsonl` corpus. Run
  `scripts/build-precedent-index.py` against the `Spare General` Drive
  folder to generate one.

## Installation

```bash
cd <plugin-root>/mcp-servers/precedent-search
pip install -r requirements.txt
```

The plugin's `.mcp.json` already declares this server. Cowork will spawn
it automatically when Checkmate is active, provided the
`CHECKMATE_PRECEDENTS_PATH` environment variable points at a valid
corpus file. That path is set by `.mcp.json` to
`${CLAUDE_PLUGIN_ROOT}/data/precedents.jsonl` by default.

## What the server exposes

### `search_precedents`

Input:
- `requirement_text` (string, required), full text of the matrix row's
  requirement
- `top_k` (integer, default 3)
- `min_similarity` (number, default 0.3)

Output: a JSON object containing the top-k matches, each with
`source_file`, `source_row`, `agency`, `year`, `requirement`, `verdict`,
`comment`, `similarity`, and a ready-to-paste `citation` string.

If no matches meet the similarity threshold, the output includes a
`verdict_hint: "I"` and reasoning explaining that no precedent was
found. The calling skill should use `I` (Need More Info) for that row,
never `N`.

### `corpus_stats`

Returns total row count, source files, agencies, year range, and verdict
distribution for the loaded corpus. Used at the start of a fill run as a
grounding note.

## Implementation notes

- Pure stdlib TF-IDF with cosine similarity. No sklearn dependency.
- Index is built in-memory at process startup from the JSONL file.
  For corpora under about 10,000 rows this completes in well under a
  second; larger corpora may warrant pre-computed vectors persisted
  alongside the JSONL (not implemented in v1.0).
- The server fails loudly when the corpus file is missing or empty.
  Do not silently fall back to general knowledge; that defeats the
  entire purpose.

## Rebuilding the corpus

See `scripts/build-precedent-index.py`. The Checkmate contribution
ritual assumes the corpus is rebuilt weekly, or whenever a new completed
RFP response lands in `Spare General`.
