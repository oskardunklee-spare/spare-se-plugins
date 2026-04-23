# Checkmate

Fill and review RFP compliance matrices for Spare's Solutions Engineering team. Replaces Responsive with a workflow tuned to Spare's voice and the real review cycles that made past submissions trustworthy.

## What's inside

- **`extract-deal-context`**, runs once at the start of a new RFP workflow. Reads the agency's RFP PDF and produces a structured `<agency>-deal-context.md` artifact (agency identity, fleet snapshot, adjacent systems, timeline, scope restrictions, competitive signals, risk/fit notes) that subsequent drafting sessions reference for every answer.
- **`fill-rfp-matrix`**, core skill. Opens an incoming `.xlsx` or `.csv` compliance matrix, detects the schema and verdict vocabulary, loads the deal-context artifact, fills the matrix with Spare-voiced responses backed by past RFPs and Spare docs, and adds two internal-only columns for confidence scoring and source citation.
- **`review-rfp-draft`**, companion QA skill. Runs a structured pass over a filled matrix and produces a triage report: blockers, SME review queue, style drift, legal/over-disclosure checks, and a ready-to-submit checklist.

## How to use

**At the start of a new RFP**: drop the agency's RFP PDF into the Cowork session and ask *"Extract the deal context from this RFP."* This produces a reusable deal-context artifact.

**To fill the matrix**: drop the compliance matrix file in and ask *"Fill this RFP matrix"* or *"Respond to this compliance matrix."* The fill skill will pick up the deal-context artifact automatically.

**Before submission**: ask *"Review my RFP draft before I submit."* The review skill produces a triage report you can work through in 30 minutes.

## Connectors this plugin expects you to have installed

Checkmate does not bundle MCP servers. It relies on connectors that should already be present in the Cowork environment for Spare's SE team:

- **Google Drive**, for searching past completed RFP responses (highest-leverage source of battle-tested language)
- **Spare documentation MCP**, for authoritative capability information from `docs.sparelabs.com` and the internal enablement site
- **Notion**, for internal product context, roadmap, and known limitations
- **Glean**, for cross-source tribal knowledge (Slack history, Gong transcripts). Optional; Checkmate will degrade gracefully if unavailable.

If any of these aren't connected, the plugin will still run but will flag more rows as `Low` confidence because it can't cross-reference past answers.

## Design principles this plugin is built on

The full methodology lives in `skills/fill-rfp-matrix/references/methodology-rules.md`. Short version:

- Schema detection first, always. Never assume a verdict vocabulary.
- Every customer-facing answer leads with `Spare` or `Spare's`.
- No em dashes.
- Honest about gaps. Disclose what Spare doesn't do, that's the trust-builder.
- Every row gets a confidence score (High/Medium/Low) plus reasoning. This is the primary mechanism that lets an SE scan a 600-row matrix in minutes.
- When the agency has a separate ERP already procured, lean into that architecture rather than claiming Spare does what the ERP does.
- Two registers (capability-first and context-first) both valid; pick per row.

## Known gaps disclosed consistently

See `skills/fill-rfp-matrix/references/known-gaps.md`. Disclose these every time they come up; consistent disclosure across deals is what makes Spare's answers trustworthy.

## Competitive positioning

See `skills/fill-rfp-matrix/references/competitive-positioning.md` for how Spare positions against named competitors (Fleetio, RTA, AssetWorks, myAvail, and others). The reference file is seeded from Spare's sales-enablement docs and points to Klue (via Glean search) as the authoritative source for battlecards not yet documented here.

## Contributing

The plugin compounds in value only if SEs feed learnings back into it. After every submitted RFP, spend 15 minutes adding to the reference files. See `CONTRIBUTING.md` for the specifics.

## Adding to the plugin

When you disclose a new gap in a submitted RFP, add the exact phrasing used to `known-gaps.md`. When a new voice template proves itself across multiple deals, add it to `voice-templates.md`. When a new agency schema comes through, add its layout to `schema-detection.md`.

The plugin gets better every time an SE uses it.
