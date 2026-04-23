# Disclosing Gaps Honestly

This file is methodology only. It does not list specific capabilities that Spare does or does not ship. That kind of claim goes stale as the product updates.

When sourced evidence (a past RFP response, a Spare docs page, a changelog entry) indicates that a capability is not currently available, disclose the gap plainly in the response. Do not paper over it; gap honesty is the trust-builder that distinguishes Spare's responses from vendor boilerplate.

## Where gap claims come from

A gap claim in your response is legitimate only if you can cite one of:

- A past RFP response where Spare disclosed the same gap (include filename and row)
- A Spare docs page that explicitly says the capability is not available, or is on the roadmap, or requires custom development
- A Notion page or Glean hit from product or engineering describing the gap

If you cannot find a sourced basis for a gap, the verdict is `I` (Need More Info), not `N`. Absence of evidence is not evidence of absence. Spare ships frequently; the feature may have been added since the last RFP precedent you are looking at.

## Gap-disclosure phrasing patterns

When a gap is sourced and you are writing the customer-facing comment, use one of these patterns. The specific feature name and mitigation language come from the source you cited.

### Pattern 1: Not available, on roadmap

```
Spare [...supports the broader capability X...]. Note: [specific sub-feature] is not currently available and is on Spare's product roadmap.
```

### Pattern 2: Not native, workaround exists

```
Spare [...supports the broader capability X...]. Note: [specific sub-feature] is not currently a native out-of-the-box feature. [Cite the workaround from the source: manual process, scheduled report, Open API query, etc.].
```

### Pattern 3: Scoping required

```
Spare [...supports the broader capability X...]. [Specific sub-feature] is feasible via Spare's Open API and would require scoping based on the agency's specific system. A dedicated integration scoping session with the agency's IT team is recommended.
```

### Pattern 4: Requires clarification

```
Spare's approach here depends on what [agency] is tracking. For [interpretation A], [sourced answer]. For [interpretation B], [sourced answer]. We would welcome clarification from the agency on [the specific sub-dimension] so we can confirm the most appropriate response.
```

## Integration scoping

When the requirement is "integrate with [external system X]," the default posture is: Spare's Open API supports integration with most third-party systems, but specific integrations are defined during implementation scoping rather than shipped as out-of-the-box features. Cite this stance from a past RFP response that used it.

The specific status of an integration (pre-built connector vs. scoping-required) should come from the Spare docs or a recent past RFP. Do not assume either direction.

## Contributing to this file

This file intentionally does not list specific gap claims. If you find yourself wanting to add one (e.g., a specific feature that is not native), that is a signal to instead cite the source in the row's Internal Reasoning column and, after submission, note the claim in `CONTRIBUTING.md` with where it was sourced (past RFP filename and date, or doc URL). That way the next SE can re-verify against the current product state rather than trusting a cached claim here.
