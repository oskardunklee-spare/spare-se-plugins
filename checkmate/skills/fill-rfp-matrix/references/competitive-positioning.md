# Competitive Positioning

How Spare positions against named competitors. Use this when the agency's RFP names an incumbent, an alternative vendor, or a legacy system being replaced; or when the deal-context artifact flags a competitive signal. The positioning below comes from Spare's sales enablement and is kept current via Klue.

## Source of truth hierarchy

1. **Spare sales-enablement docs (Spare docs MCP).** The `/sales-enablement/eam/overview` page has built-in battlecards for the most common EAM competitors. Always check there first. Similar pages exist for other product lines (demand-response, fixed-route, SpareOne).
2. **Klue via Glean.** Klue is Spare's competitive-intelligence platform and the authoritative source for up-to-date battlecards, win/loss notes, and pricing intel. Klue content is indexed in Glean. When you need current competitive data for a competitor not documented below, search Glean with queries like `klue battlecard <competitor>` or `competitive positioning <competitor>`. If the incumbent named in the RFP is not in this file, Glean is where to look.
3. **Klue directly.** If Glean comes up short or you need the latest raw battlecard, the SE can open Klue directly. There is not currently an MCP connector for Klue, so this step requires manual lookup.

## How to use positioning in RFP answers

Do not lead with competitor names in customer-facing comments. The answer column should still open with `Spare` per Rule 5 and focus on what Spare does, not what the competitor doesn't. Competitive positioning is used to shape *which* Spare capabilities to foreground. Examples:

- If the incumbent is Fleetio and the RFP heavily emphasizes transit-specific compliance (VMRS, FTA), lean into Spare's transit-specific design and FTA compliance features.
- If the incumbent is RTA and the RFP mentions long implementation timelines as a pain point, lean into Spare's 3-month deployment and cloud-native architecture.
- If the incumbent is AssetWorks and the RFP emphasizes user adoption, lean into the GCTD proof point (100% mechanic adoption within 30 days).
- If the incumbent is myAvail/ETMS (FleetNet), lean into cloud-native architecture, modern mobile experience, and the ability to replace both fleet ops and EAM on one platform.

The goal is not to name the competitor in the answer. The goal is to let the Spare capability that specifically beats the competitor show up more prominently in answers that touch related requirement areas.

## Seeded competitor positioning (as of April 2026)

### Fleetio

- **Win when**: Transit-specific needs, FTA compliance required, multi-depot operations
- **Key differentiator**: Built specifically for public transit, not adapted from commercial fleet
- **Top 3 advantages**: Transit-specific (VMRS codes, FTA compliance built-in); facilities management included (Fleetio doesn't have this); government-ready procurement
- **Their weakness**: Generic commercial fleet tool trying to serve transit
- **Landmines the SE may hear from the customer**: "How does it handle FTA reporting?" (Fleetio struggles with transit compliance); "Can it manage fleet AND facilities?" (Fleetio cannot, requires a separate system); "What's your experience with government procurement?" (limited public-sector references)

### RTA Fleet

- **Win when**: Cloud requirement, modern UI important, quick implementation needed
- **Key differentiator**: 100% cloud-native, no servers required
- **Top 3 advantages**: Cloud-native architecture (no servers, IT overhead, or maintenance); 3-month deployment vs their 9 to 12 months; modern mobile app with high mechanic adoption
- **Their weakness**: Legacy architecture, slow to deploy
- **Pricing intel**: RTA charges approximately $8,500/year for small transit agencies (Duluth Transit example)
- **Landmines**: "What's your total implementation timeline?" (they take 9 to 12 months minimum); "What infrastructure do we need?" (requires on-premise servers and IT staff); "How quickly do mechanics adopt the mobile app?" (poor mobile experience); "Can we see it working today?" (no cloud demo environment)

### AssetWorks

- **Win when**: Ease of use priority, modern technology required, user adoption critical
- **Key differentiator**: Superior user experience with minimal training requirements
- **Top 3 advantages**: Intuitive design (users adopt quickly); minimal training (< 1 week vs their 4 to 6 weeks); 95%+ adoption rate
- **Their weakness**: Complex, expensive, poor user adoption
- **Landmines**: "How long does training typically take?" (they require 4 to 6 weeks); "What's the typical user adoption rate?" (known for poor mechanic adoption); "Can we start with a pilot?" (all-or-nothing pricing); "How many dedicated IT resources needed?" (significant IT support required)

### myAvail / ETMS (FleetNet)

- Legacy on-premise transit-ops-and-EAM combined system; being actively replaced across several agencies (MTD is replacing it, for example)
- Spare positions as the modern cloud-native replacement that covers both ops and EAM in one integrated platform
- **Verify with Klue**: This positioning is based on limited data. Before a Spare-vs-myAvail-sized deal, search Glean for `klue battlecard myAvail` or `competitive myAvail FleetNet` to pull the current battlecard.

### Other competitors worth checking Klue for

Spare likely has Klue battlecards for additional competitors not fully documented above. If the RFP names any of these as incumbent or competitor, search Glean before drafting:

- Trapeze (TransitMaster, PASS, FX-Paratransit)
- Hexagon / Infor (EAM, HxGN EAM)
- Routematch
- Cevotec / Ecolane
- TripSpark / Trapeze Flex
- Via Transportation
- Transdev (operator, not software, but sometimes the operational incumbent)
- Blaise Transit (for small paratransit agencies)

## Win-when heuristics across the board

Regardless of which specific competitor is named, Spare's core win conditions are consistent. Lean on these when the RFP emphasizes any of:

- **Cloud-native / SaaS delivery.** Spare is purpose-built for this; legacy competitors are not.
- **Modern mobile experience.** Spare Maintain App and Spare Driver App consistently outperform legacy mobile.
- **Fast deployment.** Spare averages 3 months; legacy competitors average 9 to 18 months.
- **Unified platform.** Spare covers ops, EAM, and customer experience in one integrated platform; most competitors cover only one of these.
- **Transit-specific compliance.** FTA reporting, VMRS codes, NTD compliance, ADA/AODA accessibility are all built in.
- **Open API and integration-friendly.** Spare is integration-first architecture; many competitors are closed systems.

## Updating this file

When Klue publishes new competitive data, or when an SE learns a new landmine or pricing signal from a live deal, update this file. Add the date of the update at the top of the relevant competitor section so the file's freshness is auditable.
