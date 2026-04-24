---
name: review-rfp-draft
description: QA a drafted RFP compliance matrix before the SE submits it. Use when the user asks to "review my RFP draft," "QA the compliance matrix," "check before I submit," "pre-submission review," "audit the responses," or has just finished filling a matrix and wants a second pass. Companion skill to fill-rfp-matrix, runs all the style, honesty, and formatting checks the first skill should have enforced, and produces a triage report the SE can act on in minutes.
---

# Review RFP Draft

Run a structured QA pass over a filled RFP compliance matrix. Produce a triage report the SE can use to focus review time where it matters.

## What this skill does

Scan every filled answer row and check it against the rules the `fill-rfp-matrix` skill is supposed to enforce. Then produce a short report grouped by severity, so the SE can triage in this order:

1. **Blockers**, things that must be fixed before submission: unsourced scope-judgment language anywhere in the output, rows with no source citation in the reasoning column, em dashes, answers that don't open with `Spare`, inherited formatting that differs from the template, stray pre-existing agency data that wasn't cleared, internal-review columns that aren't labeled `strip before submit`
2. **SME review needed**, rows flagged `Low` confidence, rows with `I` (Need More Info) or `Mod` or `Y-ND` verdicts, rows with explicit clarification requests in the comment
3. **Style drift**, answers that meet the rules but have voice inconsistencies (generic phrasing, missing product names, missing deal-context framing)

## Checks to run

### Blocker checks (fail = must fix)

For every row where the comment column is non-empty:

