# Invoice SaaS — pSEO example

A small, valid inventory for an Italian invoice-generation SaaS. It shows the core idea: the matrix is a **candidate generator**, not a publishing plan.

## The family

- **Entities:** `designer`, `sviluppatore`, `fotografo`, `consulente`, `artigiano`, `docente`
- **Modifiers:** `forfettario`, `ordinario`
- **Locale:** `it-IT`
- **Raw candidates:** 6 × 2 = 12
- **Published in this example:** 8

## What is published, and why

| URL | Job | Why it passes |
| --- | --- | --- |
| `/fattura/designer` | Entity hub | Different intent from the regime page; links to the regime pages |
| `/fattura/designer/forfettario` | Regime-specific calculation | Unique rules, rates, contributions, worked example |
| `/fattura/sviluppatore` | Entity hub | Same pattern |
| `/fattura/sviluppatore/forfettario` | Regime-specific calculation | Unique data and example |
| `/fattura/fotografo/forfettario` | Regime-specific calculation | Demand and data justify a standalone page |
| `/fattura/consulente/forfettario` | Regime-specific calculation | Demand and data justify a standalone page |
| `/fattura/artigiano/forfettario` | Regime-specific calculation | Unique contribution rules |
| `/confronta/forfettario-vs-ordinario` | Comparison | Different job: choosing a regime, not filing an invoice |

## What is not published

- `/fattura/docente/forfettario` — `eligible`: the data is plausible, but the demand check and the rule review are not complete.
- `/fattura/artigiano` — `eligible`: the entity hub is planned for the next cohort.
- `/fattura/designer/ordinario` — `suppressed`: kept for users, canonicalized to the designer hub until the regime data is complete. It is not in the sitemap.
- `/vecchio/fattura-designer` — `retired`: permanent redirect to the designer hub.

The point is not that 8 is the right number. The point is that **8 pages have a reason to exist**, while the other 4 do not yet.

## Cannibalization note

`/fattura/designer` and `/fattura/designer/forfettario` must target different jobs. If the hub starts answering the regime query, merge them or rewrite the hub. The inventory linter only flags exact duplicate queries; semantic cannibalization still needs a human review.

## Validate it

```bash
python3 scripts/pseo_lint.py examples/invoice-saas/page-inventory.csv
```

Expected result: `RESULT: PASS`.

Try `--json` for CI, or `--strict` to treat warnings as errors.
