# Scope of Spare

**Spare ships a broad product catalog.** This file lists it, with Drive pointers for precedent files inside the `Spare General` master folder. Use both the product names and the Drive pointers as anchors when searching for evidence per Rule 1 and Rule 2 in `methodology-rules.md`.

**Do not use this file to conclude that Spare does or does not support a specific feature.** Specific capability status always comes from live evidence (a cited past RFP row or doc page). The catalog below tells you what names to search for; the precedents tell you what Spare has committed to.

## Product catalog

All shipping products. Spell exactly as below when naming them in customer-facing comments.

### Spare Operations
Demand-response dispatch, routing, paratransit, microtransit, on-demand. Live Map, Time Travel, Mission Control dashboards. Dispatcher actions (cancel duty, pause matching, re-optimize).

### Spare EAM
Full Enterprise Asset Management. Includes: Work Order management, Preventive Maintenance scheduling (by time, mileage, or engine hours), Parts Inventory with reorder points and multi-location storerooms, Vendors & Purchasing (POs), Asset Lifecycle tracking, Depreciation, Sub-components (parent/child asset relationships), and the Spare Maintain mobile app for technicians. Includes Non-Vehicle Assets (facilities, equipment, infrastructure) as of the Spring 2026 release.

### Spare EAM Lite
Lightweight version of EAM. Inspections (DVIR pre/post-trip) and Issue tracking only. No work orders, PM scheduling, parts, or vendors. Positioned as an upsell-ready entry point.

### Spare Resolve
Case management with AI Case Intelligence for classifying and surfacing case context.

### Spare Eligibility
Rider eligibility, application workflows, renewals.

### Spare Engage
Rider engagement, communications, bulk messaging, notifications.

### Spare Analytics
Operational reporting, dashboards, custom report builder, SQL access. Scout is the in-product AI reporting assistant.

### Spare Driver App
Driver-facing mobile app. Pre-trip and post-trip inspections, manifest delivery, real-time trip updates.

### Spare Rider App
Rider-facing mobile app. Trip booking, real-time vehicle tracking, notifications.

### Spare Maintain
Mobile app for mechanics and technicians. Digital work orders, parts lookup, photo documentation, offline mode.

### SpareONE
Multi-modal platform for mixed fixed-route + on-demand operations. Fixed-route anti-cannibalization (FRAC) controls.

### Open API
Documented integration surface. Used for ERP integration (Dynamics 365, Tyler Munis), GPS/telematics (Geotab), SSO (Entra), fare (Cubic, Token Transit), GIS (ESRI ArcGIS), HR/payroll, fuel management.

## Service modes Spare has answered RFPs for

From past precedent files in `Spare General`:

- ADA paratransit
- Demand-response / dial-a-ride
- Microtransit
- NEMT
- First-mile / last-mile
- Fixed-route (via SpareONE)
- Enterprise Asset Management (via Spare EAM)
- Fleet maintenance and inspections (via Spare EAM + Maintain + Driver App)
- Rider experience and customer-facing apps

## Drive precedent pointers

All paths are subfolders or files inside the `Spare General` master Google Drive folder. The fill-rfp-matrix skill must anchor in `Spare General` per Rule 1 before drafting. Known EAM-relevant precedents:

- **Laramie Fleet Management Software RFP**, `Laramie RFP - Spare EAM Response Matrix (Updated)`. Recent (April 2026). Answered Y/N/P across fleet and asset management, inventory, fuel, oil, work orders, data conversion, technical requirements, data ownership, and optional Public Works asset management.
- **Calgary EAM Specs**, `Calgary_EAM_Specs_with_Responses_SpareOnly_updated.csv`. July 2025.
- **TCAT EAM RFP**, `TCAT EAM RFP 1-28-26.pdf` and response doc. January 2026.
- **NFTA EAM RFP**, folder contains `NFTA EAM RFP Proposer Pricing Response`, `NFTA EAM RFP Vendor Submittal Checklist`, `NFTA EAM RFP Proposer Roles and Responsibilities`. March 2026.
- **SolTrans EAM RFP**, `SolTrans EAM RFP Scope and Budget`. November 2025.
- **Valley Transit EAM RFP**, folder.
- **EAM RFP - March 2026**, folder.
- **Potential EAM RFP**, folder.
- **Master reference**, `Spare's Master Sample RFP Tech Spec Requirements [MAKE A COPY]`. Canonical Q&A bank across service types.

For non-EAM categories (paratransit, microtransit, fixed-route, fare, rider experience), the `Spare General` folder contains additional precedents; search by agency name and service type.

## Contributing to this file

When Spare ships a new product or major module, add its canonical name to the catalog. When a new RFP precedent lands in Drive, add a pointer under Drive precedent pointers. Do not add feature-level claims (e.g., "supports barcode scanning") here; feature claims belong in the sourced response for a specific RFP row, cited from a past RFP or a doc page.
