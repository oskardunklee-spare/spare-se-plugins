# Voice Templates

**Read this first.** These templates are skeletons, not sentences. Every filled-in row must be tailored to the specific requirement text of that row. If two rows in the same section end up with identical or near-identical comments, you did it wrong, the requirement text differs between rows, so the comment should too.

## Anti-pattern: lifting precedent comment text verbatim

The precedent corpus contains answered rows from past Spare RFPs. Those rows vary in quality: some are polished final submissions, others are draft / working matrices where SEs left behind scratch notes, open questions, and product-team shorthand in the comment field. Examples from live v1.3.1 runs where precedent-note text leaked into customer-facing drafts:

| Leaked draft | What got carried forward |
|---|---|
| *"Specifically, TBD - Custom Field and Workflow with notification? Usse asset type as SW."* | Literal "TBD", open question mark, typo ("Usse"), engineering shorthand ("SW") |
| *"Specifically, custom Field, may need custom reporting. Could use asset types as well for filtering."* | Internal scratch musing |
| *"Specifically, full ERP integration via modules on purchasing. Not likely to have and requires decision on pursuit."* | Product-team language ("Not likely to have", "requires decision") |
| *"Specifically, no capability to expose cell phone number. Might not want to do this globally for security."* | SE's private aside, not a customer answer |

An agency reading these will see TBDs, typos, engineering jargon, hedging, and unresolved questions, and score the response as unprofessional or unprepared.

**Rule: the precedent comment is a source, not a copy.** Read it, extract the factual content about the capability, and rephrase in Spare's voice using the templates in this file. Do not paste precedent comment text directly into drafts. Do not copy forward any of these internal-note markers:

- Literal `TBD`, `TBD:`, `TBD -`
- Question marks inside the answer (except where the requirement literally asks for clarification)
- Hedging from notes: `might have complexity`, `might not want`, `not likely to have`, `requires decision`, `need custom`, `could use`, `may need`
- Obvious typos or engineering shorthand that wouldn't appear in a published doc (`Usse`, all-caps abbreviations mid-sentence, fragmentary "Custom Field" as a noun phrase)
- Meta-commentary: `Specifically,` followed by a scratch-note clause; `This would be addressed as a configuration or custom enhancement during implementation` as a vapid fallback (use only when the precedent explicitly supports it)

If the precedent comment visibly reads as a draft note rather than a polished answer (contains any of the markers above, has typos, or reads as a private aside), treat it as a weak signal. Either corroborate via docs per Rule 25, pick a different precedent, or mark the row `I` (Need More Info).

## Anti-pattern: forcing a broken 'Spare' opener

Every customer-facing comment opens with `Spare` or `Spare's`. But if the natural continuation of that opener produces broken English, rewrite the sentence; don't force it.

Example from a live v1.3.1 run:

Bad: *"Spare's within Spare EAM, alerting user if item needing repair is within warranty date is covered with one noted sub-feature."*

The draft opened with "Spare's" but the continuation "within Spare EAM" reads as a possessive followed by a preposition, which isn't grammatical. Rewrite:

Better: *"Spare EAM supports warranty-aware work-order alerts when an asset comes in for repair. [Specifics from the cited precedent.]"*

Better: *"Within Spare EAM, warranty-date alerts fire when an asset comes in for repair. [Specifics.]"*  — opens with "Within Spare EAM" (not "Spare's"). The review skill treats *"Within Spare EAM..."* as an acceptable opener because Spare is still the first named subject.

Rule: if the opener doesn't parse as a grammatical English sentence, the row is a blocker. Rewrite. Banned constructions include "Spare's within Spare EAM, ...", "Spare's regarding X, ...", "Spare's in terms of Y, ..." — any "Spare's" followed directly by a preposition.

## Anti-pattern: splicing the requirement text into the answer

A grammar-and-tone failure mode where the model lifts the raw requirement phrase and inserts it as a noun into a generic sentence template. Examples caught in live runs:

