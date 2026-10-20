# Page model, demand, and eligibility

This reference turns the pSEO idea into a defensible page set. Read it before designing the database or the route.

## 1. The page family

A **page family** is a repeatable page type with one intent, one template, and one data contract. Examples:

- `/software/[slug]` — entity page for a software product.
- `/software/[slug]/for-[use-case]` — entity × use case.
- `/dentist/[city]` — location page.
- `/compare/[a]-vs-[b]` — comparison page.
- `/integrations/[a]/[b]` — integration page.
- `/calculator/[scenario]` — calculator page.
- `/statistics/[topic]` — data/report page.

A family is not "all pages that use the same component". It is a promise: every URL in the family answers the same kind of question with the same kind of evidence.

### Family selection test

Score each candidate family 1–5 on:

| Criterion | Question |
| --- | --- |
| Demand | Is there a query cluster with real volume or clear business value? |
| Data advantage | Do we have facts a generic writer does not? |
| SERP weakness | Are current results generic, stale, incomplete, or hard to use? |
| Business value | Does a visit plausibly lead to the product's valuable action? |
| Build feasibility | Can we model the data and render the page reliably? |
| Maintenance | Can we keep the facts fresh at the claimed cadence? |
| Risk | Is the topic regulated, sensitive, or prone to policy issues? |

A family with demand but no data advantage is a content project, not a pSEO project. A family with data but no demand is a dataset looking for an audience.

## 2. Demand validation

Use the strongest evidence available, in this order:

1. **First-party Search Console data.** Queries the site already receives, pages with impressions but poor CTR, queries with no dedicated page.
2. **Internal search and support logs.** What users type into the site search, what they ask support, what sales hears.
3. **Keyword research tools.** Cluster volume, not exact-match volume. Treat third-party volumes as estimates with a provider and date.
4. **SERP inspection.** What ranks, what the results actually answer, whether the intent is transactional, informational, local, or navigational.
5. **Competitor coverage.** Pages that attract links or rank for the cluster; not proof of demand by itself.
6. **Paid search.** Impressions, clicks, and conversion rate by query theme, if available.

### Query clusters, not exact matches

A page can serve a cluster:

```text
primary query: "fattura forfettario designer"
variants:
  - "fattura elettronica designer forfettario"
  - "come fare fattura forfettario designer"
  - "fattura professionista forfettario"
  - "calcolo fattura forfettario designer"
```

The page targets the cluster's **job**, not every string. Do not create one page per variant unless the answers genuinely differ.

### Demand labels

Record the evidence type next to every number:

- `measured` — first-party analytics, Search Console, paid search.
- `estimated` — keyword tool, third-party panel, model.
- `observed` — SERP inspection, competitor page, internal search.
- `hypothesis` — reasoned guess, not yet tested.

Never present an estimate as measured. Never invent a volume to justify a page.

### When demand is thin

If a combination has no measurable demand:

- Do not publish it as a standalone indexable page.
- Keep it as a filter, an on-page section, or a query parameter on a stronger page.
- Or include it in a pilot with an explicit hypothesis and a kill date.

## 3. The matrix and the eligibility gates

```text
entities   = the things the page is about (roles, products, cities, services)
modifiers  = the dimension that changes the answer (use case, regime, attribute)
locales    = the language/market versions that are genuinely different

candidates = entities × modifiers × locales
published  = candidates ∩ eligibility
```

The full product is usually enormous. The published set should be much smaller.

### Gate definitions

| Gate | Pass condition | Evidence to store |
| --- | --- | --- |
| Demand | Cluster has volume, GSC impressions, internal demand, or documented strategic value | source, metric, date |
| Data | At least `N` unique facts (default 5), each with a source | fact rows, provenance |
| Differentiation | No duplicate content hash; material difference from siblings | hash, similarity score |
| Utility | The page supports a task or decision | template section map |
| Trust | Sources, dates, author/reviewer where needed | source URLs, reviewer |
| Technical | Server-rendered, self-canonical, valid schema, acceptable CWV | crawl, validator |
| Economics | Expected value > build + maintenance cost | estimate, owner |
| Risk | No legal, privacy, trademark, or policy blocker | review note |

Gates are pass/fail. A page that fails one gate is not published, even if its total score is high.

### Prioritization score

For pages that pass all gates, rank with a simple weighted score:

```text
priority = 0.35 * demand
         + 0.25 * data_advantage
         + 0.20 * business_value
         + 0.10 * serp_weakness
         + 0.10 * confidence
         - 0.15 * maintenance_cost
```

All inputs 0–5. The weights are a starting point, not a law. Document any change.

## 4. The uniqueness rubric

