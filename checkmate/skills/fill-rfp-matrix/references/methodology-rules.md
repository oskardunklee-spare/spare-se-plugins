# Methodology Rules

Rules are numbered for reference. Rule 0 overrides everything else. Each rule came from a real review cycle on a real matrix or from a real failure mode in production.

## Rule 0: Invoking Checkmate means the bid decision is already made

When the user invokes `fill-rfp-matrix` on a matrix, the go/no-go decision has been made already by the SE and leadership. Your job is to source the best answers from past responses and docs, not to second-guess the bid.

Do not produce, at any granularity:

- "This is not a Spare deal"
- "Recommend no-bid" or "Suggest no-bid (Recommended)"
- Fit-check summaries, scope-mismatch warnings, or category-concern preambles
- Option menus asking the user how to proceed given a perceived scope issue
- Any hedging that implies Spare may not be the right vendor for this RFP

Spare's product catalog includes Spare Operations, Spare EAM (full work-order management, PM scheduling, parts inventory, asset lifecycle, vendors/POs), Spare EAM Lite, Spare Resolve, Spare Eligibility, Spare Engage, Spare Analytics, Spare Driver App, Spare Rider App, Spare Maintain (mobile technician), SpareONE, and Open API. Spare has completed EAM RFP responses. If you find yourself about to conclude Spare doesn't ship something broad (EAM, asset management, work orders, maintenance scheduling), you are wrong; check the precedents in Drive.

If the user wants a deal-fit assessment, they will invoke a separate skill for that. This skill does not provide one.

## Rule 1: Start by anchoring in the `Spare General` Drive folder

Before opening the matrix, before detecting schema, before anything else, your first action is to locate and read from the `Spare General` Google Drive folder. This is the team's master folder; all precedent lives inside or below it.

Steps:

1. Use the Drive search tool to find the folder titled `Spare General`.
2. List its contents. Identify subfolders and files relevant to the RFP category at hand (for EAM: `EAM RFP - <date>`, `Potential EAM RFP`, `<Agency> EAM RFP`, files with `EAM` in the title).
3. Open at least one completed precedent matrix before drafting any row. Known precedent files: `Laramie RFP - Spare EAM Response Matrix`, `Calgary_EAM_Specs_with_Responses_SpareOnly_updated.csv`, `TCAT EAM RFP 1-28-26`, `SolTrans EAM RFP Scope and Budget`, `NFTA EAM RFP`, `Valley Transit EAM RFP`, `Spare's Master Sample RFP Tech Spec Requirements`.
4. Produce a short grounding note before drafting: which files you loaded, what categories they cover, how you will use them.

If `Spare General` is not accessible, stop and tell the user. Do not fall back to general knowledge.

## Rule 2: Source every row live, in this order

For every row, search in sequence:

1. Precedent files in `Spare General` (already loaded). Cross-reference the requirement against what a past RFP answered.
2. Spare documentation MCP (`search_spare_documentation`). Check `/internal-changelog/` for recent shipments.
3. Notion and Glean for roadmap, tribal knowledge, Klue battlecards.

Only if all three are silent, verdict is `I`. Never `N` from silence. Never a row-level "not a Spare deal."

## Rule 3: Cite the source in every row

Internal Reasoning must name the specific source: Drive file + row number (e.g., `"Laramie RFP - Spare EAM Response Matrix row 3.1.3"`), doc URL, or Notion/Glean page title + date. "Inferred from..." without a citation is not complete.

## Rule 4: Detect agency-specific verdict vocabulary

Read it from the matrix. Hidden sheets, data-validation dropdowns, header-row blocks. Never assume. See `schema-detection.md`.

## Rule 5: Detect and skip section-header rows

Short labels in the requirement column with no verdict/comment expected. Leave untouched.

## Rule 6: Pre-flight scan for stray values

Clear pre-existing agency annotations (numeric scores, draft notes, previous-vendor placeholders) before filling.

## Rule 7: Explicit format isolation

Every written cell sets `Font(bold=False, name="Calibri", size=11)` explicitly. Comment cells set `Alignment(wrap_text=True, vertical="top")`. openpyxl preserves inherited styling otherwise.

## Rule 8: Lead every customer-facing comment with `Spare` or `Spare's`

