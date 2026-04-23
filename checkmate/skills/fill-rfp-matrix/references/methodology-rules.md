# Methodology Rules

Each rule below came from a real review cycle on a real matrix. Follow all of them; if one seems wrong for a specific row, escalate to the SE rather than overriding silently.

## Rule 1, Detect agency-specific verdict vocabulary

Never assume the verdict set. Read it from the matrix. It may live in a hidden "Response Options" sheet, a "Dropdown" sheet, a "Data Validation" on the verdict column, or in the rows between the title and the data. See `schema-detection.md` for detection logic.

Vocabularies observed so far: `Yes/No/Mod`, `Yes/No/Other`, `Fully Meet – Configuration only / Fully Meet – Customization required / Partially Meet – Configuration only / Partially Meet – Customization required / Unable`, `Y/Y-ND/N/I` (with `F/E` qualifier), `Y/N/P`, prose-only.

## Rule 2, Detect and skip section-header rows

Section-header rows have a short label in the requirement column and no expected verdict or comment. Example from HOLON: `3.1 Fleet Operations`, `System Deployment`, `Monitoring and Diagnostics`. Example from GRT: separate `Requirement Area` and `Requirement Sub Area` columns carry the same information. Leave these rows untouched. Filling them is a clear tell that the output was auto-generated without schema awareness.

## Rule 3, Pre-flight scan for stray values

Agencies often publish matrices with stray numeric scores, draft notes, or previous-vendor placeholders sitting in the answer columns. Example: the MTD matrix had `4`, `1`, and `custom field` in column K of rows 19-24 before any proposer touched it. Clear these explicitly on every row you fill, and on rows you leave unfilled, so the submitted file is unambiguous.

## Rule 4, Explicit format isolation

Every cell you write must set `Font(bold=False, name="Calibri", size=11)` explicitly (or match the template's visible neighbor font). openpyxl silently preserves inherited bold, italic, and color, which will make your answers visually different from their neighbors. Also set `Alignment(wrap_text=True, vertical="top")` on comment cells.

## Rule 5, Lead every customer-facing comment with `Spare` or `Spare's`

The first word must be `Spare` (as a noun) or `Spare's` (possessive). Never open with the requirement topic, a generic descriptor, or the customer's context. The possessive form satisfies the rule: *"Spare's approach here depends on..."* is fine. *"In an AV deployment..."* is not, even if the rest of the answer is good, rework it.

## Rule 6, No em dashes

The em-dash character (Unicode `U+2014`, the `\u2014` codepoint) is a known AI-writing tell. Use commas, periods, semicolons, parentheses, or restructured sentences instead. Do not generate text with em dashes and then run find-and-replace; that produces awkward grammar. Generate without them from the start.

## Rule 7, Be honest about gaps

When a capability is not available, disclose it plainly. Example: *"Note: automated warranty expiration notifications are not currently available. Warranty data is stored in the asset record and can be referenced manually or via scheduled reports."* Known gaps are documented in `known-gaps.md`. Never overclaim, that's the exact trust problem this skill exists to fix.

## Rule 8, Use clarification-request phrasing for genuinely ambiguous requirements

When a requirement could be interpreted multiple ways (platform health vs vehicle health, service-level vs AV-telemetry), answer what Spare can do for each interpretation and close with: *"We would welcome clarification from the agency on which aspects are most relevant to this requirement."* This reframes ambiguity as partnership rather than evasion, and it's a signature Spare move across the corpus.

## Rule 9, Add internal-only Confidence and Reasoning columns

At the right edge of the matrix, two columns past the last agency-defined column, add:
- `Internal Confidence (strip before submit)`, values `High` / `Medium` / `Low`, color-coded
- `Internal Reasoning / Sources (strip before submit)`, plain text citing past RFP row, doc URL, or Notion page

Yellow-highlighted bold headers for both. The `(strip before submit)` suffix is mandatory so the SE doesn't accidentally submit them.

## Rule 10, Confidence rubric

- `High` (green), Directly sourced from past RFP + Spare docs, or a directly-disclosed gap. Verdict is clear from the facts.
- `Medium` (yellow), Capability is there but specific wording, permission model, or threshold needs SME verification.
- `Low` (red), No direct source. Answer based on product reasoning alone. SME must verify before submission.

## Rule 11, ERP-partner framing when the agency has a separate ERP

When an agency has explicitly procured a separate ERP (MTD → Dynamics 365, Laramie referenced Tyler Munis), requirements phrased `ability to X or integrate with ERP to fulfill this requirement` should be answered with the agency's equivalent of `Y`, `Support = TPS/Third Party`, and a comment positioning Spare as the integration partner. Do not answer `N` when the agency's own stated architecture creates a better answer.

## Rule 12, `Spare's` counts

Rule 5 accepts both `Spare` and `Spare's` as the opening word. *"Spare's approach here..."* / *"Spare's Open API supports..."* are valid openings. Earlier drafts rejected the possessive form; this was too strict.

## Rule 13, Weave the deal context explicitly

Agency-specific framing separates trustworthy answers from generic filler. For paratransit deals, name ADA and rider experience. For AV pilots, name remote monitoring operators and the no-onboard-driver reality. For EAM deals, name the agency's ERP (Dynamics 365, Tyler Munis), their implementation partner (Crowe), and the fleet characteristics (`145 vehicles`, `11,000 work orders/year`, `24/7 maintenance ops`). Load this context from the agency's RFP PDF at the start.

## Rule 14, Capability-first vs context-first opening, picked per row

Two opening registers co-exist in the corpus. Both are valid.

- *Capability-first*: `Spare EAM supports X by...`, use for short, narrow, factual requirements.
- *Context-first*: `Spare's approach here depends on what the agency is tracking. For platform health, ... For vehicle health, ...`, use for multi-dimensional or ambiguous requirements, where leading with "why this matters" earns trust.

Both must still open with `Spare` or `Spare's`.

## Rule 15, Three-layer and three-tool templates are reusable

Multi-dimensional capability requirements (detect, monitor, report) map cleanly to a three-layer answer: platform / service / vehicle. Multi-tool requirements (incident logging, case management, reporting) map cleanly to a three-tool answer: audit logs / Spare Resolve / Spare EAM. Recognize these patterns and reach for the templates in `voice-templates.md`.
