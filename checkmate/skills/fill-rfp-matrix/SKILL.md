---
name: fill-rfp-matrix
description: Fill an RFP compliance matrix with Spare-voiced responses, sourced row-by-row from the "Spare General" Google Drive folder (past RFP responses, EAM submissions) and the Spare documentation MCP. Use when the user asks to "fill the RFP matrix," "respond to the compliance matrix," "draft RFP responses," "answer the requirements matrix," "fill out the spec sheet," or references an incoming `.xlsx` or `.csv` compliance matrix from a transit agency RFP. Also trigger when the user uploads a matrix file and asks for help answering it.
---

# Fill RFP Matrix

Draft Spare's responses to a transit-agency RFP compliance matrix. Every verdict and every comment is sourced from live evidence in the `Spare General` Google Drive folder (past RFP responses, EAM submissions) and the Spare documentation MCP. The deliverable is the agency's matrix file, filled in the agency's own schema, with internal columns added for the SE to review before stripping and submitting.

## Ground truth: what Spare ships

**Spare ships a broad product catalog that includes a full Enterprise Asset Management (EAM) product.** If you find yourself about to conclude "Spare doesn't do EAM" or "Spare doesn't do asset management" or "this is not a Spare deal," you are wrong. Check the precedents in Drive.

Spare's product catalog includes:

- **Spare Operations**, demand-response dispatch, routing, and paratransit/microtransit operations
- **Spare EAM**, Enterprise Asset Management with Work Orders, Preventive Maintenance scheduling, Parts Inventory with reorder points, Vendors & Purchasing (POs), Asset Lifecycle tracking, Depreciation, Sub-components (parent/child asset relationships), and a mobile technician app (Spare Maintain)
- **Spare EAM Lite**, lightweight version focused on inspections and issue tracking
- **Spare Resolve**, case management with AI Case Intelligence
- **Spare Eligibility**, rider eligibility and application management
- **Spare Engage**, rider engagement and communications
- **Spare Analytics**, operational reporting and analytics
- **Spare Driver App**, driver-facing mobile app with inspections
- **Spare Rider App**, rider-facing mobile app
- **SpareONE**, multi-modal platform for mixed fixed-route and on-demand
- **Open API**, documented integration surface for third-party systems (ERP, GPS, fare, SSO, GIS, etc.)

Spare has completed EAM-focused RFP responses for multiple agencies. Before concluding that a specific requirement is outside Spare's scope, you must find and consult the relevant precedent in Drive.

## Rule 0: Invoking Checkmate means the bid decision is already made

When the user invokes this skill on a matrix, the go/no-go decision has already been made by the SE and their leadership. **Your job is to source the best answers from past responses and docs, not to decide whether to bid.**

Do not output:

- "This is not a Spare deal" or equivalent at any level
- "Recommend no-bid" / "This appears outside Spare's product domain"
- Option menus asking the user whether to bid, fit-check summaries, or scope-concern warnings
- Hedging preambles about category mismatch

Fit assessment is a separate concern. If the user wants a fit check, they will ask for one explicitly.

If after executing the mandatory search sequence (below) you genuinely cannot find evidence one way or the other for a specific row, the verdict is `I` (Need More Info) in the agency's vocabulary, with reasoning that names the sources searched and what was found. Not a no-bid recommendation.

## Mandatory first action: prepare the precedent corpus

Before opening the matrix, before detecting schema, before anything else. The corpus is cached on disk in the plugin workspace and refreshed incrementally from Drive. Only files that actually changed since the last fill are re-parsed; unchanged Drive = fast path.

### Status reporting convention

Fills take minutes to tens of minutes depending on cache state and matrix size. A silent run is a bad UX; the user is left guessing whether something crashed. **Post short user-facing status messages at every phase transition.** Rules:

