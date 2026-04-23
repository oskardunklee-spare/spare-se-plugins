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

## Mandatory first action: anchor in Spare General

Before opening the matrix, before detecting schema, before anything else:

1. **Use the Google Drive search tool to locate the folder titled `Spare General`.** This is the team's master Drive folder. Everything downstream sources from here.
2. **List the contents of `Spare General`.** Look for subfolders related to the RFP category at hand. For EAM RFPs, look for folders named like `EAM RFP - <date>`, `Potential EAM RFP`, `<Agency> EAM RFP`, or files named with `EAM` in the title.
3. **Read at least one completed EAM (or domain-equivalent) response matrix in full before drafting any row.** Known precedents include: `Laramie RFP - Spare EAM Response Matrix`, `Calgary_EAM_Specs_with_Responses_SpareOnly_updated.csv`, `TCAT EAM RFP`, `SolTrans EAM RFP`, `NFTA EAM RFP`, `Valley Transit EAM RFP`, and `Spare's Master Sample RFP Tech Spec Requirements`. If the incoming RFP is not EAM-focused, adapt the search to the relevant category (paratransit, microtransit, fixed-route, fare, rider experience) but always start from `Spare General`.
4. **Do not begin drafting until you have named at least one concrete precedent file from `Spare General` that you will use as a source.** Your first output, before any row is filled, should be a short "grounding note" identifying which Drive files you loaded and what they cover.

If you cannot locate `Spare General` or any EAM precedent within it, stop and tell the user; do not fall back to general knowledge.

## Before drafting any row

### 1. Load deal context

Check the session working directory for a `<agency>-deal-context.md` file produced by the companion `extract-deal-context` skill. If present, load it. If not, run `extract-deal-context` first on the agency's RFP PDF.

### 2. Detect the matrix schema

Identify the requirement column, the verdict column, the comment column, and the agency's verdict vocabulary. Read verdict vocabulary from the file (hidden sheets, header-row blocks, or data-validation dropdowns), never assume. See `references/schema-detection.md`.

### 3. Pre-flight scan for stray values

Scan the verdict and comment columns across the full requirement range for pre-existing agency annotations (numeric scores, draft notes, previous-vendor placeholders). Clear them on every row you will fill and on every row you leave unfilled.

### 4. Isolate template formatting

Every cell you write must explicitly set `Font(bold=False, name="Calibri", size=11)` and `Alignment(wrap_text=True, vertical="top")` on comment cells.

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

2. **Spare documentation MCP**, for feature corroboration and "not currently available" checks. Run after Step 1, to confirm the precedent is still accurate given any recent product changes. `search_spare_documentation` with keywords from the row; read relevant `/sales-enablement/*.mdx`, `/customer-enablement/*.mdx`, `/internal-changelog/*.mdx` pages.

3. **Notion and Glean**, for tribal knowledge, Klue battlecards, or roadmap questions the precedents and docs do not answer.

4. **Verdict is `I` only when** `search_precedents` returned no matches AND the docs MCP is silent on the specific capability. Never `N` from silence. Never "not a Spare deal" at the row level.

### Before drafting any row: run `corpus_stats`

Before the first row is drafted, call the `corpus_stats` tool on the `checkmate-precedents` MCP server to confirm the precedent corpus is loaded and populated. Include its output as your grounding note (how many rows, how many source files, which agencies, year range). If the corpus is empty or the server reports an error, stop and tell the user to run `scripts/build-precedent-index.py`.

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
- [ ] Pre-existing stray values cleared
- [ ] Internal Confidence and Reasoning columns present, color-coded, labeled `(strip before submit)`
- [ ] Section-header rows untouched
- [ ] Agency's verdict vocabulary used exactly
- [ ] Deal context woven in where it adds signal

## Finishing a fill

**The fill is not complete until `review-rfp-draft` has run on the output file and returned a clean triage report.** This is not a separate optional step; it is part of the drafting workflow (Rule 20).

When you finish the last row, immediately invoke `review-rfp-draft` on the filled file. Read the triage report. If there are blockers (especially repetition blockers from Rule 19, rows whose comments share >70% of text with a previous row), rewrite those specific rows and re-run review until the report is clean. Only then hand the file back to the user.

Do not tell the user "here is your filled matrix, please review" without having run the review skill yourself.

## Reference files

- `references/methodology-rules.md`, the complete rule list (Rule 0 forbids bid/scope judgments; Rule 1 requires the Spare General search anchor)
- `references/voice-templates.md`, structural answer patterns
- `references/known-gaps.md`, how to disclose sourced gaps
- `references/scope-of-spare.md`, canonical product catalog and Drive precedent pointers
- `references/competitive-positioning.md`, how to frame against named competitors
- `references/schema-detection.md`, matrix schema detection and observed agency layouts
