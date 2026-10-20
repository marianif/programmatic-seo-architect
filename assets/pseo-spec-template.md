# pSEO specification — [project]

> Fill this in before writing routes or templates. Keep it in the repository and update it when the matrix, gates, or URL rules change.

## 1. Decision summary

- **Project:**
- **Owner:**
- **Date:**
- **Status:** draft / approved / in build / live / paused
- **Primary page family:**
- **Pilot size:**
- **Target launch:**
- **Decision this pilot must inform:**

## 2. Business and audience

- **What the business sells:**
- **Valuable action:** signup / lead / purchase / booking / download / application
- **Audience and job-to-be-done:**
- **Markets and languages:**
- **Current organic baseline:**
- **Main competitors in the SERP:**
- **Why this project should win:**

## 3. Page families

| Family | Route pattern | Intent | Data required | Owner | Status |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

For each family, answer:

- What query cluster does it serve?
- What unique data does it have?
- What decision or task does it support?
- What would make it thin?
- What is the maintenance cadence?

## 4. Demand evidence

| Cluster | Evidence type | Source | Metric | Date | Confidence |
| --- | --- | --- | --- | --- | --- |
|  | measured / estimated / observed / hypothesis |  |  |  |  |

Rules:

- Do not present an estimate as measured.
- Do not invent a volume.
- If demand is only a hypothesis, say so and define the pilot's learning goal.

## 5. Data sources and rights

| Source | What it provides | URL / system | License / rights | Update cadence | Owner |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

- **Can we republish the data?**
- **Personal data involved?**
- **Attribution required?**
- **What happens if the source is unavailable?**

## 6. Matrix and eligibility

### Dimensions

| Dimension | Values | Count |
| --- | --- | --- |
| Entities |  |  |
| Modifiers |  |  |
| Locales |  |  |
| Raw candidates |  |  |

### Gates

| Gate | Rule | Evidence |
| --- | --- | --- |
| Demand |  |  |
| Data | Minimum unique facts:  |  |
| Differentiation |  |  |
| Utility |  |  |
| Trust |  |  |
| Technical |  |  |
| Economics |  |  |
| Risk |  |  |

### Expected output

- **Eligible pages:**
- **Published in pilot:**
- **Excluded combinations and why:**

## 7. Page registry and statuses

- **Registry location:**
- **Statuses:** candidate / eligible / published / suppressed / retired
- **Who can change status:**
- **What triggers `lastmod`:**
- **What triggers an indexing event:**

## 8. URL architecture

- **Pattern:**
- **Locale pattern:**
- **Trailing slash:**
- **Canonical rule:**
- **Redirect rule:**
- **Reserved slugs:**
- **Pagination:**
- **Facets:**
- **Legacy URLs to migrate:**

## 9. Template anatomy

| Section | Purpose | Data source | Unique? |
| --- | --- | --- | --- |
| H1 |  |  |  |
| Answer / summary |  |  |  |
| Data table |  |  |  |
| Main sections |  |  |  |
| Calculator / tool |  |  |  |
| FAQ |  |  |  |
| Related links |  |  |  |
| CTA |  |  |  |

- **What is above the fold?**
- **What is the primary action?**
- **What content must be server-rendered?**

## 10. Metadata and structured data

- **Title formula:**
- **Description formula:**
- **H1 formula:**
- **OG image:**
- **Primary schema type:**
- **Supporting schema:**
- **Author / reviewer:**
- **Dates:**
- **What must not be marked up:**

## 11. Rendering and caching

- **Framework and version:**
- **Rendering mode:**
- **Prerender set:**
- **On-demand behavior:**
- **Cache headers:**
- **Cache tags:**
- **Invalidation triggers:**
- **Hosting / CDN:**

## 12. Internal linking

- **Hub pages:**
- **Child → parent links:**
- **Sibling links:**
- **Related links:**
- **Maximum links per page:**
- **Orphan check:**

## 13. Sitemaps and indexing

- **Sitemap generator:**
- **Sitemap index:**
- **Chunk size:**
- **Search Console property:**
- **IndexNow:**
- **Google Indexing API:** only `JobPosting` / `BroadcastEvent`; otherwise N/A
- **Indexing worker:**
- **Retry policy:**
- **Alert channel:**

## 14. QA gates

| Gate | Pass condition | Owner | Evidence |
| --- | --- | --- | --- |
| Inventory lint |  |  |  |
| Route status |  |  |  |
| Canonical |  |  |  |
| Metadata |  |  |  |
| Schema |  |  |  |
| Sitemap |  |  |  |
| Links |  |  |  |
| Performance |  |  |  |
| Analytics |  |  |  |

## 15. Measurement and pruning

- **Baseline metrics:**
- **Cohort definition:**
- **Review dates:** 14 / 30 / 90 days
- **Scale criteria:**
- **Kill criteria:**
- **Pruning actions:**
- **Owner:**

## 16. Risks and open questions

| Risk | Likelihood | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

Open questions:

1.
2.
3.

## 17. Pilot plan

| Step | Owner | Date | Output |
| --- | --- | --- | --- |
| Data snapshot |  |  |  |
| Registry seed |  |  |  |
| Template build |  |  |  |
| QA |  |  |  |
| Canary publish |  |  |  |
| 14-day review |  |  |  |
| Scale / stop decision |  |  |  |

## 18. Approval

- **SEO:**
- **Engineering:**
- **Data owner:**
- **Legal / compliance (if needed):**
- **Business owner:**
