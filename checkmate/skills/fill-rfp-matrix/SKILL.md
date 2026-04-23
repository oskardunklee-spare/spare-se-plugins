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

1. **Past RFP responses in `Spare General`**. Already loaded during the mandatory first action. For each row, cross-reference against the precedent matrix: has a similar requirement been answered before? Use that answer's verdict and adapt its language.
2. **Spare documentation MCP**. `search_spare_documentation` with keywords from the row. Read relevant `/sales-enablement/*.mdx`, `/customer-enablement/*.mdx`, `/internal-changelog/*.mdx` pages. Check the changelog before asserting "not available"; Spare ships frequently.
3. **Notion and Glean**. For roadmap, tribal knowledge, Klue battlecards.
4. **Only if all three come up empty, verdict is `I`**, with reasoning naming what was searched. Never `N` from silence. Never "not a Spare deal" at the row level either.

### Every row cites at least one source

Internal Reasoning must name the specific source: Drive file name + row (e.g., `"Laramie RFP - Spare EAM Response Matrix row 3.1.3 answered Y for PM scheduling by time/mileage/hours"`), doc URL, or Notion/Glean reference with date. No source = not complete.

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
