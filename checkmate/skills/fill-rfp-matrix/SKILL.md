---
name: fill-rfp-matrix
description: Fill an RFP compliance matrix with Spare-voiced responses, sourced row-by-row from past RFP responses in Google Drive and the Spare documentation MCP. Use when the user asks to "fill the RFP matrix," "respond to the compliance matrix," "draft RFP responses," "answer the requirements matrix," "fill out the spec sheet," or references an incoming `.xlsx` or `.csv` compliance matrix from a transit agency RFP. Also trigger when the user uploads a matrix file and asks for help answering it.
---

# Fill RFP Matrix

Draft Spare's responses to a transit-agency RFP compliance matrix. Every verdict and every comment is sourced from live evidence. The deliverable is the agency's matrix file, filled in the agency's own schema, with internal columns added for the SE to review before stripping and submitting.

## The rule that beats every other rule

**Never make a scope judgment without a source.** Do not output "this isn't a Spare deal" or equivalent language at any level, not per-row, not per-section, not per-matrix. Do not refuse to draft on category grounds. Do not assume a requirement is out of scope because the RFP is labeled EAM, asset management, CAD/AVL, fare, or anything else. Spare's product catalog is broad and updates frequently; the only trustworthy way to determine what Spare supports is to query the live sources for the specific requirement in front of you.

If after searching all sources you cannot find evidence one way or the other, the verdict is `I` (Need More Info) or the agency's equivalent, with reasoning that explains exactly which sources were searched and what was found. Never guess.

## Before drafting any row

### 1. Load deal context

Check the session working directory for a `<agency>-deal-context.md` file produced by the companion `extract-deal-context` skill. If present, load it. If not, run `extract-deal-context` first on the agency's RFP PDF.

### 2. Detect the matrix schema

Identify the requirement column, the verdict column, the comment column, and the agency's verdict vocabulary. Verdict vocabulary lives in hidden sheets, header-row blocks, or data-validation dropdowns; read it from the file, never assume. See `references/schema-detection.md` for detection logic and observed agency layouts.

### 3. Pre-flight scan for stray values

Scan the verdict and comment columns across the full requirement range for pre-existing agency annotations (numeric scores, draft notes, previous-vendor placeholders). Clear them on every row you will fill and on every row you leave unfilled, so the submitted file is unambiguous.

### 4. Isolate template formatting

Every cell you write must explicitly set `Font(bold=False, name="Calibri", size=11)` and `Alignment(wrap_text=True, vertical="top")` on comment cells. openpyxl silently preserves inherited styling otherwise.

### 5. Add the internal review columns

At the right edge of the matrix (two columns past the last agency-defined column), add:

- `Internal Confidence (strip before submit)`, `High` / `Medium` / `Low`, color-coded green/yellow/red
- `Internal Reasoning / Sources (strip before submit)`, plain text listing the specific past RFP row, doc URL, or Notion/Glean hit that backs each answer

Yellow-highlighted bold headers. These columns exist so the SE can audit sourcing quickly. A row with no citation in the reasoning column is a bug.

## Drafting each row

### Mandatory search sequence per row

Every row must go through this sequence before a verdict is assigned. You cannot skip steps. You cannot answer from general knowledge or from this plugin's reference files alone.

**Step 1: Search past RFP responses in Google Drive.** This is the highest-leverage source. A near-identical requirement that Spare has answered before is the strongest possible evidence; it has been through internal review, legal, and commercial sign-off. Search by keyword from the requirement text. Recent completed matrices live in folders named like `<Agency> RFP - Spare EAM Response Matrix`, `Spare's Master Sample RFP Tech Spec Requirements`, `EAM RFP - March 2026`, and similar patterns. Favor responses from the last 12 months over older ones.

**Step 2: Search the Spare documentation MCP.** Authoritative current state of the product. Run keyword searches (`search_spare_documentation`), then read specific `/sales-enablement/*.mdx`, `/customer-enablement/*.mdx`, and `/internal-changelog/*.mdx` pages that look relevant. The Spring 2026 release and the ongoing changelog pages describe what ships now. Always check the changelog for the product area before committing to a "not available" claim; Spare ships frequently and what was absent in a past RFP may now be generally available.

**Step 3: If still ambiguous, search Notion and Glean.** Notion carries internal product context, roadmap, and team knowledge. Glean indexes Slack history, Gong transcripts, Klue battlecards, and cross-source tribal knowledge. Useful for resolving ambiguity or finding a specific SME's recent note.

**Step 4: Only if all three sources come up empty, the verdict is `I` (Need More Info) in the agency's equivalent vocabulary.** Do not default to `N`. An absent source does not prove absent capability. Always cite what was searched and what was not found.

### Every row cites at least one source