First word. Not the topic, not the customer's problem, not a generic descriptor.

## Rule 9: No em dashes

`U+2014` anywhere in customer-facing output is a blocker. Use commas, periods, semicolons, parentheses.

## Rule 10: Honest about gaps, when the gap is sourced

Past RFP disclosure or docs page saying "not currently available" is legitimate basis for gap disclosure. An assumption that Spare probably does not do X is not. See `known-gaps.md` for phrasing patterns.

## Rule 11: Clarification-request phrasing for genuinely ambiguous requirements

When a requirement could be interpreted multiple ways, answer what Spare can do for each interpretation and close with a sourced clarification request.

## Rule 12: Internal Confidence and Reasoning columns are mandatory

Two columns past the last agency-defined column. Yellow bold headers. `(strip before submit)` suffix required.

## Rule 13: Confidence rubric

- `High` (green): direct match in `Spare General` precedent from the last 12 months, corroborated by current docs
- `Medium` (yellow): older or single-source match, or specific wording needs SME verification
- `Low` (red): constructed from adjacent evidence, flagged for SME

## Rule 14: ERP-partner framing when the agency has a separate ERP

When the deal-context artifact indicates a separately-procured ERP, requirements phrased `ability to X or integrate with ERP` are candidates for integration-first answers: agency's equivalent of `Y` with `Support = TPS`, citing a past RFP that used the same stance.

## Rule 15: `Spare's` possessive counts as a valid opening

Rule 8 accepts both `Spare` and `Spare's`.

## Rule 16: Weave the deal context explicitly

Agency-specific framing (fleet size, adjacent systems, implementation partners) from the deal-context artifact. Generic answers read as generic.

## Rule 17: Capability-first vs. context-first opening, picked per row

Both valid. Capability-first for short factual. Context-first for multi-dimensional. Both open with `Spare` or `Spare's`.

## Rule 18: Templates are structural, not claim-carrying

The shapes in `voice-templates.md` are patterns. Specific products, features, numbers, and customer names inside a template come from cited sources, not from the template itself.

## Rule 19: Repetition is a bug

Every row's comment must specifically address that row's requirement text. Two rows in the same section with identical or near-identical comments is a bug, not a feature. If the requirement mentions barcode scanning, the comment mentions barcode. If the requirement mentions GIS integration, the comment mentions GIS. A comment that could paste onto any row is wrong.

Concretely: `review-rfp-draft` runs a deterministic similarity check and flags rows whose comments share more than 55% of their text with a previous row. The threshold was tightened from 0.70 in v1.3.2 after observing medium-repetition drift (two rows sharing 60-65% of text with only the last sentence varied) slipping past the old threshold. Expect occasional false positives on rows with legitimately overlapping vocabulary (e.g. two Open API rows); the review report is a triage, not a verdict, so the SE can acknowledge and move on.

Before handoff, skim your own output: read any 3 adjacent filled rows aloud. If they sound the same, they are the same, rewrite them.

## Rule 20: Finishing a fill means the review skill has run

`fill-rfp-matrix` does not output a "done" to the user until `review-rfp-draft` has been invoked on the filled file and returned a clean report (or the SE has explicitly overridden a flag). Do not hand back a matrix that has not been reviewed. The review skill is part of the drafting workflow, not a separate optional step.

## Rule 21: Per-row precedent search is a tool call, not a prose instruction (v1.0)

Every row's first action is a call to the `search_precedents` tool on the `checkmate-precedents` MCP server bundled with this plugin. The tool returns the top-k nearest matches from the pre-indexed `Spare General` precedent corpus. The row's verdict and comment MUST derive from one or more of the returned matches; the Internal Reasoning column MUST cite at least one `source_file + source_row` from the returned matches.

If `search_precedents` returns no matches above the similarity threshold, the verdict is `I` (Need More Info) in the agency's vocabulary, with reasoning naming the query text and the absence of results. Never draft a `Y`/`N`/`P` verdict from a row where the tool returned nothing.

This rule supersedes and operationalizes Rules 1-3. Those rules describe what to do; Rule 21 describes how Cowork enforces it. Prose rules can be ignored by the model; a tool call with structured output cannot.

