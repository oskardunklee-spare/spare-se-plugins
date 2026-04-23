---
name: fill-rfp-matrix
description: Fill an RFP compliance matrix with Spare-voiced responses. Use when the user asks to "fill the RFP matrix," "respond to the compliance matrix," "draft RFP responses," "answer the requirements matrix," "fill out the spec sheet," or references an incoming `.xlsx` or `.csv` compliance matrix from a transit agency RFP. Also trigger when the user uploads a matrix file and asks for help answering it.
---

# Fill RFP Matrix

Draft Spare's responses to a transit-agency RFP compliance matrix. The deliverable is the agency's matrix file, filled in the agency's own schema, with two internal-only columns added for the SE to review before stripping and submitting.

## Before drafting any row

Do all five of these before writing a single answer. Skipping them produces inconsistent, hard-to-trust output, the exact problem this skill exists to fix.

### 1. Load deal context

Before drafting, check the session working directory for a file named `<agency>-deal-context.md` produced by the companion `extract-deal-context` skill. If present, load it; every row draft should reference fields from it (adjacent systems, fleet snapshot, scope restrictions, competitive signals).

If no deal-context file exists, run `extract-deal-context` first. Do not draft blindly. Ask the user for the agency's RFP PDF if they haven't attached it, then run that skill to produce the artifact.

The deal-context artifact contains at minimum: agency identity, fleet/operations snapshot, financials and scope, adjacent systems the agency has or is procuring (the highest-value section for drafting), timeline, scope restrictions, competitive signals, and risk/fit notes.

### 2. Detect the matrix schema

Open the matrix file and identify:

- **Requirement column**, the text of each question
- **Verdict column**, the compliance verdict (vocabulary varies per agency)
- **Comment/Response column**, the prose response
- **Any Support/Module/Phase columns**, often required alongside the verdict
- **Section-header rows**, rows with text in the requirement column but no expected verdict/comment (e.g., `3.1 Fleet Operations`, `Monitoring and Diagnostics`). Leave these untouched.

Verdict vocabulary is agency-specific. Look for it in:
1. A hidden "Response Options," "Dropdown," or "Instructions" sheet
2. The rows between the title and the data (e.g., MTD defines `Y / Y-ND / N / I` in rows 5–8 before the requirement data starts at row 19)
3. The data validation dropdown on the verdict column

Never assume a verdict vocabulary. Read it from the file.

Common vocabularies observed across agencies:

| Agency | Verdict set |
|---|---|
| HOLON | `Yes / No / Mod` |
| BC Transit | `Yes / No / Other` |
| GRT (MobilityPLUS) | `Fully Meet – Configuration only / Fully Meet – Customization required / Partially Meet – Configuration only / Partially Meet – Customization required / Unable` |
| MTD | `Y / Y-ND / N / I` (plus `F / E` qualifier on Y-ND) |
| Laramie | `Y / N / P` (Partial) |
| PDRTA | no verdict column, prose only |

### 3. Pre-flight scan for stray values

Before filling anything, scan the verdict and comment columns across the full requirement range. Agencies frequently leave:

- Numeric scores or priority rankings from internal reviewers (e.g., MTD had `4` and `1` sitting in the Comments column of rows 19–24 before any proposer touched it)
- Draft text notes (`"custom field"`, `"TBD"`, `"see appendix"`)
- Previous-vendor placeholder data

Clear these explicitly on every row you are going to fill, AND on rows you are leaving unfilled (so it's unambiguous what's your answer versus leftover agency junk). For unfilled rows, leave them visibly blank or mark them `[NOT YET ANSWERED]` if the user asks for a partial fill.

### 4. Isolate template formatting