"Unique content" is not a word count. It is a set of facts, structures, and judgments that a sibling page cannot reuse unchanged.

A page is **materially unique** when at least three of these are true:

- It has unique facts or measurements (prices, rules, availability, local data).
- It has a unique data table or calculator output.
- It has a unique decision or recommendation, with reasons.
- It has a unique example, case, or source.
- It has unique local or regulatory context.
- It has unique images, charts, or maps generated from the data.
- It answers a different intent than its siblings.

A page is **template-only** when the only changes are the entity name, city, or a synonym. Template-only pages belong on a hub page or in a filter, not in the index.

### Similarity checks

Use two layers:

1. **Exact hash.** Hash the normalized main content (strip navigation, footer, shared boilerplate). Identical hashes are duplicates.
2. **Near-duplicate score.** Shingle the main text (e.g., 5-word shingles) and compute Jaccard similarity, or use embeddings. A high score (e.g., > 0.8) is a review flag, not an automatic deletion; some legal or product pages legitimately share language.

Do not publish a cluster of near-duplicates. Consolidate them into one strong page or differentiate the data and the answer.

### Thin-content patterns to reject

- "X in [city]" with no local address, local proof, local pricing, or local rules.
- "X for [role]" where the answer is identical for every role.
- "X vs Y" with no real comparison data, only a generic feature list.
- A page whose H1 is the only unique element.
- A page that exists to link to another page (doorway).
- A page that reproduces a feed or search result without added analysis.
- A page with a fake "updated today" stamp but unchanged data.
- A page with invented reviews, ratings, or testimonials.

## 5. Worked example — invoice SaaS (Italy)

This is a worked example based on an Italian invoice SaaS.

### Entities

`designer`, `sviluppatore`, `fotografo`, `consulente`, `artigiano`, `docente`.

### Modifiers

`forfettario`, `ordinario`. Potential future modifiers: `prestazione occasionale`, `società`.

### Raw matrix

`6 entities × 2 regimes × 1 locale = 12 candidate URLs`

### Eligibility

Not all 12 deserve a page. Apply the gates:

- A regime page exists only if the regime actually changes the invoice rules, rates, or calculator output for that entity.
- The page needs at least five unique facts: applicable regime rules, coefficient, tax rate, contribution rules, invoice fields, deadline, exemption threshold, calculation example.
- The page needs a unique calculator output and a worked example for that entity/regime combination.
- The entity hub page must target a different query from the entity × regime page, or it should not exist. Otherwise the two cannibalize each other.

A realistic first release might publish:

```text
/fattura/designer
/fattura/designer/forfettario
/fattura/sviluppatore
/fattura/sviluppatore/forfettario
/fattura/fotografo/forfettario
/fattura/consulente/forfettario
/fattura/artigiano/forfettario
/confronta/forfettario-vs-ordinario
```

The remaining combinations stay `eligible` or `candidate` until demand or data justifies them. The sitemap contains only the published subset.

### Why this is pSEO and not spam

Each page answers a different calculation or filing question with real rules, real thresholds, and a working example. The data model carries the rules; the template does not invent them. If the rules are identical across two entities, those two pages should be consolidated.

## 6. Data model

A practical schema has five layers.

### Page family

```text
id, slug, route_pattern, intent, template_version,
min_unique_facts, status, owner, created_at
```

### Source

```text
id, name, base_url, license, rights_note,
update_cadence, last_fetched_at, reliability
```

### Fact

```text
id, entity_id, key, value_json, source_id,
source_url, retrieved_at, confidence
```

### Page

```text
id, family_id, path, canonical_path, status,
indexable, http_status, title, meta_description,
primary_query, demand_score, data_score, quality_score,
unique_facts, content_hash, source_updated_at,
published_at, last_reviewed_at, lastmod, retired_at, redirect_to
```

### Indexing event

```text
id, page_id, url, provider, event_type,
idempotency_key, request_at, response_status,
response_body, attempts, next_retry_at, completed_at
```

The registry is authoritative. A route can read the registry, but it must not compute a different answer than the registry.

### Constraints worth enforcing in the database

- `path` is unique.
- `status = 'published'` implies `indexable = true`.
- `status = 'published'` implies `http_status = 200`.
- `status = 'published'` implies `canonical_path = path`.
- `status = 'retired'` implies `indexable = false`.
- `lastmod` is not earlier than `published_at`.
- `unique_facts >= 0`.
- A page cannot be its own redirect target.

## 7. Cannibalization

Cannibalization is two or more pages competing for the same query cluster with substantially the same answer. It is common in pSEO because families overlap.

Check:

