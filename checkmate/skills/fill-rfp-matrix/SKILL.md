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

Verify the required connectors are available before doing anything Drive-shaped:

- **Google Drive connector** (required). Call a lightweight Drive tool (e.g., `list_recent_files` with a small pageSize, or `get_file_metadata` on the Shared Drive root) to confirm it responds. If it doesn't, stop and tell the user: *"Checkmate needs the Google Drive connector to walk Spare General. Install or reconnect it in Cowork Settings → Connectors and try again."*
- **Spare documentation MCP** (recommended). If unavailable, warn but continue; per-row docs corroboration degrades to precedent-only sourcing.

#### 2. Install openpyxl in the sandbox

```bash
pip install openpyxl --break-system-packages 2>&1 | tail -1
```

Only strictly required if Step 5 will run (i.e., files need re-parsing). Run it eagerly anyway; it's cheap and the downstream script will assume it's there.

#### 3. Decide cache status: warm, pre-seeded, or cold

```bash
CACHE="$CLAUDE_PLUGIN_ROOT/data/cache"
mkdir -p "$CACHE"
```

Three branches:

- **Warm start** — `$CACHE/precedents.jsonl` parses and `$CACHE/state.json` is present and valid JSON. This is the normal case after the first fill. Proceed to Step 4 (Drive diff).

- **Pre-seeded warm start** — `$CACHE/precedents.jsonl` parses with more than the 10-row sample, but `$CACHE/state.json` is missing or malformed. The corpus was hand-placed (e.g. seeded after a prior session's walk, or restored from backup) and there is no manifest to diff against. **Do not do a full walk.** Post: *"Found existing corpus (N rows from M files). Bootstrapping state manifest from current Drive state; ready in ~1-2 minutes."* Then:
  - Run Step 4's **resolve-the-root** and **list-Drive-metadata** sub-steps only (no downloads, no parsing).
  - Write `state.json` from the listed files as though this were an up-to-date walk.
  - Skip Steps 5 and 6 entirely. Trust the existing JSONL as-is.
  - Proceed to Step 7.

- **Cold start** — `$CACHE/precedents.jsonl` is missing, empty, or fails to parse. Post: *"No cached corpus found. Walking Spare General now. Expect 15-25 minutes on first run; every fill after this will be seconds unless Drive content changes."* Skip Step 4 and go straight to Step 5 (full walk).

#### 4. Diff Drive against the cache (fast path)

**Resolve the Shared Drive root:**

- **Primary (by hardcoded ID):** call `get_file_metadata` on `fileId = "0AIjutkwbzFjJUk9PVA"` with `supportsAllDrives: true`. Record as `$DRIVE_ROOT_ID`.
- **Backup (by name):** if the hardcoded ID fails, search by name: `q: "name = 'Spare General' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"` with `corpora: "allDrives"`, `supportsAllDrives: true`, `includeItemsFromAllDrives: true`.
- **If both fail:** stop. Report what was tried. Do not draft from the bundled sample.

**List metadata only** (no downloads) for every `.xlsx`, `.csv`, or Google Sheet under `$DRIVE_ROOT_ID` modified in the past 18 months. On every list call pass `supportsAllDrives: true`, `includeItemsFromAllDrives: true`, `corpora: "drive"`, `driveId: $DRIVE_ROOT_ID`. Return just the `{id, name, mimeType, modifiedTime, webViewLink}` tuples. This is a metadata pass, not a download pass — should take 1-3 minutes even on a large drive.

**Compare against `state.json`:**

- `added` = Drive file IDs not in `state.json`
- `changed` = Drive file IDs whose `modifiedTime` in Drive is newer than in `state.json`
- `removed` = file IDs in `state.json` not seen in Drive

**Branch:**

- If `added`, `changed`, and `removed` are all empty: **nothing to do.** Post: *"Corpus is up to date (N rows from M files, last walked <date>). Loading cache."* Skip to Step 6.
- Otherwise: post a status message naming the deltas (e.g. *"3 files changed, 1 added since last fill. Re-parsing 4 files, ~2 minutes."*) and continue to Step 5 with a **targeted rebuild** over just `added ∪ changed`. Remove any rows in `precedents.jsonl` whose `source_id` is in `changed ∪ removed`; keep the rest.

#### 5. Download and parse the target files

Prepare a session scratch dir:

```bash
SCRATCH="$(pwd)/checkmate-rebuild"
rm -rf "$SCRATCH" && mkdir -p "$SCRATCH/downloads"
```

If this is a **cold start**, the target set is every xlsx/csv/Sheet under `$DRIVE_ROOT_ID` modified in the past 18 months (walk it now with BFS, Shared Drive flags as in Step 4). If this is a **targeted rebuild**, the target set is just `added ∪ changed`.

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

#### 6. Rewrite state.json

```bash
python3 -c "
import json
from datetime import datetime, timezone
drive_files = $DRIVE_FILE_LIST_JSON  # list of {id, modifiedTime} from Step 4 (or full walk in cold-start)
state = {
    'last_walk_at': datetime.now(timezone.utc).isoformat(),
    'files': {f['id']: f['modifiedTime'] for f in drive_files},
}
with open('$CACHE/state.json', 'w') as f:
    json.dump(state, f, indent=2)
print('state.json updated')
"
```

#### 7. Confirm the corpus is loaded

Call the `corpus_stats` tool on the `checkmate-precedents` MCP server. Report its output as the grounding note: total rows, unique source files, agencies, year range. The MCP server hot-reloads on mtime change.

If `corpus_stats` returns only the 10-row bundled sample (unique_source_files == 1 AND the sole file name contains "[SAMPLE]"), the cache path wasn't populated. Stop and tell the user. Do not draft from the sample.

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

When you finish the last row, immediately invoke `review-rfp-draft` on the filled file. Read the triage report. If there are blockers (especially repetition blockers from Rule 19, rows whose comments share >55% of text with a previous row), rewrite those specific rows and re-run review until the report is clean. Only then hand the file back to the user.

Do not tell the user "here is your filled matrix, please review" without having run the review skill yourself.

## Reference files

- `references/methodology-rules.md`, the complete rule list (Rule 0 forbids bid/scope judgments; Rule 1 requires the Spare General search anchor)
- `references/voice-templates.md`, structural answer patterns
- `references/known-gaps.md`, how to disclose sourced gaps
- `references/scope-of-spare.md`, canonical product catalog and Drive precedent pointers
- `references/competitive-positioning.md`, how to frame against named competitors
- `references/schema-detection.md`, matrix schema detection and observed agency layouts