- [ ] **Unsourced scope-judgment language anywhere in the output.** If the draft contains "this is not a Spare deal," "Spare does not do this category," "this RFP is outside our product domain," or equivalent at any level (per-row, per-section, summary), this is a critical blocker. The fill skill must source every row; category-level refusals are forbidden per Rule 0. Discard the draft and re-run with the updated methodology.
- [ ] **Repetition across rows (Rule 19).** For each sheet, compare every filled comment against every prior filled comment in the same sheet. If two comments share more than 55% of their text verbatim, both rows are blockers. This is the single most common failure mode. Implementation: use Python's `difflib.SequenceMatcher(None, a, b).ratio()` or an equivalent similarity measure; threshold `> 0.55`. Report every offending row pair and require the fill skill to rewrite those rows against their specific requirement text before the draft is cleared. The threshold was tightened from 0.70 in v1.3.2 to catch medium-repetition drift where the old setting let partial copy-paste slip through (two rows sharing 60-65% of text with only the last sentence varied). Expect occasional false positives on rows with legitimately overlapping vocabulary (e.g. two Open API rows); list them so the SE can acknowledge and move on. Example of the failure to catch: 16 consecutive rows in 2A all ending with the ERP-partner boilerplate ("Spare EAM captures the operational data at the asset and work order level and exchanges it with... via Spare's Open API..."); the template was pasted unchanged onto rows about barcode scanning, GIS integration, leased assets, CFDA tracking, and document attachments, none of which are about ERP integration. If you see that pattern, it is wrong.
- [ ] **Requirement-splicing (Rule 23).** For each filled row, take the first 8 words (or the full requirement if shorter) of the requirement column, strip punctuation, lowercase, and check whether the normalized string appears as a contiguous substring inside the normalized comment. When it does, the row has spliced the requirement phrase into a sentence template rather than responding to it in natural English, producing outputs like *"Spare EAM addresses ability for system billing to integrate with ERP for AR."* Flag every offending row. The fix is to rephrase the requirement in plain English before answering. Implementation: `import re; def norm(s): return re.sub(r"\\s+", " ", re.sub(r"[^a-z0-9\\s]", "", s.lower())).strip(); spliced = norm(" ".join(requirement.split()[:8])) in norm(comment)`. A short heuristic, so some false positives are expected on requirements that genuinely share vocabulary with the answer (e.g. "Spare EAM supports preventive maintenance scheduling" on a PM row); use judgement.
- [ ] **Third-party system name not in deal context (Rule 24).** Scan every filled comment for named third-party systems. Compare against the loaded deal-context artifact. Any system named in a comment but not in the deal context is a blocker; the row must be re-drafted with the default integration framing ("the agency's ERP" or equivalent) or with the correct name if the SE confirms it belongs. Maintain this list of names to scan for (case-insensitive, match whole-word): `Microsoft Dynamics 365`, `Dynamics 365`, `Dynamics`, `Workday`, `SAP`, `NetSuite`, `PeopleSoft`, `Oracle`, `Trapeze`, `Ecolane`, `RouteMatch`, `myAvail`, `Avail`, `Cubic`, `Moneris`, `Geotab`, `ServiceNow`, `Salesforce`, `HubSpot`, `Crowe`. If new integrations come up in real runs, add them here. Implementation: for each comment, regex-search for each name; for each hit, check whether the same name appears in the current `<agency>-deal-context.md` content. Report mismatches with row number + named system.
- [ ] **Generic vapid comments.** Flag any comment matching the exact pattern "Spare EAM supports this requirement as part of its standard feature set. Configuration and specific workflow details will be confirmed during system design and discovery." or close variants. Meaningless compliance theater; must be rewritten with row-specific content.
- [ ] **Every row has a non-empty Internal Reasoning with at least one source citation.** A reasoning note that reads "inferred from..." or "based on general knowledge of Spare..." without a citation (past RFP filename + row, doc page URL, or Notion/Glean reference) is a blocker. The row must be re-drafted with a real source.
- [ ] **Every cited precedent must have appeared in the `search_precedents` results for that row's requirement (v1.0).** Validate by re-running `search_precedents` on the row's requirement text with `top_k=10` and checking that the `source_file` + `source_row` combination cited in the Internal Reasoning column appears in the returned matches. A cited precedent that does not appear is a hallucination blocker; the row must be re-drafted from the actual search results.
- [ ] **Similarity floor for cited precedents (v1.0).** If the cited precedent's similarity score (as recorded in Internal Reasoning) is below 0.3, the row should have been marked `I` (Need More Info), not `Y`/`N`/`P`. Flag.
- [ ] First word of the customer-facing comment is `Spare` or `Spare's`. Flag any other opener. Acceptable: `Spare supports...`, `Spare's Live Map...`. Not acceptable: `In an AV deployment...`, `Barcode scanning...`, `The Spare Maintain app...`.
- [ ] No em dashes (the `U+2014` character) anywhere. Report exact count and offending rows.
- [ ] Font is not bold on the comment cell (unless the template's neighbor comment cells are themselves bold, which is rare and should be flagged for SE to decide).
- [ ] Verdict value is one of the agency's declared vocabulary. Flag any verdict that isn't in the declared set (e.g., a `P` in an MTD matrix where the vocab is `Y/Y-ND/N/I` is wrong).
- [ ] If an internal Confidence column exists, it is color-coded and the header contains `strip before submit`. If this label is missing, flag it, the SE might accidentally submit it.

### Pre-existing-data checks (fail = must fix)

- [ ] Scan the verdict and comment columns of the full requirement range for values that don't look like Spare-drafted answers: short numeric values (`4`, `1`), placeholder strings (`TBD`, `see appendix`, `custom field`), or formatting that looks very different from the drafted rows. Report these, they are usually leftover agency data that must be cleared.

### SME-review checks (report for SE attention)

- [ ] List every row with `Confidence = Low`. Include row number, requirement text (truncated to 80 chars), current verdict, and the reasoning. The SE must verify each of these before submission.
- [ ] List every row with `Confidence = Medium`. Group by theme if there are many (e.g., "5 rows about permission model," "3 rows about reporting frequency") so the SE can batch SME questions.
- [ ] List every row with verdict `I` / `Need More Information` / `Other`. These are explicit "ask the agency" rows, make sure the SE is comfortable submitting each.
- [ ] List every row with verdict `Mod` / `Y-ND` / `P` / `Partially Meet`. Reserve this verdict class for genuinely scope-dependent multi-part requirements. If the count is high, that's a signal something is wrong (either the methodology is over-flagging partials, or the RFP is genuinely outside Spare's scope and the deal-fit should be reassessed).
- [ ] List every row whose comment contains the clarification-request pattern (`we would welcome clarification from the agency`). The SE should confirm each one is warranted. Too many clarification requests hurts scoring; too few means the methodology is overclaiming.

### Style-drift checks (report for SE awareness)

- [ ] Flag comments that don't name a specific Spare product or feature (e.g., answers that say only "Spare supports this" without naming Spare EAM, Spare Operations, Open API, etc.). These read as hedging.
- [ ] Flag comments that don't reference the agency's deal context anywhere (agency name, fleet size, ERP name, service type). Context-free answers read as generic.
- [ ] Flag comments containing banned phrases: `leverage`, `leveraging`, `cutting-edge`, `best-in-class`, `seamlessly`, `robust and scalable`, `we pride ourselves`, `powerful platform`, `elevate`.
- [ ] Flag comments longer than ~400 words (likely padded) or shorter than ~15 words on a multi-part requirement (likely under-answered).