Template cells often carry inherited font styling (bold, italic, color) that openpyxl silently preserves when you write a value. Every cell you write must explicitly set `Font(bold=False, name="Calibri", size=11)` (or match the template's visible font). Otherwise answers will look different from their neighbors.

Set `Alignment(wrap_text=True, vertical="top")` on every comment cell so long prose wraps correctly.

### 5. Add the internal review columns

At the right edge of the matrix (two columns past the last agency-defined column), add:

- **Column header: `Internal Confidence (strip before submit)`**, values `High` / `Medium` / `Low`, color-coded green/yellow/red
- **Column header: `Internal Reasoning / Sources (strip before submit)`**, plain text listing which past RFP row, Spare doc page, or Notion/Glean hit backed the answer, plus any caveats

Use yellow-highlighted bold headers for both so they visually read as internal metadata. The SE will strip these columns before submitting the matrix to the agency.

## Drafting each row

### Search order for every row

Before writing an answer, do the searches below in order. Stop when you have a confident answer.

1. **Past RFP responses in Google Drive.** This is the highest-leverage source. Prior completed matrices have been through internal review and Spare has committed to the answers. If a near-identical requirement has been answered before, reuse the language with minor adjustments for the new agency's deal context. Recent EAM-focused precedents live in folders like `EAM RFP - March 2026` and in files named `<Agency> - Spare EAM Response Matrix`.
2. **Spare documentation MCP.** Authoritative source for what's in the generally-available product. Good for specific feature claims (custom fields, Open API, mobile app capabilities). Less useful for capability-gap questions.
3. **Notion and Glean.** For roadmap items, product decisions, known limitations, and tribal SE knowledge that hasn't made it to public docs.

### Voice

Follow these rules without exception. Every rule came from a real review cycle on a real matrix.

- **Lead with `Spare` or `Spare's`.** The first word of the customer-facing comment must be `Spare` (as a noun) or `Spare's` (possessive). Never open with the customer's problem, the capability name, or a generic descriptor. *"Spare EAM supports…"* is good. *"Barcode scanning is supported…"* is wrong. *"In an AV deployment…"* is wrong even if it reads well, rework it to open with Spare.
- **No em dashes.** The em-dash character (Unicode `U+2014`) is a known AI-writing tell. Use commas, periods, semicolons, or parentheses instead. Do not generate text with em dashes and then post-hoc replace; generate without them from the start.
- **Third-person, product-named.** Spare, not "we." Name the specific product (`Spare EAM`, `Spare Operations`, `Spare Maintain app`, `Spare Driver App`, `Spare Resolve`, `Spare Analytics`, `Spare Engage`, `Open API`, `Live Map`, `Time Travel`).
- **Specific and quantified.** Cite actual numbers from docs (`every 3-5 seconds`, `99.99% uptime target`, `100% FTA compliance`, `within 30 days`). Vague claims are less trustworthy than narrow specific ones.
- **Honest about gaps.** When a capability isn't there, say so plainly. Example: *"Note: automated warranty expiration notifications are not currently available. Warranty data is stored in the asset record and can be referenced manually or via scheduled reports."* This is a trust-builder, not a weakness. Known gaps are catalogued in `references/known-gaps.md`.
- **Weave in the deal context.** For paratransit deals, reference ADA and rider experience. For AV pilots, reference remote monitoring operators and no-onboard-driver framing. For EAM deals against agencies with a separate ERP, name the ERP (Dynamics 365, Tyler Munis) and position Spare as the integration partner. Generic answers look generic.
- **Length scales with requirement complexity.** Narrow factual asks → 1-2 sentences. Multi-dimensional capabilities → 2-4 paragraphs. Don't pad; don't under-answer.

### Answer registers

Two opening registers exist in the corpus. Pick per row.

- **Capability-first**, `Spare EAM supports X by doing Y...`. Use for short, narrow, factual requirements (`Vehicle status`, `Barcode scanning`, `Export to Excel`). Cleaner, shorter, gets to the point.
- **Context-first**, `Spare's approach here depends on what the agency is tracking. For platform health, ... For vehicle health, ...`. Use for multi-dimensional or ambiguous requirements where different interpretations deserve different answers, and where leading with "why this matters" earns trust.

Both must still open with `Spare` or `Spare's` as the first word.

### Reusable answer templates

See `references/voice-templates.md` for complete templates, including:

- **Three-layer template** (platform health / service operations / vehicle health) for `detect X`, `monitor X`, `report X` requirements
- **Three-tool template** (audit logs / Resolve / EAM) for incident logging, case management, customer feedback requirements
- **ERP-partner template** (for `ability to X or integrate with ERP` requirements when the agency has a separate ERP)
- **Clarification-request template** for genuinely ambiguous or scope-dependent requirements

### Verdict selection

- **Use the best-fit verdict from the agency's vocabulary, not the closest synonym.** If the vocabulary is `Y / Y-ND / N / I`, don't write `P` because a previous matrix used `P`.
- **Reserve "partial" and "modified" verdicts for genuinely scope-dependent multi-part requirements.** Example: HOLON's R48 final-pilot-report requirement spans KPIs, scalability, and lessons learned, all three need agency alignment before committing. `Mod` is right. A simple "does Spare support photo attachments?" is always `Y`, never `P`.
- **Use the "Need More Information" or equivalent verdict when you genuinely cannot resolve the answer from docs + past RFPs.** Better to flag for SME verification than to guess. This is a feature, not a weakness.
- **ERP-adjacent requirements with the agency's ERP named separately in the RFP.** When an agency has explicitly procured a separate ERP (e.g., MTD has Dynamics 365), the right verdict for `ability to X or integrate with ERP` is often the agency's equivalent of `Y` with the Support column set to `TPS` or `Third Party`, and the comment positioning Spare as the integration partner. Do not answer `N` when the agency's own architecture creates a better answer.

### Confidence scoring

For every row you fill, set the Internal Confidence column:

- **High (green)**, Answer directly sourced from a past RFP response + Spare docs, or directly disclosed capability/gap. Verdict is clear from the facts.
- **Medium (yellow)**, Capability is there but specific wording, permission model, or threshold needs SME verification. Or answer is inferred from adjacent capabilities but not documented directly.
- **Low (red)**, No direct source found. Answer based on product reasoning only. SME must verify before submission.

In the Internal Reasoning column, cite the source explicitly: which past RFP row, which Spare doc page URL, which Notion page. When uncertain, say so: *"Inferred from X. Need SME to confirm Y. Flagged Medium."*

This confidence scoring is the primary trust mechanism. An SE should be able to scan a 600-row filled matrix, sort by confidence, and triage only the yellows and reds, not re-verify every row from scratch.

## Output checklist

Before handing off the filled file, verify:

- [ ] Every filled comment opens with `Spare` or `Spare's`
- [ ] Zero em dashes across all filled cells
- [ ] Every filled cell has `Font(bold=False)` set explicitly
- [ ] Pre-existing stray values in answer columns are cleared
- [ ] Internal Confidence and Internal Reasoning columns are present, labeled `(strip before submit)`, and color-coded
- [ ] Section-header rows are untouched
- [ ] Agency's verdict vocabulary is used exactly (no substitutions)
- [ ] Deal context (agency name, adjacent systems, fleet size) appears in answers where it adds signal

Companion skills: `extract-deal-context` runs once at the start of a new RFP workflow to produce the deal-context artifact this skill loads; `review-rfp-draft` runs a structured QA pass (blockers, SME review, style drift, legal/over-disclosure, coverage) before the SE submits the matrix.

## Reference files

- `references/methodology-rules.md`, the complete rule list (15 rules), with the review-cycle origin of each
- `references/voice-templates.md`, three-layer, three-tool, ERP-partner, and clarification-request templates with examples
- `references/known-gaps.md`, capability gaps that must be disclosed honestly (warranty notifications, MPG auto-calc, cost-center billing, etc.)
- `references/schema-detection.md`, how to detect the matrix schema programmatically, including every known agency layout
- `references/competitive-positioning.md`, how to position Spare against named competitors (Fleetio, RTA, AssetWorks, myAvail, others). Primary source is Spare's sales-enablement docs; fall back to Glean for Klue-sourced battlecards when a competitor isn't documented here
