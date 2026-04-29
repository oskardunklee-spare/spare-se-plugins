---
name: enforce-spare-voice
description: Rewrite RFP compliance-matrix comments in Spare's actual voice. Takes a filled matrix file (xlsx or csv), scans every customer-facing comment against Spare's tone principles (active verbs, short sentences, no hedge filler, plain language, no vendor-register phrases), and rewrites any row that reads as generic enterprise-vendor boilerplate. Invoked automatically by fill-rfp-matrix after drafting and before review; also runnable standalone when the user says "rewrite this matrix in Spare voice," "clean up the voice on this fill," "enforce Spare tone on this draft," or "the answers sound too corporate." The goal is quality output that sounds like Spare, not rule-satisfaction.
---

# Enforce Spare Voice

Rewrite every customer-facing comment in the matrix so it sounds like Spare, not a generic enterprise-software vendor. This skill is the backstop that catches bad voice even when the drafting-time rules didn't prevent it.

## What this skill does

1. Opens the matrix file (the one `fill-rfp-matrix` just produced, or an SE-supplied filled matrix).
2. Detects the comment column using the same header patterns as `parse_matrix.py`, skipping internal columns (`Internal Confidence`, `Internal Reasoning / Sources (strip before submit)`, etc.).
3. For every filled row, scans the comment against Spare voice signals. If the comment shows any of the failure modes in the "What gets rewritten" list below, rewrites it.
4. Writes the cleaned matrix back to the same file (or a new path if the user requested a copy).
5. Reports a summary: how many rows were scanned, how many rewrites happened, and the top 3-5 rewrites with before/after snippets so the SE can audit the pass.

## When to invoke

- **Automatically**, by `fill-rfp-matrix` as the last step before `review-rfp-draft`. The fill skill invokes this after the last row is drafted and before handing off to review.
- **Standalone**, when the user says any of:
  - *"Rewrite this matrix in Spare voice"*
  - *"Clean up the voice on this fill"*
  - *"Enforce Spare tone on this draft"*
  - *"These answers sound too corporate / too vendor-y / too generic"*
  - *"The tone is off on this matrix"*

## Spare voice principles (the rules this skill enforces)

1. **Active voice with concrete verbs.** "Spare tags each asset" not "assets can be tagged by Spare." Ban nominalizations like "categorize with configurable attributes" (→ "tag with attributes").
2. **Short sentences, one idea each.** Split anything with three commas or a semicolon+conjunction. Target sentence length: 15-25 words.
3. **No hedge filler.** Ban the following words/phrases from customer-facing comments and rewrite around them:
   - `typically`, `typically owned`, `typically maintained`, `typically handled by`
   - `fully documented`, `comprehensively`, `robustly`, `seamlessly`, `leveraging`, `leveraged`, `robust`, `cutting-edge`, `best-in-class`, `powerful`, `elevate`
   - `is reflected in`, `is passed to`, `is exchanged with` → replace with active verbs like "flows to," "syncs to," "sends"
   - `the platform exposes` (when appearing in more than one row of the same sheet) → vary the subject
4. **Plain language.** Replace jargon with ordinary words when the meaning is the same:
   - "threshold logic is typically owned in the ERP" → "the ERP owns the threshold"
   - "data flows for asset master, purchase orders, receipts" → "asset, PO, and receipt data flows"
5. **Confident, not salesy.** State what Spare does. Skip the adjectives. Delete any "we pride ourselves," "robust and scalable," or similar puffery.
6. **No quoted-requirement preamble or colon-intro template.** Ban the pattern `Spare [verb] "[requirement]" in Spare EAM: [actual answer]`. If you see this pattern, delete the first clause up through the colon and keep the substantive answer (rewritten in Spare voice).
7. **No "Spare's" followed by a preposition.** `Spare's within Spare EAM, X is covered` → rewrite as `Spare EAM covers X` or `Within Spare EAM, X happens`.

See `checkmate/skills/fill-rfp-matrix/references/voice-templates.md` for the full reference including before/after examples.

## What gets rewritten

Rewrite any row whose comment matches one or more of:

1. **Contains any banned vendor-register phrase** (the list under Principle 3 above).
2. **Opens with a quoted-requirement splice** — `Spare [verb] "..."` where the quote contains the requirement phrase.
3. **Uses the colon-intro construction** — a first clause of 6+ words followed by a colon followed by the actual substantive answer.
4. **Opens with `Spare's` + preposition** — `Spare's within`, `Spare's in`, `Spare's regarding`, etc.
5. **Is predominantly passive voice** — more than 60% of clauses use passive constructions. Rewrite to active.
6. **Strings together three or more enterprise-noun lists without purpose** — e.g., "for asset master, purchase orders, receipts, and inventory transactions for procurement and payables" when the agency asked a specific narrow question.
7. **Is long and wordy for what it says** — if the same content fits in 60% of the word count, the original is padded and should be tightened.
8. **Sits in a stretch of monotonous openers** — any row whose first 2 words match the previous row's first 2 words, AND those same first 2 words also match the row before that. Three or more consecutive `Spare EAM ___` openers is a stamping signal; rotate the second or third row to one of the alternate opener patterns.