### Legal / over-disclosure checks (report for SE + legal attention)

Every RFP submission carries risk of accidentally disclosing things Spare shouldn't. These checks catch the most common failure modes.

- [ ] **Unauthorized customer references.** Scan every comment for agency or customer names (e.g., `GCTD`, `Gulf Coast Transit District`, `StarTran`, `BC Transit`, `Oakville Transit`, `Winnipeg Transit`, `Hamilton Street Railway`, `Citibus`, `Lubbock`, `People's Transit`, `Columbia Area Transit`, `RTC Washoe`, `Duluth Transit`). Cross-reference against the team's approved-references list (maintained separately by SE leadership or marketing). Flag any mention of a customer not on that list, even if the reference is accurate. The SE or a manager must confirm the agency has approved being named in this specific RFP.
- [ ] **Unannounced / roadmap features.** Flag any phrase that implies a capability is available when it's actually on the roadmap. Patterns to catch: `will be available`, `coming soon`, `in development`, `planned for release`, `next release`, `slated for`, `on track for`. Roadmap commitments in an RFP response can become contractual obligations; they must be reviewed before submission.
- [ ] **Exact financial, SLA, or performance metrics that should be legal-approved.** Flag any mention of specific uptime numbers (`99.9%`, `99.99%`, `99.999%`), specific pricing numbers, specific response-time SLAs (`30-minute response`, `90-minute response`, `1-hour resolution`), specific dollar amounts, or specific penalty/remedy terms. These are fine to include if they match Spare's standard MSA and Security Documentation, but they should not be invented or estimated. The SE should confirm every such number against the latest approved commercial and security docs before submission.
- [ ] **Named integration partners or implementation partners of the agency.** If a comment names a third party (e.g., `Crowe, LLP` as MTD's Dynamics 365 implementer), verify the reference is factual and that naming them is appropriate given the RFP context. Some agencies consider their implementation partners confidential.
- [ ] **Comparative or disparaging language about competitors.** Flag any comment that names a competitor or negatively characterizes a competing product (e.g., `unlike Fleetio`, `faster than legacy systems`, `competitors require 9 months to deploy`). Competitive positioning belongs in the reference file for drafting guidance, not in customer-facing comments. RFP responses should be affirmative about Spare, not comparative.
- [ ] **Internal-only product names or feature flags.** Flag any mention of internal code names, feature-flag names, or engineering-internal module names (anything that doesn't appear in Spare's public customer-facing documentation). These should be replaced with the customer-facing product name.

### Coverage checks

- [ ] Report the coverage ratio: filled rows / total requirement rows. Call out any section where coverage is especially low.
- [ ] Identify section-header rows that were accidentally filled (they should have been left blank).

## Output format

Produce a markdown report with these sections in order:

```
# RFP Draft Review, <matrix filename>

## Blockers (<count>)
<list each with row, sheet, issue, exact offending text, and fix>

## SME review needed (<count>)
### Low confidence (<count>)
### I / Need More Info verdicts (<count>)
### Mod / Partial verdicts (<count>)
### Medium confidence, grouped by theme

## Style drift (<count>)
<grouped by flag type>

## Coverage
Filled: <X> / <Y> (<Z%>)
Sections with low coverage: <list>
Section-header rows accidentally filled: <list or "none">

## Ready-to-submit checklist
- [ ] All blockers resolved
- [ ] Every Low-confidence row reviewed with product SME
- [ ] Internal columns (Confidence, Reasoning) stripped or hidden
- [ ] Filename matches agency's required naming convention
- [ ] Sheet tabs match the agency's original file
```

## Notes on running the checks

- Do the blocker checks first in a single pass, writing findings to a list. Do not stop at the first blocker, collect them all.
- Use openpyxl with `data_only=False` so you can see raw cell values and font attributes. Check `cell.font.bold`, `cell.font.italic`, and the actual string contents (including testing for the em-dash character directly).
- When counting em dashes, use `content.count("\u2014")` in Python. Do not try to find them by eye.
- Do not modify the file during review; this skill only reports. The SE applies fixes.
- If the file has multiple requirement sheets (MTD 2A/2B, BC Transit's 16 sheets), run every check on every sheet and report per-sheet.