| Requirement | Bad draft |
|---|---|
| "Ability for system billing to integrate with ERP for AR" | *"Spare EAM addresses ability for system billing to integrate with ERP for AR."* |
| "Restrict access to employee & vendor pay rates" | *"Spare EAM's native functionality includes restrict access to employee & vendor pay rates."* |
| "Search for data using a variety of search criteria (wildcard, less than, greater than, etc.)" | *"Spare EAM is configured for search for data using a variety of search criteria."* |

These all read broken because the requirement is being pasted as an object into a generic sentence skeleton ("Spare EAM addresses [X]", "is configured for [X]", "includes [X]") rather than responded to in natural English. An evaluator reads them as vendor boilerplate and marks the row down.

**Rule: rephrase the requirement in plain English before answering it.** Read the requirement. Identify the specific capability it asks about. Write a sentence that answers "does Spare support this?" in natural language, then pull specifics from the cited precedent. Do not paste the requirement phrase into a sentence template.

Good versions of the examples above:

| Requirement | Better draft |
|---|---|
| "Ability for system billing to integrate with ERP for AR" | *"Spare's Open API exposes billing events (invoices, receivables, payment status) for integration with the agency's ERP. Specific field mappings and cadence are scoped during implementation."* |
| "Restrict access to employee & vendor pay rates" | *"Spare EAM's role-based access control governs visibility of sensitive fields, including employee and vendor pay rates. Permissions are configured per role during implementation."* |
| "Search for data using a variety of search criteria" | *"Spare EAM supports flexible record search across standard operators (equals, not-equals, less-than, greater-than, range, partial match, wildcard) on all core entity fields."* |

## Anti-pattern: copy-paste across rows

**This is the most common failure mode and it is a blocker.** Example of what NOT to do (taken from a v0.4.0 run that shipped wrong):

Row 19: *"Spare EAM captures the operational data at the asset and work order level and exchanges it with MTD's Microsoft Dynamics 365 ERP via Spare's Open API..."*

Row 20: *"Spare EAM captures the operational data at the asset and work order level and exchanges it with MTD's Microsoft Dynamics 365 ERP via Spare's Open API..."*

Row 21: *"Spare EAM captures the operational data at the asset and work order level and exchanges it with MTD's Microsoft Dynamics 365 ERP via Spare's Open API..."*

Fifteen more identical rows.

Each row in the matrix asks about a different capability (asset disposal, CFDA tracking, barcode scanning, GIS integration, document attachments, leased assets). The comments must address each specific capability using sourced language from a past RFP or Spare docs. An evaluator reading 16 identical comments marks the submission as vendor boilerplate and scores it low.

**Rule: every comment must quote or paraphrase the specific capability named in the requirement text.** If the requirement says "barcode technology for asset identification," the comment must mention barcode. If the requirement says "GIS integration for asset location," the comment must mention GIS. A generic "Spare EAM captures operational data" comment that could paste onto any row is wrong.

**Rule: two rows with comments sharing more than 55% of their text is a bug.** The `review-rfp-draft` skill flags this automatically at `difflib.SequenceMatcher(...).ratio() > 0.55`. Before handoff, verify each row's comment addresses that row's specific requirement.

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

### Integration / API answer template (default for ALL integration asks)

**This template applies to every integration category, not just ERP.** Use it for any requirement about exchanging data with an external system: ERP, GL, fare, payment processor, scheduling, AVL / telematics, GIS, CRM, ITSM, eligibility, identity / SSO, document management, or anything else. The default framing is **capability + scope**, not a commitment to a specific partner product.

```
Spare exposes a public Open API covering [specific entities named in the sourced precedent: work orders, assets, parts, duties, requests, etc.]. [Optional specifics from the precedent: auth method, webhook support, rate limits, sync cadence.] Specific integration scope with the agency's [integration category, e.g. ERP, fare system, telematics provider, scheduling system, GIS, etc.] is confirmed during discovery and implementation.
```

**Do not name a specific third-party product in the comment unless that product is explicitly named in the current deal's `<agency>-deal-context.md` artifact.** This applies to every integration type, not just ERPs:

