# checkmate-precedents MCP server

Deterministic per-row precedent lookup for the Checkmate plugin. Loads
the session's precedent corpus (`precedents.jsonl`) and exposes a
`search_precedents` tool that returns the top-k TF-IDF matches for any
given requirement text.

This server is invoked automatically by Checkmate's `fill-rfp-matrix`
and `review-rfp-draft` skills. It is the mechanism by which Rule 2
(source every row live) is enforced programmatically rather than
through prose instructions that the model can ignore.

## No installation required

The server is pure Python stdlib. No `pip install`, no virtualenv, no
MCP package dependency. Any Python 3.10+ runtime that ships with
Cowork or the host OS will work. Cowork spawns it automatically when
Checkmate is active.

## Corpus path resolution

The server looks for `precedents.jsonl` in this order, first hit wins:

1. `$CHECKMATE_PRECEDENTS_PATH`, if set. The plugin does not set this
   by default; it is available for advanced overrides.
2. `~/.cache/checkmate/precedents.jsonl`. This is the expected
   production path. The `fill-rfp-matrix` skill populates it at the
   start of every fill session by walking `Spare General` via the
   Drive connector.
3. `$CLAUDE_PLUGIN_ROOT/data/precedents.jsonl`. The bundled 10-row
   sample. Used for smoke-testing the server and plugin install flow,
   not for real RFP fills.

The server hot-reloads the corpus on every tool call if the file's
mtime has changed, so each fill session's fresh corpus is picked up
automatically without restarting the server.

## What the server exposes

### `search_precedents`

Input:

- `requirement_text` (string, required), full text of the matrix row's
  requirement
- `top_k` (integer, default 3)
- `min_similarity` (number, default 0.3)

Output: a JSON object containing the top-k matches, each with
`source_file`, `source_row`, `agency`, `year`, `requirement`, `verdict`,
`comment`, `similarity`, `url`, and a ready-to-paste `citation` string.

If no matches meet the similarity threshold, the output includes a
`verdict_hint: "I"` and reasoning explaining that no precedent was
found. The calling skill should use `I` (Need More Info) for that row,
never `N`.

### `corpus_stats`

Returns total row count, source files, agencies, year range, verdict
distribution, and the path of the corpus file currently loaded. Used
at the end of the in-session rebuild to confirm the corpus is real
and populated before any row is drafted.

## Implementation notes

- Pure stdlib TF-IDF with cosine similarity. No sklearn dependency.
- MCP JSON-RPC 2.0 implemented directly over stdio (newline-delimited
  JSON, one message per line). No `mcp` package dependency.
- Index is built in-memory at process startup and on hot-reload. For
  corpora under about 10,000 rows this completes in well under a
  second; larger corpora may warrant pre-computed vectors persisted
  alongside the JSONL (not implemented).
- The server fails loudly when no corpus path resolves. Do not
  silently fall back to general knowledge; that defeats the entire
  purpose.

## How the corpus gets populated

The `fill-rfp-matrix` skill walks the `Spare General` Shared Drive via
the Drive connector at the start of every fill, parses every matrix
modified in the past 18 months, and writes the result to
`~/.cache/checkmate/precedents.jsonl`. The server hot-reloads on
mtime and serves from that file for the rest of the session. There is
no persistent shared corpus and no scheduled rebuild; every fill sees
fresh Drive state.
