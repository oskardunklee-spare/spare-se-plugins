# Checkmate

Fill and review RFP compliance matrices for Spare's Solutions Engineering team. Replaces Responsive with a workflow tuned to Spare's voice, backed by deterministic per-row precedent lookup against Spare's full past-RFP corpus.

## What's inside

- **`extract-deal-context`**, runs once at the start of a new RFP workflow. Reads the agency's RFP PDF and produces a structured `<agency>-deal-context.md` artifact (agency identity, fleet snapshot, adjacent systems, timeline, scope restrictions, competitive signals, regulatory framework notes) that subsequent drafting sessions reference. The artifact contains facts only; no fit assessments or no-bid recommendations.
- **`fill-rfp-matrix`**, core skill. Pulls the precedent corpus from Drive at session start, then for every row: calls the bundled `search_precedents` tool to retrieve matching past-RFP precedents and drafts the Spare-voiced comment grounded in those precedents. Verdict is `I` (Need More Info) when no precedent meets the similarity threshold, never `N` from silence.
- **`review-rfp-draft`**, companion QA skill. Validates that every cited precedent actually came from `search_precedents` for that row's requirement, catches cross-row comment repetition (>70% text similarity), flags legal/over-disclosure risks, and produces a triage report.
- **`rebuild-precedent-corpus`**, Cowork-native corpus refresher. Walks `Spare General` via the Drive connector, parses every past-RFP matrix, and publishes a fresh `precedents.jsonl` back to Drive. No terminal work required for anyone, including the SE running it.
- **`mcp-servers/precedent-search/`**, a pure-stdlib Python MCP server bundled with the plugin. Loads `precedents.jsonl` from the session cache, Drive-backed cache, or bundled sample (in that order) and exposes `search_precedents` and `corpus_stats` tools. TF-IDF + cosine similarity, zero third-party dependencies, hot-reloads on mtime change.

## Install and set up (first-time)

1. Install the plugin via the Spare SE Plugins marketplace in Cowork.
2. Confirm the Google Drive connector is installed and authenticated in Cowork (Settings, Connectors). No additional auth or Google Cloud setup required.
3. Ask Cowork to run the rebuild skill once:

   > "Rebuild the Checkmate precedent corpus."

   The skill walks `Spare General` via the Drive connector, parses every completed matrix, and writes the corpus back to Drive at `Spare General/_checkmate/precedents.jsonl`. It also caches a local copy at `~/.cache/checkmate/precedents.jsonl` so the current session sees it immediately.

4. Schedule the rebuild to run weekly via Cowork's built-in `schedule` skill:

   > "Schedule the Checkmate precedent rebuild to run every Monday at 6am."

The plugin ships with a 10-row sample `precedents.jsonl` so you can smoke-test the install, but you must run the rebuild once before using Checkmate on a live RFP.

## How to use

- **Start a new RFP**: drop the agency's RFP PDF into Cowork and ask *"Extract the deal context from this RFP."*
- **Fill the matrix**: drop the compliance matrix file in and ask *"Fill this RFP matrix."* Checkmate pulls the current corpus from Drive, calls `search_precedents` for every row, and drafts only from what the search returns.
- **Before submission**: ask *"Review my RFP draft before I submit."* The review skill validates citations, catches repetition, flags legal risks, and produces a ready-to-submit checklist.
- **After submission**: ask *"Rebuild the Checkmate precedent corpus."* (Or let the scheduled job handle it.)

## How the deterministic lookup works

v1.1 replaces prose-based "search Drive for precedents" instructions with a concrete tool call, and the Drive-indexer step with a Cowork-native skill that needs no terminal and no Google Cloud project.

1. `rebuild-precedent-corpus` walks `Spare General` via the Drive connector, extracts every answered row from every completed matrix, and publishes a JSONL corpus back to Drive at `Spare General/_checkmate/precedents.jsonl`.
2. At session start, `fill-rfp-matrix` pulls that file from Drive into `~/.cache/checkmate/precedents.jsonl`.
3. The `checkmate-precedents` MCP server loads the corpus into memory and computes TF-IDF vectors. It hot-reloads on mtime change, so the fresh pull is picked up automatically on the first `search_precedents` call.
4. `fill-rfp-matrix` calls `search_precedents(requirement_text=<row>)` before drafting each row. The tool returns the top-3 nearest matches with similarity scores, verdicts, comment text, and citations.
5. The drafted comment must derive from and cite one of the returned matches. No match above threshold (default 0.3) means the verdict is `I`, not a guess.
6. `review-rfp-draft` re-runs the search on each filled row and verifies the cited precedent appears in the results. Cited precedents that don't appear are flagged as hallucination blockers.

This is how Rule 2 (source every row live) is enforced in code rather than in prose.

## Connectors this plugin expects you to have installed

- **Google Drive**, required. Used by `rebuild-precedent-corpus` to walk `Spare General`, and by `fill-rfp-matrix` to pull the published corpus at session start. Also used for additional cross-references beyond the indexed corpus.
- **Spare documentation MCP**, recommended. Current product-state confirmation ("has this shipped since the last RFP?").
- **Notion**, optional. Roadmap and internal context.
- **Glean**, optional. Klue battlecards and tribal knowledge.

## Rebuilding the corpus

Use the `rebuild-precedent-corpus` skill. It is Cowork-native and needs no terminal, no pip install, and no Google Cloud setup. Re-run weekly (via the `schedule` skill) or whenever a new completed RFP response lands in `Spare General`. The MCP server hot-reloads on the next `search_precedents` call.

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
