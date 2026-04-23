# Methodology Rules

Rules are numbered for reference. Rule 0 overrides everything else. Each rule came from a real review cycle on a real matrix or from a real failure mode in production.

## Rule 0, Never make an unsourced scope judgment

Do not output language like "this is not a Spare deal," "Spare does not do X category," "this RFP is outside Spare's product domain," or equivalent, at any level (per-row, per-section, per-matrix). Do not refuse to draft on category grounds. Do not assume a requirement is out of scope because the RFP is labeled EAM, asset management, fare, CAD/AVL, or anything else.

The only way to determine whether Spare supports a specific requirement is to search the live sources (Drive past RFPs, Spare docs MCP, Notion, Glean) for that specific requirement. Spare's product catalog is broad and updates frequently; category-level intuition is not a reliable signal and has produced wrong outputs in the past.

If after searching all sources you cannot find evidence one way or the other, the verdict is `I` (Need More Info) in the agency's vocabulary, with reasoning that names the sources searched and what was found. Never guess, never decline, never category-judge.

## Rule 1, Source every row live, in this order

For every row, search in this sequence before assigning a verdict:

1. Past RFP responses in Google Drive (highest leverage; battle-tested language)
2. Spare documentation MCP (current product state; check `/internal-changelog/` for recent shipments)
3. Notion and Glean (internal context, roadmap, Klue battlecards, Slack/Gong tribal knowledge)

Only if all three come up empty, verdict is `I`. Do not answer from general knowledge or from this plugin's reference files alone.

## Rule 2, Cite the source in every row

The Internal Reasoning column must name the specific source: past RFP filename and row, doc page URL, or Notion/Glean page title and date. A reasoning note that says "inferred from..." or "based on general knowledge of Spare..." without a citation is not complete.

## Rule 3, Detect agency-specific verdict vocabulary

Never assume the verdict set. Read it from the matrix. It may live in a hidden "Response Options" sheet, a "Dropdown" sheet, data validation on the verdict column, or rows between the sheet title and the data. See `schema-detection.md` for detection logic.

## Rule 4, Detect and skip section-header rows

Section-header rows have a short label in the requirement column and no expected verdict or comment. Leave them untouched. Filling them is a clear tell that the output was auto-generated without schema awareness.

## Rule 5, Pre-flight scan for stray values

Agencies often publish matrices with stray numeric scores, draft notes, or previous-vendor placeholders in the answer columns. Clear these explicitly on every row you fill and on every row you leave unfilled, so the submitted file is unambiguous.

## Rule 6, Explicit format isolation

Every cell you write must set `Font(bold=False, name="Calibri", size=11)` explicitly (or match the template's visible neighbor font). openpyxl silently preserves inherited bold, italic, and color. Also set `Alignment(wrap_text=True, vertical="top")` on comment cells.

## Rule 7, Lead every customer-facing comment with `Spare` or `Spare's`

First word of the customer-facing comment must be `Spare` (noun) or `Spare's` (possessive). Never open with the requirement topic, a generic descriptor, or the customer's context.

## Rule 8, No em dashes

The em-dash character (`U+2014`) is a known AI-writing tell. Use commas, periods, semicolons, parentheses, or restructured sentences.

## Rule 9, Be honest about gaps, when the gap is sourced

When a past RFP or a Spare docs page explicitly discloses a gap, surface it in the response using one of the patterns in `known-gaps.md`. When you have no source for a gap, the verdict is `I`, not `N` with a guessed-at gap explanation. An assumption that Spare probably does not do X is not a gap disclosure; it is a hallucination.

## Rule 10, Clarification-request phrasing for genuinely ambiguous requirements

When a requirement could be interpreted multiple ways (platform health vs. vehicle health, service-level vs. AV-telemetry), answer what Spare can do for each interpretation and close with: *"We would welcome clarification from the agency on which aspects are most relevant to this requirement."* This reframes ambiguity as partnership, not evasion.

## Rule 11, Internal Confidence and Reasoning columns are mandatory

At the right edge of the matrix (two columns past the last agency-defined column), add:
- `Internal Confidence (strip before submit)`, values High / Medium / Low, color-coded
- `Internal Reasoning / Sources (strip before submit)`, plain text citing at least one source

Yellow-highlighted bold headers. The `(strip before submit)` suffix is mandatory so the SE does not accidentally submit them.

## Rule 12, Confidence rubric

- `High` (green): direct match from a past RFP in the same product area within the last 12 months, plus corroboration from current docs.
- `Medium` (yellow): cited source exists but is older than 12 months, or only one source, or specific wording needs SME verification.
- `Low` (red): no direct source, answer constructed from adjacent evidence. Explicitly flagged for SME verification.

## Rule 13, ERP-partner framing when the agency has a separate ERP

When the deal context indicates the agency has explicitly procured a separate ERP, requirements phrased `ability to X or integrate with ERP to fulfill this requirement` are candidates for an integration-first answer: agency's equivalent of `Y` with `Support = TPS/Third Party`, positioning Spare as the integration partner via Open API. Cite the specific integration stance from a past RFP that used the same framing.

## Rule 14, `Spare's` possessive counts as a valid opening

Rule 7 accepts both `Spare` and `Spare's` as the opening word. *"Spare's approach here..."* is valid.

## Rule 15, Weave the deal context explicitly

Agency-specific framing separates trustworthy answers from generic filler. Reference the agency's fleet size, service modes, adjacent systems (ERP, GPS, SSO), and implementation partners from the deal-context artifact. Generic answers read as generic.

## Rule 16, Capability-first vs. context-first opening, picked per row

Both are valid. Capability-first for short factual requirements. Context-first for multi-dimensional or ambiguous requirements. Both still open with `Spare` or `Spare's`.

## Rule 17, Three-layer and three-tool templates are structural, not claim-carrying

The templates in `voice-templates.md` are shapes only. The specific products, features, and numbers named inside the shape must come from a cited source, not from the template itself.
