# spare-se-plugins

Claude plugins built by and for Spare's Solutions Engineering team.

## What's here

A shared marketplace of plugins that extend Claude Desktop with SE-specific
workflows — RFP response drafting, discovery recaps, Day of Service
Simulation helpers, and more.

## Plugins in this repo

| Plugin | Version | What it does |
|---|---|---|
| [checkmate](./checkmate) | 0.3.0 | Draft and QA RFP compliance matrices in Spare's voice, sourced live from Google Drive past-RFP responses and the Spare documentation MCP. Forbids unsourced scope judgments, cites sources per row, scores confidence, and runs a pre-submission review pass covering voice, formatting, legal over-disclosure, and coverage. Replaces Responsive for RFP responses. |

## Using these plugins

This repo is connected to Spare's Claude organization as a plugin marketplace.
Plugins auto-sync to the team on merge to `main`. You'll see them in
Claude Desktop under Customize → Browse plugins.

## Contributing

1. Branch off `main`
2. Add your plugin as a folder at the repo root (lowercase-hyphenated name)
3. Register it in `.claude-plugin/marketplace.json`
4. Open a PR

See individual plugin folders for usage docs.