# Review input — ir-20261014-v1

Scope: data integration only; no application, training, bulk translation or source edits.

Review these authoritative local inputs, relative to repository root:
- data/TomatoAI/data/dataset-registry.json (current_run selects five immutable runs).
- data/TomatoAI/data/processed/plantexpert-tomato/pex-b3da04d66a031756/cards/*.json (all 17 cards).
- data/TomatoAI/data/processed/plantexpert-tomato/pex-b3da04d66a031756/label-knowledge-mapping.json
- data/TomatoAI/data/processed/plantexpert-tomato/pex-b3da04d66a031756/glossary-vi-draft.json
- data/TomatoAI/data/reports/plantexpert-tomato/pex-b3da04d66a031756/{summary,source-schema,review-queue}.json
- data/TomatoAI/data/reports/plantvillage/pv-d9e4c21eec8e9172/summary.json
- planning/tomato-desktop/knowledge-localization-edtech.md
- planning/tomato-desktop/architecture.md
- planning/tomato-desktop/README.md

Questions: label/condition/card identity; evidence versus expert approval; per-claim source and chemical gates; independent translation approval; healthy/basic-care boundary; class-index/version/hash contract; grouping readiness; cultivation datasets outside MVP.

The input is a document/data-contract bundle. It is not evidence that classifier labels or advice are professionally approved. No model/checkpoint exists. Draft planning remains unofficial.