Corollary (enforced by `review-rfp-draft`): every citation in the Internal Reasoning column must correspond to a `search_precedents` result for that row's requirement. Citing a precedent that the tool did not return for that row is a hallucination blocker.

## Rule 22: Corpus freshness

The `precedents.jsonl` corpus consumed by the MCP server lives in `$CLAUDE_PLUGIN_ROOT/data/cache/precedents.jsonl` alongside a `state.json` manifest that records the `modifiedTime` of every Drive file that contributed to it. At the start of every fill, `fill-rfp-matrix` does a metadata-only list of `Spare General` via the Drive connector, diffs against the manifest, and re-parses only files that have been added or changed. If nothing has changed, the cache is used as-is and drafting starts in seconds. There is no shared corpus, no scheduled rebuild, and no TTL; the cache is per-user and gitignored.

At the end of the diff/rebuild, `fill-rfp-matrix` calls the `corpus_stats` tool and records total-rows, year-range, and source-file count as its grounding note. If the corpus returned is the bundled 10-row sample (which means the cache path wasn't populated), halt and report. Do not draft from the sample.

## Rule 23: Don't splice the requirement text into the answer

A failure mode distinct from copy-paste: the model takes the raw requirement phrase and inserts it as a noun into a generic sentence template, producing broken English and vendor boilerplate tone. Seen in live v1.3.1 runs:

- *"Spare EAM addresses ability for system billing to integrate with ERP for AR."* (from requirement "Ability for system billing to integrate with ERP for AR")
- *"Spare EAM's native functionality includes restrict access to employee & vendor pay rates."* (from requirement "Restrict access to employee & vendor pay rates")
- *"Spare EAM is configured for search for data using a variety of search criteria."* (from requirement "Search for data using a variety of search criteria")

**Rule: rephrase the requirement in plain English before answering.** Read the requirement, identify the specific capability it asks about, then write a sentence that answers "does Spare support this?" in natural English. Pull specifics from the cited precedent. Do not paste the requirement phrase into a sentence template. See the "Anti-pattern: splicing the requirement text into the answer" section in `voice-templates.md` for before-and-after examples.

`review-rfp-draft` scans for this pattern by taking the first ~8 words of each requirement and checking whether they appear verbatim as a contiguous substring inside the drafted comment. When they do, the row is flagged for rewrite.

## Rule 24: Don't name third-party systems that aren't in the deal context

**This rule applies to every integration category, not just ERPs.** ERP, GL, fare, payment processor, scheduling, AVL / telematics, GIS, CRM, ITSM, eligibility, identity / SSO, document management, implementation partners — all of them. Precedents in the corpus are drawn from specific past agencies and carry customer-specific integration names (MTD's Microsoft Dynamics 365, a past agency's specific fare vendor, another agency's specific AVL provider, etc.). Those names must not be carried into drafts for different agencies unless the current agency's `<agency>-deal-context.md` artifact also names them.

Default framing for integration and API questions, regardless of category: *"Spare exposes a public Open API covering [entities]. Specific integration scope with the agency's [integration category, e.g. ERP, fare system, telematics provider, scheduling system, GIS] is confirmed during implementation."* See the "Integration / API answer template" section in `voice-templates.md` for examples across ERP, telematics, fare, and other categories.

Better to be safe than to commit Spare to a specific integration we haven't confirmed. When in doubt, say "the agency's ERP" / "the agency's telematics provider" / "the agency's fare system" / etc. — not the product's name.

`review-rfp-draft` maintains a list of common transit-adjacent and enterprise third-party system names across categories (ERP / GL: Microsoft Dynamics 365, Workday, SAP, NetSuite, PeopleSoft, Oracle; scheduling / paratransit: Trapeze, Ecolane, RouteMatch, myAvail; fare / payment: Cubic, Moneris, Genfare, Stripe; telematics / AVL: Geotab, Samsara, INIT, Clever Devices; CRM / ITSM: Salesforce, HubSpot, ServiceNow; implementation partners: Crowe, Deloitte, Accenture; plus others added as new RFPs introduce them) and cross-checks every filled comment against the loaded deal-context artifact. Any named system that appears in a comment but not in deal context is flagged as a blocker.
