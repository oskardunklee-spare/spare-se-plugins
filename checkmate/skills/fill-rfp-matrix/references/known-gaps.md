# Known Capability Gaps

When a requirement asks about one of these, disclose the gap plainly. These are the honesty points that build trust; do not paper over them. Every gap below has been disclosed in at least one past RFP response.

## Spare EAM

| Gap | Disclosure template |
|---|---|
| Safety recall tracking | *"Safety recall tracking is not currently a native feature and is on Spare's product roadmap."* |
| MPG auto-calculation from fuel imports | *"Spare EAM does not currently calculate MPG automatically from fuel import data. Fuel quantity and cost data can be imported and recorded, but MPG/fuel efficiency calculations are not a native feature at this time."* |
| Cost-center structures and cost-center-based billing | *"Spare EAM does not currently support native cost center structures with cost center-based billing. All costs are tracked at the asset and work order level."* |
| Warranty expiration notifications (automated) | *"Automated warranty expiration notifications are not currently available. Warranty data is stored in the asset record and can be referenced manually or via scheduled reports."* |
| Fuel-card / pump-control direct integration | *"Direct integration with fuel cards or pump control systems is not currently available. Integration via Spare's Open API is feasible and would require scoping based on the agency's specific fuel management system."* |
| Waste oil compliance reporting (formal regulatory) | *"Formal regulatory compliance reporting for waste oil disposal is not currently a native feature. Standard inventory transaction history is available and can serve as a basis for compliance documentation."* |
| Predictive lifecycle / replacement scoring (automated) | *"Spare EAM provides lifecycle cost analysis based on age, usage, and maintenance history to support informed asset retention decisions. Automated predictive replacement scoring and algorithmic lifecycle forecasting are not currently available. Data visibility supports informed manual decision-making today."* |
| Inventory turnover reporting (native OOTB) | *"Standard reports include stock valuation and usage analysis by item and location. Inventory turnover reporting is not currently available as a native out-of-box report. Usage trend data is available and can be used to construct turnover analysis through the report builder."* |
| Fuel consumption LTD / FY search (native) | *"Spare EAM tracks mileage at the asset level by date range. Native fuel consumption reporting by LTD and FY with fiscal year search is not currently available out of the box. Fuel data can be imported and queried via the report builder."* |
| Replacement-cost tracked attribute (standard field) | *"Replacement cost as a tracked asset attribute is not currently available as a standard field and will be reviewed during scoping."* |

## Spare Operations

| Gap | Disclosure template |
|---|---|
| Automated PM / inspection reminder notifications (in operations) | *"Note: automated reminders and notifications for scheduled inspections, preventative maintenance, and repairs are not currently supported out of the box."* |
| Grammar check in free-form fields | *"Spell check is provided by the user's browser. Grammar check is dependent on the browser or extensions in use."* |

## Integration scoping (not quite a "gap", but always name)

Spare's Open API supports integration with most third-party systems, but specific integrations are defined during implementation scoping rather than as out-of-the-box features. For these, use `Y-ND` with `E` (Enhancement) where the vocabulary supports that distinction, or `P` (Partial), or the agency's equivalent:

- Tyler Munis
- Microsoft Dynamics 365
- ESRI ArcGIS / other GIS platforms
- Entra / Azure AD SSO
- Geotab and other telematics
- Cubic fare systems
- Fuel management systems (Gasboy, FleetNet, etc.)
- HR/payroll integrations

Template: *"Integration with [system] via Spare's Open API is feasible; the specific connection, data flows, and implementation scope must be confirmed during discovery. A dedicated integration scoping session with the agency's IT team is recommended."*

## Adding to this file

When a new gap is disclosed in a submitted RFP, add it here with the exact disclosure phrasing used and which RFP it came from. Consistent disclosure across deals is the trust-builder.
