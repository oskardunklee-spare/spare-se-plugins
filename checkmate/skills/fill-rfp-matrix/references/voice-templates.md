# Voice Templates

Reusable answer shapes. Each template below has been through a real review cycle.

## Three-layer template (platform / service / vehicle)

Use for requirements like "detect faults," "monitor anomalies," "report reliability," "track issues." These often have three valid interpretations that deserve three distinct answers.

```
Spare's [capability] spans three distinct layers.

Platform health: [what Spare does at the platform level, status page, 99.99% uptime target, 24/7 on-call engineering, formal business continuity plan].

Service operations: [configurable alerts, violation triggers, dispatcher actions, cancel duty, pause matching, re-optimize. Spare Analytics dashboards and reports covering key metrics].

Vehicle health: [Spare EAM maintenance tracking, work orders, issue logging. For AV or telemetry-integrated deployments, Open API integration with the vehicle's diagnostics system].

[If the requirement is ambiguous about scope:] We would welcome clarification from the agency on which aspects are most relevant to this requirement.
```

## Three-tool template (audit logs / Resolve / EAM)

Use for "incident logging," "case management," "customer feedback," "complaint tracking," "event review" requirements.

```
Spare provides [count] complementary tools for [requirement].

First, Spare maintains detailed audit logs across all user activity, data access, and security events (who accessed what, from where, when), with historical duty and trip changes also logged.

Second, Spare Resolve is a dedicated case management module for logging, tracking, and managing complaints, incidents, and other cases, with AI Case Intelligence to classify and surface relevant context.

Third, for incidents involving vehicle damage or mechanical issues, Spare EAM provides work order management and issue tracking so operations, fleet, and maintenance teams can close the loop.
```

## ERP-partner template

Use when the agency has explicitly procured a separate ERP and the requirement is phrased `ability to X or integrate with ERP to fulfill this requirement`.

```
Spare EAM maintains full operational asset records (VIN, acquisition date and cost, lifecycle status) and exchanges asset data with [agency's ERP name, e.g. Microsoft Dynamics 365] via Spare's Open API. The [financial function, e.g. capitalization threshold] is owned by [ERP name] as the authoritative financial system, and Spare EAM surfaces the resulting status on the operational asset record so operations users can filter, report, and create work orders against it. Specific integration scope, field mappings, and sync cadence will be confirmed during discovery with [agency's] IT team and [implementation partner if known, e.g. Crowe].
```

Verdict: agency's equivalent of `Y` (or `Y-ND` if explicitly identified as Non-Default). Support: `TPS` / `Third Party` / equivalent.

## Clarification-request template

Use when the requirement is genuinely ambiguous or scope-dependent. The form is: acknowledge the multiple interpretations, answer for each, close with an explicit clarification request.

```
Spare's approach here depends on what [agency] is tracking. For [interpretation A], [answer A with specifics]. For [interpretation B], [answer B with specifics]. [Optionally: interpretation C]. We would welcome clarification from the agency on [the specific dimension in question], particularly around [concrete sub-question].
```

## Short factual template (capability-first)

Use for narrow, single-feature requirements (`Vehicle status`, `Barcode scanning`, `Export to Excel`). One to three sentences total.

```
Spare['s] [Product/Feature] [does X] [with specifics Y]. [Optional: one sentence on scope or notable detail].
```

Examples:

- *"Spare's interactive Live Map gives dispatchers and remote monitoring operators a continuously-updated view of every vehicle, with color-coded status indicators (on-time, delayed, idle, flagged). Status refreshes every 3 seconds on the rider-facing ETA view and every minute on the operations dashboard."*
- *"Spare EAM supports barcode and QR code scanning via the Spare Maintain app (iOS and Android) for asset identification, parts lookup, and inventory transactions."*

## Honest-gap disclosure template

Use inside an answer where Spare mostly meets the requirement but has a specific named gap.

```
[Capability that is supported]. Note: [specific gap] is not currently available. [Workaround or alternative, if any]. [If on roadmap, say so].
```

Example:
*"Spare EAM stores warranty terms and expiration dates on the asset record. Warranty data can be referenced during work-order creation to surface whether an item is still under warranty. Note: automated warranty-expiration email/push notifications are not currently available out of the box; warranty data can be surfaced via scheduled reports or ad-hoc queries."*

## Never-use phrases

Avoid these, they are either AI tells, marketing filler, or inconsistent with Spare's house voice:

- *"leveraging cutting-edge technology"*
- *"seamlessly integrates"*
- *"best-in-class"*
- *"robust and scalable"* (say specifically what scales, e.g. "architected for 145-vehicle fleets and up")
- *"We pride ourselves on..."*
- The em-dash character (`U+2014`) anywhere
- *"elevate"* as a verb
- *"streamlined"* as a pure adjective (OK as a verb with an object: "streamlines dispatch workflows")
- *"powerful"* as an adjective for the platform

## Common product-name references

Spell these exactly as below when naming them in answers:

- Spare Operations
- Spare EAM (full name when first mentioned; subsequent references can drop "Spare EAM" to "EAM" for readability)
- Spare EAM Lite
- Spare Maintain app
- Spare Driver App
- Spare Rider App
- Spare Resolve
- Spare Analytics
- Spare Engage
- Spare Eligibility
- Spare Platform
- Open API (not "API" alone when referring to the Spare Open API)
- Live Map
- Time Travel
- Mission Control dashboards
- AI Case Intelligence
- Scout (Spare's AI reporting tool)

## Common quantified claims (verified from docs, safe to reuse)

- GPS location updates: `every 3-5 seconds`
- Operations dashboard refresh: `every 3 seconds` (rider-facing ETA) and `every minute` (operational metrics)
- Uptime target: `99.99%`
- Status page URL: `sparelabs.statuspage.io` (live + 90-day history)
- GCTD reference result: `100% FTA compliance from day one, 100% mechanic adoption within 30 days, 20% increase in completed inspections, 2 hours saved daily on paperwork`
- Spare customer count: `200+ public agencies across North America since 2015`
- EAM Lite vs Full EAM difference: Full EAM includes Work Orders, PM Scheduling, Parts & Inventory, Vendors & Purchasing, full lifecycle tracking, depreciation, and sub-components; Lite includes only Asset view, Inspections, and Issues

Verify any specific number against the current docs before using, these can drift.