- One status line per ~30 seconds of work, more for long phases (the Drive walk, the drafting loop).
- Use simple plain-prose updates. No emojis unless the user has used them first. No elaborate progress bars.
- Prefix milestones with `✓` after completion so the user can scan the thread and see what's done.
- For counting phases (file walk, row drafting), report progress every N items: every 5 matrices during a cold-start walk, every 25 rows during drafting.
- Name the current phase so the user knows where in the pipeline things are: "Pre-flight," "Drive diff," "Parsing," "Drafting," "Review," "Saving."
- Mention concrete estimated-time-remaining when you have enough signal (e.g., after the first file during a cold walk, extrapolate).

Every step below has a **Post to user** callout showing what to say at that transition. Adapt the wording to fit the actual numbers; the intent is consistent communication, not verbatim templating.

### Spare General is a Google Shared Drive

`Spare General` is a Shared Drive (Team Drive), not a My Drive folder. Its root ID starts with `0A`. Every Drive connector call that searches or lists content inside it MUST pass Shared Drive flags or Google returns zero results silently.

```
Shared Drive name: Spare General
Shared Drive root ID: 0AIjutkwbzFjJUk9PVA
```

When calling any Drive connector search or list tool, pass:

- `supportsAllDrives: true`
- `includeItemsFromAllDrives: true`
- `corpora: "drive"` with `driveId: 0AIjutkwbzFjJUk9PVA` (or `"allDrives"` as broader fallback)

If the root ID ever changes, update this file.

### Cache locations (persistent, per-user)

The corpus and its manifest live inside the plugin workspace folder, which is mapped to the user's real disk and persists across sessions:

- `$CLAUDE_PLUGIN_ROOT/data/cache/precedents.jsonl`, the indexed corpus
- `$CLAUDE_PLUGIN_ROOT/data/cache/state.json`, the manifest: `{"last_walk_at": "<ISO>", "files": {<file_id>: <modifiedTime>, ...}}`

Both are gitignored. Each SE has their own copy; nothing is shared via Drive.

### Steps

Execute in order. Do not skip. Do not walk Drive by any mechanism other than the Cowork connector.

#### 1. Pre-flight connector check

**Post to user:** *"Starting Checkmate. Checking required connectors..."*

Verify the required connectors are available before doing anything Drive-shaped:

