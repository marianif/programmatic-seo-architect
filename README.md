# Programmatic SEO Architect

An [Agent Skills](https://agentskills.io/specification)–compatible skill for designing, building, and operating **Programmatic SEO** systems that turn structured data into useful pages at scale.

It is not a "write 10,000 articles" prompt. It is an operating model:

`source data → page candidates → eligibility gates → rendered page → discovery → indexing → measurement → pruning`

The skill's bias: publish the **smallest number of pages that create real value**, with the data model, rendering, indexing, and pruning infrastructure to keep them useful.

> **Also known as:** programmatic SEO skill · pSEO architecture · data-driven SEO · page registry · entity pages · location pages · directory SEO · comparison pages at scale · Next.js pSEO · Nuxt pSEO · ISR/SSG for SEO · JSON-LD at scale · sitemap automation · IndexNow · Google Indexing API · Claude Code / OpenCode / Codex / Cursor Agent Skill.

## Why this exists

Most pSEO advice stops at "find a pattern, generate the combinations, add JSON-LD". That produces thin pages, soft 404s, index bloat, and occasionally a manual action.

This skill starts from the parts that decide whether the system survives:

- Does the page have a job and unique data?
- Is the combination eligible, or just mathematically possible?
- Is the page server-rendered and self-canonical?
- Does the sitemap contain only real, published, indexable URLs?
- Is indexing automated with the **correct** provider for each engine?
- What gets measured, and what gets pruned when it fails?

## What it corrects

| Common pSEO advice | The correction |
| --- | --- |
| "Generate every combination in the matrix." | Compute candidates, then publish only those that pass the eligibility gates. |
| "Zero 404s: show a friendly page for every URL." | Invalid combinations return `404`/`410`; a soft 200 wastes crawl budget. |
| "Send every new URL to the Google Indexing API." | Google limits it to `JobPosting` and `BroadcastEvent`; use sitemaps and internal links for the rest, plus IndexNow for Bing/Yandex/Seznam/Naver. |
| "Add FAQPage schema for rich results." | Google retired the FAQ rich result in May 2026. Keep useful FAQs, not the myth. |
| "Use `export const revalidate = 86400` everywhere." | Next.js 16 with Cache Components removed that config; use `'use cache'`, `cacheLife()`, and `cacheTag()`. |
| "Add JSON-LD and the page is optimized." | Structured data describes visible content; it does not fix thin pages or guarantee anything. |
| "More pages mean more traffic." | More thin pages mean index bloat, cannibalization, and pruning work. |

## What it covers

| Area | What the skill does |
| --- | --- |
| Strategy | Page families, demand validation, pilot design, kill criteria |
| Data model | Page registry, sources, facts, provenance, statuses, constraints |
| Quality | Eligibility gates, uniqueness rubric, cannibalization checks |
| URLs | Hierarchy, canonicals, pagination, facets, redirects, i18n |
| Rendering | Next.js 15/16, Nuxt 4, Astro, SvelteKit; SSG, ISR, SSR, cache tags |
| Metadata | Title/description formulas, hreflang, Open Graph |
| Structured data | Type selection, `@graph`, validation, FAQ deprecation, safety |
| Indexing | Sitemaps, IndexNow, correct Google Indexing API use, event pipeline |
| Operations | Canary launch, QA gates, rollback, monitoring, pruning |

## Install

```sh
npx skills add marianif/programmatic-seo-architect
```

The [skills CLI](https://github.com/vercel-labs/skills) detects your installed agents, clones the repo and links the skill into each one.

```sh
# Install globally for Claude Code and OpenCode, non-interactive
npx skills add marianif/programmatic-seo-architect -g -a claude-code -a opencode -y

# Inspect before installing
npx skills add marianif/programmatic-seo-architect --list
```

<details>
<summary>Manual install (no Node)</summary>

Clone the repository into the skills directory of your harness, keeping `SKILL.md`, `references/`, `assets/`, and `scripts/` together under a folder named `programmatic-seo-architect`:

```sh
git clone https://github.com/marianif/programmatic-seo-architect.git <skills-dir>/programmatic-seo-architect
```

| Harness | Typical skills directory |
| --- | --- |
| Claude Code | `~/.claude/skills/programmatic-seo-architect/` |
| OpenCode | `.opencode/skills/programmatic-seo-architect/` (project) or `~/.config/opencode/skills/programmatic-seo-architect/` |
| Codex / Cursor / other Agent Skills runtimes | that runtime's documented skills directory |

</details>

No build step. The validator is a single Python 3 file with no dependencies.

## Quick start

Ask the agent:

- "Use Programmatic SEO Architect to design a pSEO pilot for our invoice SaaS. We have 6 professional roles and 2 tax regimes. Build the matrix, the eligibility gates, and a 30-page pilot plan. Do not generate pages yet."
- "Audit our existing pSEO system. We have 40,000 location pages and only 3,000 are indexed. Find the thin-content, canonical, and internal-linking causes before recommending more pages."
- "Model a page registry in PostgreSQL for a directory of 12,000 services across 300 cities. Include statuses, provenance, quality gates, and an indexing event table."
- "Implement the Next.js route for our pSEO family. We are on Next.js 16 with Cache Components. Use ISR for the top 500 pages and on-demand rendering for the rest."
- "Review our sitemap and indexing pipeline. We currently send every URL to the Google Indexing API. Correct the architecture and keep what still works."

The agent should inspect the repository first, ask only for missing context, and produce the artifacts listed in `SKILL.md` before writing production code.

## The pSEO contract

These are the non-negotiables in `SKILL.md`:

1. Page count is not a KPI.
2. Never ship the Cartesian product.
3. Every published page has a job, unique data, and a reason to exist.
4. Invalid or unpublished combinations return `404`/`410`, not soft 200s.
5. Only published, canonical, 200 pages go in sitemaps.
6. One self-referencing canonical per page.
7. Primary content and metadata are server-rendered.
8. Structured data describes visible content only.
9. The Google Indexing API is only for `JobPosting` and `BroadcastEvent`.
10. Every launch has measurement and a pruning plan.

## What makes it different

- **It corrects the common pSEO myths.** The Google Indexing API is not a general-purpose indexing button; FAQ rich results were retired in May 2026; Next.js 16 removed `revalidate` under Cache Components; `middleware.ts` is now `proxy.ts`.
- **It treats quality as a gate, not a score.** A page that fails a gate is not published, even if its priority score is high.
- **It includes a page registry, not just a template.** Statuses, provenance, content hashes, `lastmod`, and indexing events are part of the system.
- **It includes pruning.** The skill defines kill criteria and a review cadence, because pSEO without pruning becomes index bloat.
- **It gives the agent a deterministic validator.** `scripts/pseo_lint.py` checks the inventory before deploy.

## Search terms

If you arrived here searching for any of these, this is the skill:

`programmatic seo` · `pseo` · `pseo architecture` · `programmatic pages` · `data-driven seo` · `page registry` · `page matrix` · `entity pages` · `location pages` · `directory seo` · `comparison pages` · `calculator pages` · `next.js seo` · `nuxt seo` · `astro seo` · `isr` · `ssg` · `ssr` · `edge caching` · `json-ld` · `structured data` · `sitemap index` · `indexnow` · `google indexing api` · `search console api` · `thin content` · `scaled content abuse` · `doorway pages` · `cannibalization` · `crawl budget` · `indexing pipeline` · `claude code skill` · `opencode skill`

## Package contents

- `SKILL.md` — core workflow, contract, framework guidance, deliverables.
- `references/page-model.md` — page families, demand, uniqueness, data model, worked example.
- `references/rendering-and-caching.md` — Next.js, Nuxt, Astro, SvelteKit, cache headers, invalidation.
- `references/structured-data.md` — schema selection, `@graph`, validation, FAQ deprecation, safety.
- `references/indexing-and-measurement.md` — sitemaps, IndexNow, Google API limits, event pipeline, pruning.
- `references/qa-and-operations.md` — launch checklist, canary, rollback, incident playbook.
- `references/sources.md` — official documentation and access dates.
- `assets/pseo-spec-template.md` — fill-in specification.
- `assets/page-registry.sql` — PostgreSQL schema with constraints and a sitemap view.
- `assets/page-inventory-template.csv` — inventory columns.
- `scripts/pseo_lint.py` — deterministic inventory validator.
- `scripts/test_pseo_lint.py` — its test suite.
- `examples/invoice-saas/` — a small valid inventory with the reasoning behind the published subset.

## Validate the example

```bash
python3 scripts/pseo_lint.py examples/invoice-saas/page-inventory.csv
python3 -m unittest scripts/test_pseo_lint.py
```

## Scope and limits

In scope: pSEO strategy, data modeling, page registry, route architecture, rendering and caching, metadata, structured data, sitemaps, indexing automation, internal linking, QA, measurement, and pruning.

Out of scope by default: writing individual editorial articles, buying links, generating pages without unique data, and publishing automatically without review.

The skill is **instructions plus a validator**, not a crawler, keyword database, hosting platform, or publishing system. Live demand, ranking, and indexing observations require the project's analytics, Search Console, or web access. It does not guarantee rankings, indexing, rich results, or AI citations.

## Compatibility

Works with any Agent Skills runtime: Claude Code, OpenCode, Codex, Cursor, Gemini CLI, GitHub Copilot, Windsurf, and others that support `SKILL.md` with progressive disclosure.

Framework code is version-aware. The Next.js sections distinguish Next.js 15 from Next.js 16 with Cache Components; verify the installed version before copying.

## License

MIT. See [LICENSE](LICENSE).

## Sources

The technical guidance was reviewed against official documentation on **2026-10-21**. See [references/sources.md](references/sources.md) for the list and the access dates. Search features and framework APIs change; re-check before relying on a quota or a rich-result feature.
