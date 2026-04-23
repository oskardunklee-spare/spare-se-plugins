# spare-se-plugins

Claude plugins built by and for Spare's Solutions Engineering team.

## What's here

A shared marketplace of plugins that extend Claude Desktop with SE-specific
workflows — RFP response drafting, discovery recaps, Day of Service
Simulation helpers, and more.

## Plugins in this repo

| Plugin | Version | What it does |
|---|---|---|
| [checkmate](./checkmate) | 1.1.0 | Draft and QA RFP compliance matrices in Spare's voice. Bundled pure-stdlib MCP server (`checkmate-precedents`) performs deterministic per-row TF-IDF search over Spare's entire past-RFP corpus. Corpus is refreshed by a Cowork-native skill that walks the `Spare General` Google Drive folder via the Drive connector (no terminal, no pip install, no Google Cloud setup). Every row cites a returned precedent; hallucinated citations are blocked at review. Forbids no-bid and scope-judgment outputs. Replaces Responsive for RFP responses. |

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