# Voice Templates

**Read this first.** These templates are skeletons, not sentences. Every filled-in row must be tailored to the specific requirement text of that row. If two rows in the same section end up with identical or near-identical comments, you did it wrong, the requirement text differs between rows, so the comment should too.

## Anti-pattern: copy-paste across rows

**This is the most common failure mode and it is a blocker.** Example of what NOT to do (taken from a v0.4.0 run that shipped wrong):

Row 19: *"Spare EAM captures the operational data at the asset and work order level and exchanges it with MTD's Microsoft Dynamics 365 ERP via Spare's Open API..."*

Row 20: *"Spare EAM captures the operational data at the asset and work order level and exchanges it with MTD's Microsoft Dynamics 365 ERP via Spare's Open API..."*

Row 21: *"Spare EAM captures the operational data at the asset and work order level and exchanges it with MTD's Microsoft Dynamics 365 ERP via Spare's Open API..."*

Fifteen more identical rows.

Each row in the matrix asks about a different capability (asset disposal, CFDA tracking, barcode scanning, GIS integration, document attachments, leased assets). The comments must address each specific capability using sourced language from a past RFP or Spare docs. An evaluator reading 16 identical comments marks the submission as vendor boilerplate and scores it low.

**Rule: every comment must quote or paraphrase the specific capability named in the requirement text.** If the requirement says "barcode technology for asset identification," the comment must mention barcode. If the requirement says "GIS integration for asset location," the comment must mention GIS. A generic "Spare EAM captures operational data" comment that could paste onto any row is wrong.

**Rule: two rows with comments sharing more than roughly 70% of their text is a bug.** The `review-rfp-draft` skill flags this automatically. Before handoff, verify each row's comment addresses that row's specific requirement.

## How to use a template

1. Read the row's requirement text carefully. Identify the specific capability asked about.
2. Search past RFP precedents (via `Spare General` in Drive) for rows that asked about that specific capability. Use that past row's answer as the core of your comment, adapted to the current agency's deal context (fleet size, adjacent systems, service modes).
3. Pick the structural template below that fits the requirement's shape.
4. Fill every `[bracketed]` slot with row-specific content from the cited source. The filled sentence must name the specific capability, quote (or paraphrase) the specific past-RFP language that applies to it, and reference the agency's deal context where relevant.
5. Check your draft against the previous 2-3 rows in the same section. If it reads the same, rewrite.

## Templates

### Three-layer template (platform / service / vehicle)

For "detect faults," "monitor anomalies," "report reliability," "track issues" where the requirement has multiple valid interpretations.

```
Spare's [specific capability named in requirement] spans three distinct layers.

Platform health: [sourced content specific to the capability].
Service operations: [sourced content specific to the capability].
Vehicle health: [sourced content specific to the capability].

[If ambiguous:] We would welcome clarification from the agency on which aspects are most relevant to this requirement.
```

### Three-tool template

For "incident logging," "case management," "event review." The specific tools named (audit logs, Resolve, EAM, Analytics, Engage) must be cited from a past RFP that answered the same requirement. Do not assume the same three tools apply universally.

```
Spare provides [count] complementary tools for [specific requirement].

First, [tool specific to the capability, sourced].
Second, [tool specific to the capability, sourced].
Third, [tool specific to the capability, sourced].
```

### ERP-partner template

**This is the template that broke in v0.4.0.** It was stamped onto 16+ rows verbatim. Do not reuse the boilerplate; every instance must name the specific capability from the row.

For `ability to X or integrate with ERP to fulfill this requirement` when the deal context indicates the agency has a separately-procured ERP.

```
Spare EAM [describes specifically what Spare does with X, from a sourced past RFP or docs page, not a generic "captures operational data" line]. For [the specific sub-function in this row that is ERP-owned: capitalization, depreciation, GL distribution, AR billing, etc.], [agency's ERP name] is the system of record, and Spare EAM [specifically how Spare integrates for this particular sub-function via Open API]. Specific integration scope will be confirmed during discovery with [agency's] IT team.
```

A row about barcode asset identification should not get the same ERP-partner answer as a row about leased asset tracking. Even if both technically have "or integrate with ERP" in the requirement, the specific capability varies, and the comment must vary accordingly.

### Clarification-request template

For genuinely ambiguous or scope-dependent requirements.

```
Spare's approach here depends on what [agency] is tracking. For [interpretation A], [sourced answer A naming the specific capability]. For [interpretation B], [sourced answer B naming the specific capability]. We would welcome clarification from the agency on [the specific dimension in question].
```

### Short factual template (capability-first)

For narrow, single-feature requirements. One to three sentences.

```
Spare['s] [specific product or feature named in sourced evidence] [does the specific thing asked about, from sourced evidence] [with specifics from the source]. [Optional: one sentence on scope or notable detail.]
```

### Honest-gap disclosure template

When sourced evidence indicates a specific feature is not currently available. See `known-gaps.md` for gap-disclosure patterns. Even gap disclosures must be row-specific: if a past RFP disclosed a gap on warranty notifications, use that disclosure only on warranty-notification rows. Do not paste it onto unrelated rows.

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
- **"Spare EAM supports this requirement as part of its standard feature set. Configuration and specific workflow details will be confirmed during system design and discovery."** This exact vapid sentence shipped in a v0.4.0 run as 50+ row answers. It is meaningless. If you find yourself drafting it, stop and re-read the requirement.

## Product-name catalog

See `scope-of-spare.md` for the canonical product catalog and Drive precedent pointers.

## Numbers and customer references

No cached quantified claims. Every number (uptime, refresh interval, customer metric) must come from a live source every time. The Internal Reasoning column cites the source.
