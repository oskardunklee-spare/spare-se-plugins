# Checkmate

Fill and review RFP compliance matrices for Spare's Solutions Engineering team. Replaces Responsive with a workflow tuned to Spare's voice, backed by deterministic per-row precedent lookup built fresh from Spare's full past-RFP corpus at the start of every fill session.

## What's inside

- **`extract-deal-context`**, runs once at the start of a new RFP workflow. Reads the agency's RFP PDF and produces a structured `<agency>-deal-context.md` artifact (agency identity, fleet snapshot, adjacent systems, timeline, scope restrictions, competitive signals, regulatory framework notes) that subsequent drafting sessions reference. The artifact contains facts only; no fit assessments or no-bid recommendations.
- **`fill-rfp-matrix`**, core skill. First action is an in-session rebuild: walks the `Spare General` Shared Drive via the Drive connector, parses every past-RFP matrix, and writes a fresh `precedents.jsonl` to `~/.cache/checkmate/precedents.jsonl`. Then for every row: calls the bundled `search_precedents` tool to retrieve matching past-RFP precedents and drafts the Spare-voiced comment grounded in those precedents. Verdict is `I` (Need More Info) when no precedent meets the similarity threshold, never `N` from silence.
- **`review-rfp-draft`**, companion QA skill. Validates that every cited precedent actually came from `search_precedents` for that row's requirement, catches cross-row comment repetition (>70% text similarity), flags legal/over-disclosure risks, and produces a triage report.
- **`mcp-servers/precedent-search/`**, a pure-stdlib Python MCP server bundled with the plugin. Loads the local session corpus and exposes `search_precedents` and `corpus_stats` tools. TF-IDF + cosine similarity, zero third-party dependencies, hot-reloads on mtime change.

## Install and set up

1. Install the plugin via the Spare SE Plugins marketplace in Cowork.
2. Confirm the Google Drive connector is installed and authenticated in Cowork (Settings, Connectors). No additional auth or Google Cloud setup required.

That's it. No separate corpus-building step, no shared file to manage, no weekly schedule to configure. The first time you fill a matrix, Checkmate walks Spare General (15-25 minutes) and caches the result locally at `checkmate/data/cache/precedents.jsonl` inside the plugin workspace folder on your Mac. Every subsequent fill does a quick metadata-only diff against Drive (seconds) and re-parses only files that actually changed.

The cache is per-user, never shared, and gitignored. Each SE's first fill pays the one-time cost; after that, fills start in seconds unless Spare General content changes.

The plugin ships with a 10-row sample `precedents.jsonl` for smoke-testing the install; real fills never use it.

## How to use

- **Start a new RFP**: drop the agency's RFP PDF into Cowork and ask *"Extract the deal context from this RFP."*
- **Fill the matrix**: drop the compliance matrix file in and ask *"Fill this RFP matrix."* Checkmate will walk Spare General, build the corpus in-session, and then draft every row with `search_precedents`.
- **Before submission**: ask *"Review my RFP draft before I submit."* The review skill validates citations, catches repetition, flags legal risks, and produces a ready-to-submit checklist.

## How the deterministic lookup works

1. At the start of every fill, `fill-rfp-matrix` walks the `Spare General` Shared Drive via the Drive connector (Shared Drive flags required; root ID `0AIjutkwbzFjJUk9PVA`). By default it only walks matrices modified in the past 18 months.
2. Every discovered `.xlsx`, `.csv`, or Google Sheet is downloaded and parsed by a bundled Python script. Every answered row is extracted as a `(requirement, verdict, comment)` tuple with source metadata.
3. The extracted rows are written to `~/.cache/checkmate/precedents.jsonl` (session-scoped cache).
4. The `checkmate-precedents` MCP server hot-reloads the corpus into memory and indexes it with TF-IDF vectors.
5. For each matrix row, `fill-rfp-matrix` calls `search_precedents(requirement_text=<row>)`. The tool returns the top-3 nearest matches with similarity scores, verdicts, comment text, and citations.
6. The drafted comment must derive from and cite one of the returned matches. No match above threshold (default 0.3) means the verdict is `I`, not a guess.
7. `review-rfp-draft` re-runs the search on each filled row and verifies the cited precedent appears in the results. Cited precedents that don't appear are flagged as hallucination blockers.

Rule 2 (source every row live) is enforced in code rather than in prose. A tool call with structured output cannot be faked by the model.

## Why local cache + change detection instead of a shared corpus?

Spare General content can change during the day. Checkmate detects changes via a metadata-only Drive list at the start of every fill, re-parses only the files that actually changed, and keeps the rest of the cache as-is. That gives you "always fresh" without paying the cost of a full rebuild on every session. It also eliminates an entire category of plumbing (shared folder permissions, Drive publish step, scheduled refresh jobs) that earlier architectures struggled with. Each SE's cache is their own, per-user, gitignored, and never shared.

## Connectors this plugin expects you to have installed

- **Google Drive**, required. Used to walk `Spare General` at the start of every fill.
- **Spare documentation MCP**, recommended. Current product-state confirmation ("has this shipped since the last RFP?").
- **Notion**, optional. Roadmap and internal context.
- **Glean**, optional. Klue battlecards and tribal knowledge.

## Design principles

The full methodology lives in `skills/fill-rfp-matrix/references/methodology-rules.md`. Short version:

- Invoking Checkmate means the bid decision is already made. No no-bid recommendations or fit-check summaries.
- Every fill starts with a live walk of `Spare General`. No stale caches.
- Every row's first action is a `search_precedents` tool call.
- Every row cites a returned precedent; hallucinated citations are blocked at review.
- Every customer-facing answer leads with `Spare` or `Spare's`. No em dashes.
- No copy-paste across rows; the review skill flags >70% similar comments.
- Honest about gaps only when the gap is sourced from a past RFP or the docs. Never from speculation.

## Known gaps disclosed consistently

See `skills/fill-rfp-matrix/references/known-gaps.md`. This file documents the disclosure patterns, not specific cached gap claims. Specific gaps come from the live per-session corpus.

## Competitive positioning

See `skills/fill-rfp-matrix/references/competitive-positioning.md`.

## Contributing

See `CONTRIBUTING.md` for the post-RFP feedback ritual.