- Same `primary_query` in the same family → likely duplicate.
- Entity hub and entity × modifier page with the same intent → consolidate or differentiate.
- Location page and "best in [region]" page with the same inventory → differentiate the job.
- Comparison page and alternatives page for the same pair → one should target the decision, the other the shortlist.

Resolution:

1. **Differentiate** the intent, data, and H1.
2. **Merge** into the stronger URL and `301` the weaker one.
3. **Canonicalize** a variant to the primary page if it must exist for users.
4. **Remove** the weaker page from the sitemap and internal links.

Do not "fix" cannibalization by adding more keywords to one of the pages.

## 8. International and localized pages

Only create a locale version when:

- The data is localized (currency, rules, availability, addresses), not just the labels.
- A human or a validated translation pipeline reviewed the copy.
- The URL is stable and the `hreflang` cluster is complete.
- The page can be maintained in that language.

Do not machine-translate 50,000 pages and call it international pSEO. That is a scaled-content risk.

`hreflang` rules:

- Each language version links to itself and every other version, including `x-default`.
- Use the canonical URL of each version, not a redirect.
- Do not point `hreflang` at a `noindex` page.
- Keep the cluster consistent across sitemaps and HTML.

## 9. Pilot design

A pilot is not a mini-launch of the whole matrix. It is an experiment with a decision at the end.

Pilot shape:

- 20–100 pages from one family.
- At least 10 pages in the "expected winner" segment and 10 in a control segment.
- A clear hypothesis: "These pages will earn impressions for the cluster and convert at X%."
- A baseline: current impressions, clicks, conversions for the cluster.
- A review date: 14, 30, and 90 days.
- A kill criterion: no impressions after 90 days, or no clicks after 180, or conversion below the threshold.
- A scale criterion: indexed share, impressions per page, CTR, conversion, and crawl behavior.

Do not scale a family because the first five pages were indexed. Indexation is not validation.

## 10. LLM-assisted copy

An LLM can help turn structured facts into readable sections. It cannot be the source of those facts.

Use it for:

- turning a fact table into a first draft
- summarizing a long regulation into a plain-language section, with the source attached
- generating variants for A/B testing, not for indexing
- drafting FAQs from real user questions

Do not use it for:

- inventing prices, availability, reviews, ratings, or author credentials
- generating pages for combinations that failed the eligibility gates
- translating 50,000 pages without local review
- writing legal, medical, or financial claims without a qualified reviewer

Pipeline:

```text
verified facts
    ↓
outline constrained to the facts
    ↓
draft with claim-level source references
    ↓
claim extraction and source check
    ↓
duplication check against siblings
    ↓
human review
    ↓
publish
```

Prompt requirements:

- Provide the facts as structured data, not as a vague brief.
- Require a citation for every number, rule, or comparison.
- Forbid claims that are not in the facts.
- Require the output schema: H1, answer, sections, table rows, FAQ, internal links.
- Require a "what I could not verify" section in the draft.
- Do not ask for "SEO keywords" in the body; write for the reader.

Quality checks:

- Every number matches a fact row and a source.
- No invented entity, author, review, or date.
- No near-duplicate paragraphs across siblings.
- The answer is self-contained in the first 40–60 words.
- A human with domain knowledge reviewed the page before publication.

Disclosure:

- If the page is substantially automated, consider a short, human-readable note on how it was produced.
- Do not use a fake author or a fake review date to make automated copy look human.
- Follow the project's editorial policy and any applicable disclosure rules.

Cost and operations:

- Cache generation per fact set; do not regenerate unchanged pages.
- Version the prompt and the model with the page's `template_version`.
- Store the generated draft and the fact snapshot used to produce it.
- Re-run the quality gates when the facts change, not only when the prompt changes.

## 11. Inventory columns

The inventory is the human-readable view of the registry. Keep it in version control for review, and generate it from the database when possible.

| Column | Meaning |
| --- | --- |
| `path` | Canonical path, starting with `/` |
| `status` | `candidate`, `eligible`, `published`, `suppressed`, `retired` |
| `indexable` | `true` only for published pages |
| `http_status` | Expected status: `200`, `301`, `404`, `410` |
| `canonical_path` | Self for published pages |
| `redirect_to` | Target for retired pages with a redirect |
| `page_family` | Family slug |
| `primary_query` | The main query cluster |
| `title` | Rendered title |
| `meta_description` | Rendered description |
| `unique_facts` | Count of unique facts with provenance |
| `content_hash` | Hash of normalized main content |
| `lastmod` | Last significant change, ISO date |
| `notes` | Review notes, risks, owners |

Run `scripts/pseo_lint.py` on this file before every deploy.