| Category | Common names to gate behind deal-context |
|---|---|
| ERP / GL | Microsoft Dynamics 365, Workday, SAP, NetSuite, PeopleSoft, Oracle |
| Scheduling / paratransit | Trapeze, Ecolane, RouteMatch, myAvail |
| Fare / payment | Cubic, Moneris, Genfare, Stripe |
| Telematics / AVL | Geotab, Samsara, INIT, Clever Devices |
| CRM / ITSM | Salesforce, HubSpot, ServiceNow |
| Implementation partners | Crowe, Deloitte, Accenture, etc. |

Precedents in the corpus are from specific past agencies and often carry customer-specific integration names (e.g. MTD's Dynamics 365 implementation, a specific agency's fare system, a specific telematics provider). Those names must not be carried into a new draft for a different agency. The review skill flags any unsourced third-party name as a blocker, regardless of integration type.

Good default when the deal context doesn't name a specific system:

> *(ERP question)* *"Spare exposes a public Open API covering work orders, assets, parts inventory, vendors, and purchase orders. The API supports REST authentication, webhook events, and bulk export. Specific integration scope with the agency's ERP is confirmed during implementation."*

> *(Telematics question)* *"Spare consumes real-time GPS and vehicle-ID feeds from the agency's AVL / telematics provider via the Open API for live dispatch and rider ETAs. Specific integration with the agency's telematics system is confirmed during implementation."*

> *(Fare question)* *"Spare's Open API exposes booking, pricing, and payment-status events for integration with the agency's fare system. Specific integration scope is confirmed during implementation."*

Good when the deal context DOES name a system (e.g. MTD's deal-context.md lists "Microsoft Dynamics 365"):

> *"Spare EAM exchanges work order and asset-lifecycle events with MTD's Microsoft Dynamics 365 via Spare's Open API, with specific field mappings confirmed during discovery."*

Better to say "the agency's X" and let implementation scope the specifics than to commit Spare to a named integration we haven't confirmed.

### ERP-partner template

**This is the template that broke in v0.4.0.** It was stamped onto 16+ rows verbatim. Do not reuse the boilerplate; every instance must name the specific capability from the row.

**Use this template ONLY when the agency's `<agency>-deal-context.md` explicitly names the ERP.** If the deal context doesn't name one, fall back to the Integration / API answer template above and say "the agency's ERP," not a guessed product name.

For `ability to X or integrate with ERP to fulfill this requirement` when the deal context indicates the agency has a separately-procured, named ERP.

```
Spare EAM [describes specifically what Spare does with X, from a sourced past RFP or docs page, not a generic "captures operational data" line]. For [the specific sub-function in this row that is ERP-owned: capitalization, depreciation, GL distribution, AR billing, etc.], [agency's ERP name, from deal-context only] is the system of record, and Spare EAM [specifically how Spare integrates for this particular sub-function via Open API]. Specific integration scope will be confirmed during discovery with [agency's] IT team.
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
- Meaningless hedge phrases from v1.3.1 runs: *"with the caveat noted"*, *"with one noted sub-feature"*, *"with one scoped sub-feature flagged"*, *"sub-feature flagged"*, *"is covered with the caveat noted"*. These phrases are Claude-invented filler that reads as vague and defensive. If the precedent genuinely indicates a partial or noted capability, say so in specific terms from the precedent (e.g. *"Spare EAM supports X; Y requires configuration at implementation"*) rather than wrapping it in hedge vocabulary.
- *"This is tracked on Spare's product roadmap"* as a fallback closer. Only include roadmap language when a sourced precedent or docs page explicitly confirms the feature is on the roadmap. Otherwise it's a guess that can become a contractual obligation.
- *"This would be addressed as a configuration or custom enhancement during implementation"* as a universal vapid fallback. Use only when the precedent or docs explicitly confirm it.

## Product-name catalog

See `scope-of-spare.md` for the canonical product catalog and Drive precedent pointers.

## Numbers and customer references

No cached quantified claims. Every number (uptime, refresh interval, customer metric) must come from a live source every time. The Internal Reasoning column cites the source.
