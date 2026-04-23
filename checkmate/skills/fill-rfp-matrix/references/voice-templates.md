# Voice Templates

Reusable answer shapes. These are structural patterns only. The specific products, features, numbers, customer names, and any factual claims inside a template must come from a cited source (a past RFP row, a Spare docs page, or Notion/Glean) per Rule 0 and Rule 2 in `methodology-rules.md`. Do not reuse the placeholder text as-is.

## Three-layer template (platform / service / vehicle)

For requirements like "detect faults," "monitor anomalies," "report reliability," "track issues" that often have multiple valid interpretations.

```
Spare's [capability] spans three distinct layers.

Platform health: [what Spare does at the platform level, sourced from docs or past RFP].

Service operations: [alerts, dispatcher actions, analytics, sourced from docs or past RFP].

Vehicle health: [Spare EAM or equivalent product feature, sourced from docs or past RFP].

[If the requirement is ambiguous about scope:] We would welcome clarification from the agency on which aspects are most relevant to this requirement.
```

## Three-tool template

For "incident logging," "case management," "customer feedback," "complaint tracking," "event review" requirements.

```
Spare provides [count] complementary tools for [requirement].

First, [tool/capability 1, sourced].
Second, [tool/capability 2, sourced].
Third, [tool/capability 3, sourced].
```

The specific tools named (audit logs, Resolve, EAM, Analytics, etc.) must be cited from past RFPs that answered the same requirement. Do not assume the same three tools apply to every multi-tool requirement.

## ERP-partner template

For `ability to X or integrate with ERP to fulfill this requirement` when the deal-context artifact indicates the agency has a separately-procured ERP.

```
Spare [...operational capability X from source...] and exchanges data with [agency's ERP name, from deal context] via Spare's Open API. [The financial/policy function] is owned by [ERP name] as the authoritative system of record, and Spare [...surfaces the resulting state from source...]. Specific integration scope, field mappings, and sync cadence will be confirmed during discovery with [agency's] IT team and [implementation partner from deal context, if known].
```

Verdict selection (agency's equivalent of `Y` vs. `Y-ND` vs. `I`) comes from whether a past RFP used the same integration stance with the same ERP. Support column is `TPS` / `Third Party` / equivalent when the financial/policy function is ERP-owned.

## Clarification-request template

For genuinely ambiguous or scope-dependent requirements.

```
Spare's approach here depends on what [agency] is tracking. For [interpretation A], [sourced answer A]. For [interpretation B], [sourced answer B]. [Optionally: interpretation C]. We would welcome clarification from the agency on [the specific dimension in question], particularly around [concrete sub-question].
```

## Short factual template (capability-first)

For narrow, single-feature requirements. One to three sentences.

```
Spare['s] [Product/Feature, from sourced evidence] [does X, from sourced evidence] [with specifics, from sourced evidence]. [Optional: one sentence on scope or notable detail].
```

## Honest-gap disclosure template

For when the sourced evidence explicitly indicates a feature is not currently available. See also `known-gaps.md` for the four gap-disclosure patterns.

```
[Sourced capability that is supported]. Note: [sourced gap] is not currently available. [Sourced workaround or alternative, if any]. [If on roadmap per source, say so].
```

## Never-use phrases

Avoid in customer-facing comments:

- *"leveraging cutting-edge technology"*
- *"seamlessly integrates"*
- *"best-in-class"*
- *"robust and scalable"* (specify what scales, citing a source)
- *"We pride ourselves on..."*
- The em-dash character (`U+2014`) anywhere
- *"elevate"* as a verb
- *"streamlined"* as a pure adjective (OK as a verb with an object)
- *"powerful"* as an adjective for the platform

## Product-name catalog

Use `references/scope-of-spare.md` for the canonical list of Spare product names to search for and cite. Spell them exactly as they appear in the docs and past RFPs.

## Numbers and customer references

Do not cache quantified claims in this file. Uptime percentages, refresh intervals, customer adoption metrics, pricing signals, and reference-customer results must come from a live source (Spare docs MCP, a past RFP within the last 12 months) every time they are used. Product specs drift and past claims go stale. The Internal Reasoning column must cite the source for every number in the customer-facing comment.

For reference-customer quotes specifically, also verify the customer has been approved for public reference use. See the legal/over-disclosure checks in `review-rfp-draft/SKILL.md`.
