# Research and scope — 16 October 2026

## Brief

User: Manufacturing and procurement engineers reviewing a multilevel BOM export before a material estimate.

Pain: Shared subassemblies and decimal quantities make spreadsheet multiplication easy to undercount; a missing leaf price should not silently look like a complete estimate.

Smallest useful capability: Propagate exact demand through a multilevel CSV BOM, combine shared paths once at each part, and show leaf costs plus an edge-by-edge quantity ledger.

Acceptance: Shared diamond propagation yields 4.6 leaf units and an exact 11.5 subtotal for the synthetic two-unit root; missing prices withhold the total; cycles fail; deep chains do not require Python recursion.

Demand is inferred from the workflow and adjacent public discussions, not a verified request for this project. Discovery: precise GitHub topics, this runnable example and the chronological profile index; no unsolicited outreach or activity manipulation.

## Comparables

Live GitHub repository search, sort **Most stars**, query `inventory management in:description`. Highest-star relevant comparable found within this search scope: **inventree/InvenTree**. Search coverage is limited; this is not an exhaustive worldwide ranking. Broad queries returned unrelated products and were filtered by the actual user workflow.

| Repository | Stars observed | Last push observed (UTC) | Archived | API license classification |
| --- | ---: | --- | --- | --- |
| [inventree/InvenTree](https://github.com/inventree/InvenTree) | 7717 | 2026-10-16T04:54:37Z | False | MIT |
| [INTI-CMNB/KiBot](https://github.com/INTI-CMNB/KiBot) | 753 | 2026-10-15T16:20:14Z | False | AGPL-3.0 |
| [hildogjr/KiCost](https://github.com/hildogjr/KiCost) | 627 | 2026-07-08T14:46:35Z | False | MIT |

Exact observation times, README blob identities and up to five issue/PR references per comparable are in [research provenance](RESEARCH_PROVENANCE.json). NOASSERTION means the API did not classify the license; it is not permission to reuse. Stars are discovery evidence, not a measure of quality, performance or reliability.

InvenTree already documents BOM pricing, cost ranges and broader stock/pricing workflows. KiCost already builds quantity-adjusted supplier/cost spreadsheets, including handmade CSVs. KiBot automates KiCad outputs. Our narrower user path is an explicit two-CSV material rollup without a server or supplier lookup, not a claimed missing competitor capability.

Workflow alternatives: InvenTree for managed inventory/BOM pricing; KiCost for electronics supplier-cost spreadsheets; KiBot for reproducible KiCad outputs; a hand-maintained spreadsheet for a small one-off estimate.

Our install is a small Python wheel and two or fewer input steps, with a synthetic example and explicit failure states. Competitors offer broader interfaces, integrations, formats, documentation and support communities; their current READMEs/code and issue discussions were inspected, but their installations, reliability, support response and time to first useful result were not measured here. Our successful example establishes only our stated behavior. Licensing was recorded, not used as a proxy for capability.

Portfolio distinction: table-reconcile compares captured keyed tables; invoice-rounding-ledger allocates invoice/tax rounding; backup-chain-audit follows preservation ancestry. This project performs multilevel bill-of-material quantities and material cost aggregation from CSV.

## Claims and reuse

No technical performance benchmark was conducted. There is no speed, memory, reliability or feature-absence superiority claim. Standard algorithms/formats are not inventions of this project. Source references were read for semantics and workflow comparison; implementation, prose and synthetic fixtures were written for this project. No third-party code, font assets or sample user data is bundled. No competitor logos/branding are reused.