- **Google Drive connector** (required). Call a lightweight Drive tool (e.g., `list_recent_files` with a small pageSize, or `get_file_metadata` on the Shared Drive root) to confirm it responds. If it doesn't, stop and tell the user: *"Checkmate needs the Google Drive connector to walk Spare General. Install or reconnect it in Cowork Settings → Connectors and try again."* After success, **post to user:** *"✓ Google Drive connector reachable."*
- **Spare documentation MCP** (recommended). If unavailable, warn but continue; per-row docs corroboration degrades to precedent-only sourcing. **Post to user:** *"✓ Spare docs MCP reachable."* on success or *"⚠ Spare docs MCP not available; per-row corroboration will be skipped."* on failure (using `⚠` here is fine; it's a warning character, not an emoji).

#### 2. Install openpyxl in the sandbox

Check first if it's importable; skip the install and the status message if so, to avoid noise.

```bash
python3 -c "import openpyxl" 2>/dev/null || {
  # Only post the install message if we actually need to install.
  echo "installing openpyxl..."
  pip install openpyxl --break-system-packages 2>&1 | tail -1
}
```

**Post to user** only when installing: *"Installing openpyxl (one-time per session)..."* When already present, stay silent.

#### 3. Decide cache status: warm, pre-seeded, or cold

```bash
CACHE="$CLAUDE_PLUGIN_ROOT/data/cache"
mkdir -p "$CACHE"
```

Four branches — **post to user** the matching status message once the branch is decided:

- **Warm start** — `$CACHE/precedents.jsonl` parses, `$CACHE/state.json` is valid JSON, AND `state.json.parser_version` matches the current parser version (`1.3.6`). This is the normal case after the first fill.
  - **Post:** *"✓ Corpus cache is up to date (N rows from M files, built <last_walk_at>). Checking Drive for changes..."*
  - Proceed to Step 4 (Drive diff).

- **Stale-parser cold start** — `$CACHE/precedents.jsonl` exists but `state.json.parser_version` is older than the current parser version, or absent. The corpus was built with a superseded `parse_matrix.py` and may include rows that the current parser would have filtered (internal columns, scratch-note content, etc.).
  - **Post:** *"Corpus was built with parser version <old> (current is 1.3.6). Rebuilding from Spare General to apply new filters. Expect 15-25 minutes."*
  - Force a cold start; skip to Step 5 (full walk).

- **Pre-seeded warm start** — `$CACHE/precedents.jsonl` parses with more than the 10-row sample, but `$CACHE/state.json` is missing or malformed. The corpus was hand-placed (e.g. seeded after a prior session's walk, or restored from backup).
  - **Post:** *"Found existing corpus (N rows from M files). Bootstrapping state manifest from current Drive state; ready in ~1-2 minutes."*
  - Run Step 4's **resolve-the-root** and **list-Drive-metadata** sub-steps only (no downloads, no parsing).
  - Write `state.json` from the listed files (including `parser_version`) as though this were an up-to-date walk.
  - Skip Steps 5 and 6 entirely. Trust the existing JSONL as-is.
  - Proceed to Step 7.

- **Cold start** — `$CACHE/precedents.jsonl` is missing, empty, or fails to parse.
  - **Post:** *"No cached corpus found. Walking Spare General now. Expect 15-25 minutes on first run; every fill after this will be seconds unless Drive content changes."*
  - Skip Step 4 and go straight to Step 5 (full walk).

#### 4. Diff Drive against the cache (fast path)

**Resolve the Shared Drive root:**

- **Primary (by hardcoded ID):** call `get_file_metadata` on `fileId = "0AIjutkwbzFjJUk9PVA"` with `supportsAllDrives: true`. Record as `$DRIVE_ROOT_ID`.
- **Backup (by name):** if the hardcoded ID fails, search by name: `q: "name = 'Spare General' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"` with `corpora: "allDrives"`, `supportsAllDrives: true`, `includeItemsFromAllDrives: true`.
- **If both fail:** stop. Report what was tried. Do not draft from the bundled sample.

**Post to user:** *"Listing files in Spare General (metadata only). This takes 30 seconds to 2 minutes."*

**List metadata only** (no downloads) for every `.xlsx`, `.csv`, or Google Sheet under `$DRIVE_ROOT_ID` modified in the past 18 months. On every list call pass `supportsAllDrives: true`, `includeItemsFromAllDrives: true`, `corpora: "drive"`, `driveId: $DRIVE_ROOT_ID`. Return just the `{id, name, mimeType, modifiedTime, webViewLink}` tuples.

**Post to user:** *"Found N matrices modified in the past 18 months."*

**Compare against `state.json`:**

- `added` = Drive file IDs not in `state.json`
- `changed` = Drive file IDs whose `modifiedTime` in Drive is newer than in `state.json`
- `removed` = file IDs in `state.json` not seen in Drive

**Branch:**

- If `added`, `changed`, and `removed` are all empty: **nothing to do.**
  - **Post:** *"✓ No changes since last walk. Using cached corpus. Ready to draft."*
  - Skip to Step 7 (corpus_stats confirmation).
- Otherwise:
  - **Post:** name the deltas concretely, e.g. *"3 files changed, 1 added, 0 removed since last fill. Re-parsing 4 files (~2 minutes)."*
  - Continue to Step 5 with a **targeted rebuild** over just `added ∪ changed`. Remove any rows in `precedents.jsonl` whose `source_id` is in `changed ∪ removed`; keep the rest.

#### 5. Download and parse the target files

Prepare a session scratch dir:

```bash
SCRATCH="$(pwd)/checkmate-rebuild"
rm -rf "$SCRATCH" && mkdir -p "$SCRATCH/downloads"
```

If this is a **cold start**, the target set is every xlsx/csv/Sheet under `$DRIVE_ROOT_ID` modified in the past 18 months (walk it now with BFS, Shared Drive flags as in Step 4). If this is a **targeted rebuild**, the target set is just `added ∪ changed`.

**Post to user at the start of this step:** the total file count being parsed, e.g. *"Parsing 14 matrices from Spare General."* For cold starts, add an expectation: *"This is the first fill, so all 14 are new. Expect ~20 minutes."* For targeted rebuilds with <5 files, omit the time estimate.

**Post to user every 5 files (or every 5 minutes of wall clock during a cold start, whichever comes first):** the running count, e.g. *"Progress: 5 of 14 matrices parsed. Current: <filename>."* This keeps the user informed during long walks without being chatty.

For each target file:

1. Download via `download_file_content` (or equivalent) with `supportsAllDrives: true`. Save to `$SCRATCH/downloads/<file_id>.<ext>`. For Google Sheets, export as xlsx.
2. Invoke the parser:

   ```bash
   python3 "$CLAUDE_PLUGIN_ROOT/skills/fill-rfp-matrix/scripts/parse_matrix.py" \
       --input "$SCRATCH/downloads/<file_id>.<ext>" \
       --source-file "<original filename from Drive>" \
       --source-id "<drive file id>" \
       --url "<drive webViewLink if available>" \
       --output "$SCRATCH/new_rows.jsonl"
   ```

3. Exit code 0 means rows were written. Exit code 2 means unrecognized matrix (skip). Exit code 3 means parse error (log filename, continue).

**Merge into the cache:**

```bash
# Remove rows whose source_id is in the rebuild set (cold-start: empty; targeted: added∪changed∪removed)
python3 -c "
import json, sys
from pathlib import Path
cache = Path('$CACHE/precedents.jsonl')
rebuild_ids = set(open('$SCRATCH/rebuild_ids.txt').read().split()) if Path('$SCRATCH/rebuild_ids.txt').exists() else set()
keep = []
if cache.exists():
    for line in cache.open():
        line = line.strip()
        if not line: continue
        obj = json.loads(line)
        if obj.get('source_id') not in rebuild_ids:
            keep.append(line)
# Append newly parsed rows
if Path('$SCRATCH/new_rows.jsonl').exists():
    for line in Path('$SCRATCH/new_rows.jsonl').open():
        line = line.strip()
        if line: keep.append(line)
cache.write_text('\n'.join(keep) + '\n')
print(f'merged: {len(keep)} total rows in corpus')
"
```

(Substitute the real `source_id` field if the parser emits it under a different key; current emit is `id` formatted as `<source_id>:<sheet>:<row>`, so split on the first `:`.)

**Post to user after merge completes:** *"✓ Corpus updated: N total rows across M files. Written to local cache."*

#### 6. Rewrite state.json

```bash
python3 -c "
import json
from datetime import datetime, timezone
drive_files = $DRIVE_FILE_LIST_JSON  # list of {id, modifiedTime} from Step 4 (or full walk in cold-start)
state = {
    'parser_version': '1.3.6',  # bump whenever parse_matrix.py filtering logic changes
    'last_walk_at': datetime.now(timezone.utc).isoformat(),
    'files': {f['id']: f['modifiedTime'] for f in drive_files},
}
with open('$CACHE/state.json', 'w') as f:
    json.dump(state, f, indent=2)
print('state.json updated')
"
```

**If `parse_matrix.py` gets new filtering logic (new internal column patterns, new content markers, new schema heuristics), bump the `parser_version` string above AND in the stale-parser-cold-start check in Step 3.** That forces every SE's cache to rebuild cleanly on the next fill without requiring them to manually delete anything.

#### 7. Confirm the corpus is loaded

Call the `corpus_stats` tool on the `checkmate-precedents` MCP server. The MCP server hot-reloads on mtime change.

If `corpus_stats` returns only the 10-row bundled sample (unique_source_files == 1 AND the sole file name contains "[SAMPLE]"), the cache path wasn't populated. Stop and tell the user. Do not draft from the sample.

**Post to user:** the grounding note from `corpus_stats` formatted as a single readable line, e.g. *"Grounding note: 918 rows across 10 source files from 4 agencies (Laramie, Calgary, CBRM, SAMTD), 2025-2026. Ready to draft."*

Only after `corpus_stats` confirms a real, populated corpus do you begin drafting rows.

## Before drafting any row

### 1. Load deal context

Check the session working directory for a `<agency>-deal-context.md` file produced by the companion `extract-deal-context` skill. If present, load it. If not, run `extract-deal-context` first on the agency's RFP PDF.

### 2. Detect the matrix schema

Identify the requirement column, the verdict column, the comment column, and the agency's verdict vocabulary. Read verdict vocabulary from the file (hidden sheets, header-row blocks, or data-validation dropdowns), never assume. See `references/schema-detection.md`.

### 3. Pre-flight scan for stray values

Scan the verdict and comment columns across the full requirement range for pre-existing agency annotations (numeric scores, draft notes, previous-vendor placeholders). Clear them on every row you will fill and on every row you leave unfilled.

### 4. Isolate template formatting

Every cell you write must explicitly set `Font(bold=False, name="Calibri", size=11)` and `Alignment(wrap_text=True, vertical="top")` on comment cells.

**Clear explicit row heights on every row you fill.** Agency templates sometimes set a fixed row height, which causes wrapped text to clip even with `wrap_text=True`. In openpyxl, setting `ws.row_dimensions[r].height = None` removes the height attribute so Excel auto-fits the row on open:

```python
from openpyxl.worksheet.dimensions import RowDimension
# After writing verdict + comment + internal columns on row r:
ws.row_dimensions[r].height = None
# Defensive: if openpyxl's None-assignment gets normalized back, drop the attribute:
if r in ws.row_dimensions and ws.row_dimensions[r].ht is not None:
    ws.row_dimensions[r].ht = None
    ws.row_dimensions[r].customHeight = False
```

Only clear heights on rows you actually fill; do not touch section-header rows or pre-existing unfilled rows.

### 5. Add the internal review columns

Two columns past the last agency-defined column:

- `Internal Confidence (strip before submit)`, `High` / `Medium` / `Low`, color-coded green/yellow/red
- `Internal Reasoning / Sources (strip before submit)`, plain text citing the specific Drive file + row, doc URL, or Notion/Glean hit

Yellow-highlighted bold headers. A row with no citation in the reasoning column is a bug per Rule 2.

## Drafting each row

### Mandatory search sequence per row

**Step 1 is not optional and is not prose-driven. It is a tool call.**

1. **Call `search_precedents`** (the `checkmate-precedents` MCP server bundled with this plugin) with the row's full `requirement_text`. The server performs a TF-IDF search over every past Spare RFP answered in the `Spare General` Drive folder and returns the top 3 matches with similarity scores, verdicts, and comment text. The call looks like:

   ```
   search_precedents(requirement_text="<full text from the matrix row>", top_k=3)
   ```

   The result contains a `matches` array. If it is empty, the server returns a `verdict_hint: "I"` and the row's verdict must be `I` (Need More Info) in the agency's equivalent vocabulary, with reasoning naming what was searched. **Do not draft a `Y` or `N` verdict when the precedent search returned nothing.** This is how Rule 2 is enforced programmatically.

   Every row's Internal Reasoning column must cite at least one of the `source_file` + `source_row` identifiers returned by this call. If you cite a precedent that did not appear in the returned matches, `review-rfp-draft` will flag the row as a blocker.

2. **Spare documentation MCP corroboration (triggered per row, per Rule 25).** Required when ANY of these is true for the row:
   - The top `search_precedents` match has `similarity < 0.5` (weak match; precedents alone probably don't answer the row cleanly)
   - All matching precedents are from more than 12 months ago (staleness risk as product evolves)
   - The requirement falls into a product-change-sensitive category. Scan the requirement text (case-insensitive) for these keyword groups:
     - **Integration / API:** `integration`, `interoperability`, `API`, `interface`, `exchange`, `feed`, `SSO`, `webhook`, `connector`, `import`, `export`
     - **Security / compliance:** `security`, `compliance`, `audit`, `SOC`, `HIPAA`, `PCI`, `FIPS`, `PII`, `encryption`, `access control`, `penetration`
     - **Eligibility / ADA:** `eligibility`, `ADA`, `paratransit` (when in an eligibility / applications / assessment context)
     - **Roadmap / future-state:** `roadmap`, `future`, `planned`, `upcoming`, `next release`, `coming soon`
   
   When triggered: call `search_spare_documentation` with keywords from the row and read relevant `/sales-enablement/*.mdx`, `/customer-enablement/*.mdx`, `/internal-changelog/*.mdx` pages. Use the returned content to confirm or revise the precedent-based answer. Cite any doc URL used in the Internal Reasoning column alongside the precedent citation.
   
   When NOT triggered (precedent is strong, recent, and the requirement is in a category with low drift risk): proceed from the precedent alone. The precedent is the source of truth.

3. **Notion and Glean (triggered per row, per Rule 25).** Required when ANY of these is true:
   - `search_precedents` returned no matches above threshold (the row would otherwise be `I`)
   - The row names a specific competitor or requests competitive positioning (Klue battlecards via Glean)
   - The row asks about internal roadmap, product strategy, or launch timing
   
   When triggered: search via the Glean and Notion connectors. Cite any Klue battlecard or Notion page URL in the Internal Reasoning column.

4. **Verdict is `I` only when** `search_precedents` returned no matches AND (if triggered) the docs MCP and Glean are silent on the specific capability. Never `N` from silence. Never "not a Spare deal" at the row level.

### `corpus_stats` is already your grounding note

The `corpus_stats` call at the end of the in-session rebuild doubles as your grounding note for the user: row count, source files, agencies, year range. If the corpus is empty or the server reports an error, stop and tell the user. Do not continue on the bundled sample corpus.

### Every row cites at least one source

Internal Reasoning must name a specific citation returned by `search_precedents` for that row: the `citation` field of a match, which looks like `"Laramie RFP - Spare EAM Response Matrix (Updated) row Sheet1 row 5 (Laramie 2026)"`. Include the `similarity` score so the reviewer can judge match quality. Optionally add a doc URL from the Spare documentation MCP if one was used.

A reasoning note that does not include a citation returned by `search_precedents` is a bug, caught automatically by `review-rfp-draft`.

### Voice

- **Lead with `Spare` or `Spare's`.** First word.
- **No em dashes** (`U+2014`).
- **Third-person, product-named.** Use canonical product names from the catalog above.
- **Specific and quantified only when sourced.** Numbers come from live sources, not from this file.
- **Honest about gaps, when the gap is sourced.**
- **Weave in deal context** from the deal-context artifact.

### Answer registers

- **Capability-first** for short factual requirements.
- **Context-first** for multi-dimensional requirements.

Both open with `Spare` or `Spare's`.

### Reusable templates

Structural only, see `references/voice-templates.md`. Specific products/numbers inside the templates come from cited sources.

### Verdict selection

- Use the agency's exact vocabulary.
- Verdict comes from sourced evidence. `Y` from a past RFP precedent match. `Y-ND` / `P` / agency equivalent when sourced as partial. `I` when all sources are silent. Never `N` from silence.
- Never output bid/scope judgments at any granularity.

### Confidence scoring

- **High (green)**, direct match in `Spare General` past RFP from the last 12 months, corroborated by current docs
- **Medium (yellow)**, older or single-source match, or wording needs SME verification
- **Low (red)**, constructed from adjacent evidence; flag for SME

## Status reporting during drafting

A 300-row matrix takes many minutes to draft. The user needs visible progress, not silence.

**Post to user at the start of drafting:** the total scope, e.g. *"Drafting 312 requirement rows across 7 sections. Posting progress updates every 25 rows."*

**Post to user every 25 rows drafted:** the running count and current section name, e.g. *"Progress: 50 of 312 rows drafted. Currently on section 2 (Asset Setup)."*

**Post to user on notable events:**
- When a row gets verdict `I` because no precedent matched: *"Row 47: no precedent above threshold. Marked I (Need More Info)."* Don't flood on this; summarize at section boundaries if there are many.
- When a row triggered docs / Glean corroboration per Rule 25: *"Row 82 triggered docs corroboration (integration keyword). Pulling current docs..."* Again, keep brief.
- When moving to a new section: *"Starting section 3 (Work Orders), rows 89-144."*

The goal is the user can glance at the thread at any point and see where things are, what's normal, and what's an edge case. Don't over-report; one substantive line per 30-60 seconds of work is about right.

## Output checklist

- [ ] Grounding note at the start identifies which `Spare General` precedent files were loaded
- [ ] No output language implying bid/fit/scope concerns (Rule 0)
- [ ] Every filled row cites at least one source in Internal Reasoning
- [ ] Every filled comment opens with `Spare` or `Spare's`
- [ ] Zero em dashes
- [ ] `Font(bold=False)` set explicitly on every written cell
- [ ] Row heights cleared on every filled row so wrapped text auto-fits on open
- [ ] Pre-existing stray values cleared
- [ ] Internal Confidence and Reasoning columns present, color-coded, labeled `(strip before submit)`
- [ ] Section-header rows untouched
- [ ] Agency's verdict vocabulary used exactly
- [ ] Deal context woven in where it adds signal

## Finishing a fill

**The fill is not complete until `review-rfp-draft` has run on the output file and returned a clean triage report.** This is not a separate optional step; it is part of the drafting workflow (Rule 20).

When you finish the last row, **post to user:** *"✓ All 312 rows drafted. Running review now."*

Immediately invoke `review-rfp-draft` on the filled file. Read the triage report. **Post to user** a compact summary of results, e.g. *"Review complete. 3 blockers, 8 SME-review items, 12 style flags."*

If there are blockers (especially repetition blockers from Rule 19, rows whose comments share >55% of text with a previous row, or Rule 23/26/27 blockers from requirement-splicing, scratch-note leakage, or broken openers), **post to user** the specific fix plan, e.g. *"Addressing 3 blockers: row 47 and row 49 share 62% text (re-drafting row 49); row 82 has a Microsoft Dynamics 365 reference not in deal context (removing); row 103 opens with 'Spare's within...' (rewriting). Re-running review after fixes."*

Rewrite the specific rows and re-run review until the report is clean. **Post to user** once clean: *"✓ Clean review. Matrix ready."*

Only then hand the file back to the user.

**Post to user at final handoff:** the file location and what the SE should do next, e.g. *"Matrix saved to <path>. Ready for your review before submission. The Internal Confidence and Internal Reasoning / Sources columns are labeled 'strip before submit' — remove those before sending to the agency."*

Do not tell the user "here is your filled matrix, please review" without having run the review skill yourself.

## Reference files

- `references/methodology-rules.md`, the complete rule list (Rule 0 forbids bid/scope judgments; Rule 1 requires the Spare General search anchor)
- `references/voice-templates.md`, structural answer patterns
- `references/known-gaps.md`, how to disclose sourced gaps
- `references/scope-of-spare.md`, canonical product catalog and Drive precedent pointers
- `references/competitive-positioning.md`, how to frame against named competitors
- `references/schema-detection.md`, matrix schema detection and observed agency layouts
