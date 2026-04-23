# Contributing to Checkmate

Checkmate gets better every time an SE uses it on a real RFP. The value compounds only if the team feeds learnings back into the plugin. This doc explains how.

## The post-RFP ritual

After every submitted RFP, two things happen:

### 1. Drop the response in `Spare General`

The submitted RFP response should land in the `Spare General` Shared Drive folder (or wherever SE convention places it within that drive). Nothing else is required. The next SE who runs a fill will walk `Spare General` fresh as part of their session's mandatory first action and pick up your submission automatically. No corpus rebuild, no schedule, no shared file to update.

### 2. Update reference files (10 minutes)

1. **`skills/fill-rfp-matrix/references/known-gaps.md`**, if the wording of a gap disclosure improved during review. This file holds the disclosure *patterns*, not specific cached gap claims; the claims come from the live per-session corpus.
2. **`skills/fill-rfp-matrix/references/voice-templates.md`**, if a new reusable structural template emerged, or if a banned phrase showed up and needs to be added to the never-use list
3. **`skills/fill-rfp-matrix/references/schema-detection.md`**, if the RFP had a new matrix layout, verdict vocabulary, or column structure not already documented
4. **`skills/fill-rfp-matrix/references/competitive-positioning.md`**, if the RFP named a new competitor or Klue published updated battlecards
5. **`skills/fill-rfp-matrix/references/methodology-rules.md`**, if a review cycle surfaced a new rule. Add it as the next numbered rule with a one-line note on the origin.

## How to contribute

This plugin is checked into the Spare team's plugin repository. To propose changes:

1. Clone or edit the plugin directory in your Cowork working space
2. Make the update in the relevant reference file
3. Repackage as a `.plugin` file and share in your team's plugin channel
4. The SE team lead (or whoever owns plugin stewardship) reviews and publishes the new version

If you're not sure whether a learning belongs in the plugin, err on the side of adding it. A reference file with too much detail is better than a reference file that's missing the thing that would have saved the next SE three hours.

## What not to add

- **Deal-specific data** (specific agency facts beyond what appears in the deal-context artifact for that run). The plugin should stay transferable across deals.
- **Customer-identifying info without permission**. Do not add a proof point that names an unannounced customer. The GCTD reference in `voice-templates.md` is there because GCTD has approved being used as a reference; check before adding others.
- **Speculative or roadmap-dependent claims**. Only add capabilities that are in the generally-available product. Roadmap items belong in `known-gaps.md` as "on the roadmap" language, not as "Spare does X."

## Keeping the plugin honest

The whole point of Checkmate is to produce RFP responses Spare's team can trust. That requires the plugin itself to be trustworthy. Two things matter here:

- **Every claim in `voice-templates.md` and `known-gaps.md` should be verifiable against Spare docs or a past submitted RFP.** Cite the source in a comment (a link to the doc page or a reference to the deal name) when adding content.
- **When capabilities change in the product, update the plugin on the same cycle.** If Spare ships automated warranty expiration notifications next quarter, the current disclosure in `known-gaps.md` becomes wrong and the next RFP using it will embarrass the team.

## Versioning

The plugin uses semver. Cut a new version any time a reference file, skill, or MCP server is updated:

- **Patch** (1.2.1, 1.2.2) for reference-file updates, typo fixes, clarifications
- **Minor** (1.3.0, 1.4.0) for new rules, new reference files, or new skills
- **Major** (2.0.0) when the plugin architecture changes in a backwards-incompatible way

Update the version in `.claude-plugin/plugin.json` when you cut a new release.

## Owner

The plugin is owned by Spare's Solutions Engineering team. Questions and proposed updates should go to the SE team lead.
