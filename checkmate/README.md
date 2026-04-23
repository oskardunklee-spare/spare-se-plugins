# Checkmate

Fill and review RFP compliance matrices for Spare's Solutions Engineering team. Replaces Responsive with a workflow tuned to Spare's voice, backed by deterministic per-row precedent lookup against Spare's full past-RFP corpus.

## What's inside

- **`extract-deal-context`**, runs once at the start of a new RFP workflow. Reads the agency's RFP PDF and produces a structured `<agency>-deal-context.md` artifact (agency identity, fleet snapshot, adjacent systems, timeline, scope restrictions, competitive signals, regulatory framework notes) that subsequent drafting sessions reference. The artifact contains facts only; no fit assessments or no-bid recommendations.
- **`fill-rfp-matrix`**, core skill. For every row: calls the bundled `search_precedents` tool to retrieve matching past-RFP precedents from the `Spare General` Drive corpus, then drafts the Spare-voiced comment grounded in those precedents. Verdict is `I` (Need More Info) when no precedent meets the similarity threshold, never `N` from silence.
- **`review-rfp-draft`**, companion QA skill. Validates that every cited precedent actually came from `search_precedents` for that row's requirement, catches cross-row comment repetition (>70% text similarity), flags legal/over-disclosure risks, and produces a triage report.
- **`mcp-servers/precedent-search/`**, a pure-Python MCP server bundled with the plugin. Loads `data/precedents.jsonl` and exposes `search_precedents` and `corpus_stats` tools. TF-IDF + cosine similarity, no heavy dependencies.
- **`scripts/build-precedent-index.py`**, the offline Drive indexer. An SE runs this periodically to walk the `Spare General` folder, parse every matrix, and rebuild `data/precedents.jsonl`.

## Install and set up (first-time)

1. Install the plugin via the Spare SE Plugins marketplace in Cowork.
2. Install the MCP server's Python dependency:

   ```bash
   pip install "mcp>=1.0.0"
   ```

3. Build the precedent corpus (one-time plus weekly afterwards):

   ```bash
   cd <plugin-root>/scripts
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib openpyxl
   python build-precedent-index.py
   ```

   This walks `Spare General` and writes `data/precedents.jsonl`. See `scripts/README.md` for OAuth setup details.

The plugin ships with a 10-row sample `precedents.jsonl` so you can smoke-test without building the full corpus, but you must rebuild with real Drive content before running Checkmate on a live RFP.

## How to use

- **Start a new RFP**: drop the agency's RFP PDF into Cowork and ask *"Extract the deal context from this RFP."*
- **Fill the matrix**: drop the compliance matrix file in and ask *"Fill this RFP matrix."* Checkmate will anchor in `Spare General`, call `search_precedents` for every row, and draft only from what the search returns.
- **Before submission**: ask *"Review my RFP draft before I submit."* The review skill validates citations, catches repetition, flags legal risks, and produces a ready-to-submit checklist.

## How the deterministic lookup works

v1.0 replaces prose-based "search Drive for precedents" instructions with a concrete tool call.

1. `build-precedent-index.py` walks `Spare General`, extracts every answered row from every completed matrix, and writes a JSONL corpus with agency, year, requirement, verdict, comment, and source citation per row.
2. At Checkmate invocation, the `checkmate-precedents` MCP server loads the corpus into memory and computes TF-IDF vectors.
3. `fill-rfp-matrix` calls `search_precedents(requirement_text=<row>)` before drafting each row. The tool returns the top-3 nearest matches with similarity scores, verdicts, comment text, and citations.
4. The drafted comment must derive from and cite one of the returned matches. No match above threshold (default 0.3) means the verdict is `I`, not a guess.
5. `review-rfp-draft` re-runs the search on each filled row and verifies the cited precedent appears in the results. Cited precedents that don't appear are flagged as hallucination blockers.

This is how Rule 2 (source every row live) is enforced in code rather than in prose. The previous versions relied on Claude to follow prose rules; v1.0 relies on a tool call with structured output that Claude cannot fabricate.

## Connectors this plugin expects you to have installed

Checkmate ships its own precedent-search MCP server. It also benefits from these Cowork connectors (not required; the precedent corpus handles most of the lift):

- **Google Drive**, for additional cross-references beyond the indexed corpus
- **Spare documentation MCP**, for current product-state confirmation (useful for "has this shipped since the last RFP?" checks)
- **Notion**, for roadmap and internal context
- **Glean**, for Klue battlecards and tribal knowledge

## Rebuilding the corpus

Re-run `scripts/build-precedent-index.py` weekly, or whenever a new completed RFP response lands in `Spare General`. The MCP server loads the corpus at startup, so changes take effect on the next plugin reload.

## Design principles

The full methodology lives in `skills/fill-rfp-matrix/references/methodology-rules.md`. Short version:

- Invoking Checkmate means the bid decision is already made. No no-bid recommendations or fit-check summaries.
- Every row's first action is a `search_precedents` tool call.
- Every row cites a returned precedent; hallucinated citations are blocked at review.
- Every customer-facing answer leads with `Spare` or `Spare's`. No em dashes.
- No copy-paste across rows; the review skill flags >70% similar comments.
- Honest about gaps only when the gap is sourced from a past RFP or the docs. Never from speculation.

## Known gaps disclosed consistently

See `skills/fill-rfp-matrix/references/known-gaps.md`. This file documents the disclosure patterns, not specific cached gap claims. Specific gaps come from the live precedent corpus.

## Competitive positioning

See `skills/fill-rfp-matrix/references/competitive-positioning.md`.

## Contributing

See `CONTRIBUTING.md` for the post-RFP feedback ritual and the weekly corpus-rebuild cadence.
