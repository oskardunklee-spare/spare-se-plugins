# spare-se-plugins

Claude plugins built by and for Spare's Solutions Engineering team.

## What's here

A shared marketplace of plugins that extend Claude Desktop with SE-specific
workflows — RFP response drafting, discovery recaps, Day of Service
Simulation helpers, and more.

## Plugins in this repo

| Plugin | Version | What it does |
|---|---|---|
| [checkmate](./checkmate) | 1.2.0 | Draft and QA RFP compliance matrices in Spare's voice. Bundled pure-stdlib MCP server (`checkmate-precedents`) performs deterministic per-row TF-IDF search over Spare's past-RFP corpus. Corpus is rebuilt in-session at the start of every fill by walking the `Spare General` Google Shared Drive via the Drive connector (no shared file, no schedule, no stale caches). Every row cites a returned precedent; hallucinated citations are blocked at review. Forbids no-bid and scope-judgment outputs. Replaces Responsive for RFP responses. |

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