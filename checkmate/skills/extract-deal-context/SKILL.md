---
name: extract-deal-context
description: Extract and persist deal context from an agency's RFP document before any matrix drafting begins. Use when the user uploads an RFP PDF and asks to "extract the deal context," "summarize this RFP," "pull the key facts from this RFP," "get me the context for this deal," or when starting a new RFP response workflow. Produces a structured markdown artifact that subsequent fill-rfp-matrix runs reference for every answer.
---

# Extract Deal Context

Read an agency's RFP document (PDF or Word) and produce a structured deal-context artifact. Every row that the fill-rfp-matrix skill subsequently drafts should draw from this artifact. The artifact is the difference between answers that feel generic and answers that sound like they were written by someone who read the RFP.

## What this skill does NOT do

This skill extracts facts. It does not assess whether Spare should bid, whether the RFP fits Spare's product domain, or whether any part of the scope is "out of scope for Spare." When the user invokes Checkmate, the bid decision is already made.

Do not output:

- "This RFP is out of Spare's domain"
- "Recommend no-bid" or fit-check summaries
- Option menus asking the user whether to bid
- Warnings that certain sections appear unfit for Spare
- "Risk and fit notes" that speculate about what Spare does or doesn't ship

If the RFP genuinely has an unusual scope, simply report the scope as a fact (e.g., *"Attachments 2A and 2B are functional-requirement matrices with 201 and 411 rows respectively, covering capital asset accounting and EAM work-order management"*) without any judgment about whether Spare fits. Fit determination happens per-row during `fill-rfp-matrix`, sourced from past Spare RFP responses in Drive, not pre-judged from the RFP text during context extraction.

## When to run this

Run this skill once, at the start of a new RFP response workflow, before any matrix drafting. The output is a single markdown file the SE can inspect, correct, and reuse across multiple drafting sessions for the same deal.

## What to extract

Read the RFP end-to-end (or at least pages 1-20, which contain the Introduction, Background, Scope, and Timeline sections for almost every transit-agency RFP) and produce a markdown file with exactly these sections. Do not invent content. If a section is not addressed in the RFP, mark it `(not stated)` rather than guessing.

### Required sections

**Agency identity**
- Full legal name and short name (e.g., `Champaign-Urbana Mass Transit District (MTD)`)
- Jurisdiction (city, county, state/province)
- Legal classification (municipal corporation, regional authority, transit district, operating partner)
- Governance structure (board of trustees, elected officials, appointed)

**Fleet and operations snapshot**
- Annual ridership
- Revenue vehicles (count and type split: fixed-route buses, paratransit vans, cutaways, other)
- Non-revenue / support vehicles
- Facilities and terminals
- Total tracked assets
- Annual work order volume (if given)
- Parts inventory value (if given)
- Maintenance operations (shifts, staff count, technician count)
- Service modes offered: fixed-route, ADA paratransit, demand-response, microtransit, NEMT, first-mile/last-mile

**Financials and scope**
- Operating budget
- Capital budget
- Fiscal year boundaries
- Subscription year expectation (e.g., `Year 1 begins after go-live`, or `Year 1 begins at kickoff`)
- Contract structure (MSA + SOW, single-award, multi-award)

**Adjacent systems the agency has or is procuring**

This section is the single highest-value piece of context for answer-drafting. List every external system the agency names, along with what it does and whether Spare is expected to integrate with it or replace it.

- ERP (e.g., `Microsoft Dynamics 365`, implemented by `Crowe, LLP`, starting `January 2026`)
- Incumbent / legacy systems being replaced (e.g., `myAvail/ETMS (FleetNet)`)
- GPS / telematics (e.g., `Geotab`, `Samsara`, `Spireon`)
- Fare / payment (e.g., `Cubic fare system with Moneris`, `Token Transit`)
- HR / payroll
- GIS (e.g., `ESRI ArcGIS`)
- SSO (e.g., `Entra`, `Okta`, `Azure AD`)
- Others named in the RFP

**Timeline**
- Release date
- Pre-proposal conference date (if any)
- Written questions deadline
- Proposals due
- Demonstrations (expected window)
- Discovery (expected window)
- Anticipated contract award
- Go-live target / implementation window

**Scope restrictions and instructions**
- What the RFP explicitly excludes (e.g., `This RFP addresses EAM exclusively; financial functions handled by separate ERP procurement`)
- Submission instructions (file format, delivery channel, page limits, formatting requirements)
- Exception/alternative process (Form C at MTD, for example)
- Evaluation criteria and their weights if given
- Whether the agency accepts alternates or only a single solution

**Competitive signals**
- Incumbent vendor (if named or implied)
- Any competitors mentioned by name elsewhere in the RFP (sometimes in reference requirements or past-performance sections)
- Any indication the agency is shopping vs. renewing
- Consulting / procurement advisor (e.g., `GFOA` assisted MTD)

**Regulatory frameworks and notable context (facts only)**
- Regulatory frameworks referenced in the RFP (FTA, ADA, AODA, PIPEDA, GDPR, SOC2, GASB, etc.) and any specific compliance clauses the bidder must respond to.
- Matrix structure observed: number of attachments, rows per attachment, verdict vocabulary, evaluation-weight table if present.
- Anything unusual or agency-specific that a new SE reading the artifact should understand in 60 seconds (e.g., *"GFOA is advising MTD through the selection"* or *"agency just procured ERP separately; EAM scope excludes financial functions"*).

**Do not include a "risk and fit" or "Spare fit assessment" section.** Fit is determined per-row during drafting, by sourced evidence, not by pre-extraction speculation.

## Output artifact

Save the extracted context to `deal-context.md` in the Cowork session's working directory (or the outputs folder if the user is working there). Name the file explicitly so the fill-rfp-matrix skill can pick it up: `<agency-short-name>-deal-context.md` (e.g., `MTD-deal-context.md`, `BC-Transit-deal-context.md`).

Format the file with clear markdown headers matching the section list above so it's both machine-parseable (for the fill skill) and human-readable (for the SE to review).

## How the fill-rfp-matrix skill uses this

At the start of every drafting session, fill-rfp-matrix looks for a deal-context file in the session directory and loads it into working memory. When drafting each row, it references:

- **Adjacent systems**, to name the agency's own ERP, GPS, SSO, etc. explicitly in answers (e.g., "via Spare's Open API, integrated with the agency's Microsoft Dynamics 365 ERP")
- **Fleet snapshot**, to weave in quantified context ("sized appropriately for your 145-vehicle fleet and 11,000 annual work orders")
- **Scope restrictions**, to avoid proposing solutions the agency has explicitly marked out of scope
- **Competitive signals**, to pull the right positioning from competitive-positioning.md
- **Regulatory frameworks and notable context**, to shape what compliance claims need to appear in answers

## After the draft

If the SE corrects any field in the deal-context file during review, those corrections should be reflected in the rest of the filled matrix. Re-run the relevant rows through fill-rfp-matrix rather than hand-editing each one.

## Quality bar

A well-extracted deal-context file enables an SE to onboard onto the deal in 5 minutes. If reading your output takes longer than that, the sections are too long or the formatting is wrong. Dense, scannable, factual. No marketing language, no filler.