Rows that are already in Spare voice pass through unchanged. Don't rewrite for the sake of rewriting.

## Opener-rotation rules

When rewriting (or drafting in the first place via fill-rfp-matrix), use this rotation strategy across consecutive rows in the same section:

- **Track the previous 2 rows' openers.** If a new row would use the same first 2 words as the previous one, swap to a different opener pattern.
- **Aim for at least 2 distinct patterns within any 5 consecutive rows.** Three identical-pattern rows in a row is a blocker.
- **Valid alternates to `Spare [Product]` / `Spare's [feature]`:**
  - `Within Spare [Product], [subject] [verb]...`
  - `In Spare's [feature], [subject] [verb]...`
  - `Each [entity] in Spare [Product]...`
  - `[Entity] in Spare [Product] [verb]...`
  - `Through Spare's [feature], ...`

  See `voice-templates.md` "Opener variety" section for the full list with examples.
- **Spare must still appear within the first 5-7 words of the opening clause.** "The platform" / "The system" / "Out of the box" / verdict-only openers are still banned.

## How to rewrite

For each violating row:

1. **Identify what Spare actually does.** Read the existing comment and extract the factual content. If the comment is thin, re-consult the `search_precedents` results that sourced the row (cited in Internal Reasoning).
2. **Rewrite using the before/after table patterns** in `voice-templates.md`. Start with `Spare`, `Spare's`, or `Spare [Product]`. Use active verbs. Keep sentences short. Delete hedge filler.
3. **Preserve the verdict.** This skill only rewrites the comment column. Do not change verdicts, confidence scores, or citations.
4. **Keep Internal Reasoning / Sources as-is.** Do not rewrite citations. The SE needs that audit trail.

## Operating order

### Step 1: Announce

**Post to user:** *"Enforcing Spare voice. Scanning N filled rows against tone rules..."*

### Step 2: Load the matrix

Use openpyxl (should already be installed per `fill-rfp-matrix`'s prereqs). Open the file. Identify the comment column using the same column-exclusion rules from `parse_matrix.py` (skip internal columns).

### Step 3: Scan each row

For every filled row (non-empty comment), run it against the rewrite triggers above. Track:

- Total rows scanned
- Rows triggering a rewrite
- Which trigger fired (for the summary)

### Step 4: Rewrite violating rows

For each row flagged, produce a Spare-voice rewrite following the principles. Write the rewrite back into the comment cell. Preserve cell formatting: `Font(bold=False, name="Calibri", size=11)`, `Alignment(wrap_text=True, vertical="top")`, and clear any explicit row height so wrapping auto-fits on open.

### Step 5: Save

Save the file in place (or to a user-specified path).

### Step 6: Report

**Post to user** a summary:

```
✓ Voice enforcement complete.
- Scanned: 312 filled rows
- Rewritten: 47 rows
- Top triggers: 18× vendor-register phrases, 12× quoted-requirement, 9× colon-intro, 5× passive voice, 3× Spare's + preposition
Top 3 rewrites:

Row 47 (vendor-register):
  Before: "Spare EAM supports categorizing assets with configurable attributes that can flag capitalization status."
  After:  "Spare EAM tags each asset with its capitalization status via a configurable attribute."

Row 89 (quoted-requirement + colon-intro):
  Before: 'Spare addresses "identify assets based on capitalization threshold" in Spare EAM: supports this integration via the fully documented Open API.'
  After:  'Spare EAM identifies capitalizable assets via the Open API integration; MTD’s Dynamics 365 owns the threshold decision. We'll confirm the mapping at implementation.'

Row 142 (passive voice):
  Before: "The platform exposes a public Open API covering core entities."
  After:  "Spare's Open API covers every core entity."
```

## Never

- Do not change the verdict column. Voice enforcement is comment-only.
- Do not strip or alter Internal Confidence or Internal Reasoning / Sources columns. Those are the SE's audit trail.
- Do not add new citations; only `fill-rfp-matrix` and its docs-MCP triggers can do that.
- Do not rewrite section-header rows. They're not customer-facing.
- Do not "enhance" factually correct content with extra adjectives or marketing language. Spare voice is specific, not decorative.

## Reference files

- `checkmate/skills/fill-rfp-matrix/references/voice-templates.md`: complete voice reference with before/after table and full banned-phrase list
- `checkmate/skills/fill-rfp-matrix/references/methodology-rules.md`: underlying rules (Rule 4 opener, Rule 19 specificity, Rule 23 anti-splicing, Rule 26 precedent-content handling, Rule 27 opener grammar, Rule 28 quoted-requirement)