The Internal Reasoning column must name the specific source: past RFP filename and row (e.g., `"Laramie RFP - Spare EAM Response Matrix row 3.1.3"`), doc page URL, or Notion/Glean page title and date. If the reasoning says "inferred from..." or "based on general knowledge of Spare EAM..." without a source, the row is not complete.

### Voice

- **Lead with `Spare` or `Spare's`.** First word of every customer-facing comment is `Spare` as a noun or `Spare's` as possessive. Never open with the customer's problem, the capability name, or a generic descriptor.
- **No em dashes.** The em-dash character (`U+2014`) is a known AI-writing tell. Use commas, periods, semicolons, or parentheses.
- **Third-person, product-named.** Spare, not "we." Name the specific product exactly as it appears in the docs or past RFPs (see `references/scope-of-spare.md` for the canonical product catalog).
- **Specific and quantified only when sourced.** If you cite a number (uptime percentage, response interval, customer-adoption metric), the number must come from a doc hit or a past RFP you cited. Do not reuse numbers from this plugin's reference files without re-verifying against a live source; the product changes.
- **Honest about gaps, when the gap is sourced.** A past RFP disclosure or a doc page that says "not currently available" is a legitimate basis for disclosing a gap. An assumption that Spare probably does not do X is not.
- **Weave in the deal context.** Reference the agency's fleet size, adjacent systems, and service modes from the deal-context artifact. Generic answers read as generic.

### Answer registers

Two valid opening registers. Pick per row based on whether the requirement benefits from a "why this matters" hook.

- **Capability-first:** `Spare EAM supports X by...`. Use for short, narrow, factual requirements.
- **Context-first:** `Spare's approach here depends on what the agency is tracking. For X, ... For Y, ...`. Use for multi-dimensional or scope-dependent requirements.

Both open with `Spare` or `Spare's`.

### Reusable answer templates

Structural patterns only, no cached claims. See `references/voice-templates.md`:

- Three-layer template (platform / service / vehicle) for multi-dimensional capability requirements
- Three-tool template for multi-product capability requirements (the specific tools named must come from sourced evidence)
- ERP-partner template for "ability to X or integrate with ERP" requirements when the agency has a separate ERP
- Clarification-request template for genuinely ambiguous or scope-dependent requirements
- Short factual template (capability-first)

### Verdict selection

- Use the exact verdict vocabulary defined by the agency. Never substitute from another matrix.
- The verdict comes from sourced evidence, not from an assumption. A past RFP row saying `Y` to a near-identical requirement is strong support for `Y`. A doc page describing the feature is support for `Y`. Absence of either is not support for `N`; it is support for `I`.
- Reserve partial / "modified" verdicts for genuinely scope-dependent multi-part requirements. Most answers are `Y` or `I`.

### Confidence scoring

- **High (green)**, direct match from past RFP in the same product area within the last 12 months, plus corroboration from current docs.
- **Medium (yellow)**, cited source exists but is older than 12 months, or only one source (past RFP without doc confirmation, or doc without a past RFP precedent), or specific wording needs SME verification.
- **Low (red)**, no direct source; answer constructed from adjacent evidence and explicitly flagged for SME verification. Low-confidence rows are a feature, not a weakness; they tell the SE exactly where to focus review time.

## Output checklist

Before handing off the filled file, verify:

- [ ] No row outputs language like "this isn't a Spare deal," "Spare doesn't do X category," or equivalent without citing a specific source
- [ ] Every filled comment opens with `Spare` or `Spare's`
- [ ] Zero em dashes
- [ ] Every filled cell has `Font(bold=False)` explicitly set
- [ ] Pre-existing stray values in answer columns are cleared
- [ ] Internal Confidence and Internal Reasoning columns present, labeled `(strip before submit)`, color-coded
- [ ] Every filled row has a non-empty Internal Reasoning with at least one source citation (Drive filename + row, or doc URL, or Notion/Glean reference)
- [ ] Section-header rows are untouched
- [ ] Agency's verdict vocabulary used exactly
- [ ] Deal context appears in answers where it adds signal

Run the companion skill `review-rfp-draft` before submission for a full QA pass.

## Reference files

- `references/methodology-rules.md`, the complete rule list, with Rule 0 forbidding unsourced scope judgments
- `references/voice-templates.md`, structural answer patterns
- `references/known-gaps.md`, methodology for disclosing gaps (specific gap claims must be sourced live, not from this file)
- `references/scope-of-spare.md`, the Spare product catalog (names only, for search scaffolding; not an authoritative scope statement)
- `references/competitive-positioning.md`, how to position against named competitors when the deal context names one
- `references/schema-detection.md`, how to detect matrix schema, including observed agency layouts
