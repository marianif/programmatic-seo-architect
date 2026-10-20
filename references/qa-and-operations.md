# QA, launch, and operations

A pSEO launch is a migration-sized change. Treat it like one: canary first, measure, then expand. This reference is the operational checklist.

## 1. Pre-launch checklist

### Data and eligibility

- [ ] Every published page has a page-family owner.
- [ ] Every published page has at least the minimum number of unique facts.
- [ ] Every fact has a source and a retrieval date.
- [ ] Data rights allow republication.
- [ ] No page is a template-only variation of a sibling.
- [ ] No duplicate `content_hash` among published pages.
- [ ] No unresolved cannibalization between siblings.
- [ ] `lastmod` reflects a real change.
- [ ] Stale pages are refreshed or removed from the freshness claim.

### Routes and rendering

- [ ] Every published path returns `200`.
- [ ] A random invalid path returns `404`.
- [ ] A retired path returns `410` or a single-hop `301`.
- [ ] The page is server-rendered with JavaScript disabled.
- [ ] The canonical is self-referencing and absolute.
- [ ] No redirect chains.
- [ ] No `noindex` on a published page.
- [ ] No `200` page with an empty template or "not found" body.
- [ ] Trailing-slash policy is consistent.

### Metadata and structured data

- [ ] Title and description are unique.
- [ ] No placeholders (`{`, `}`, `undefined`, `null`).
- [ ] One H1 per page.
- [ ] Open Graph image exists and is relevant.
- [ ] JSON-LD parses and matches visible content.
- [ ] No fake ratings, reviews, prices, or authors.
- [ ] Breadcrumb schema matches the visible breadcrumb.
- [ ] `hreflang` clusters are complete and self-referencing.

### Discovery

- [ ] Sitemap contains only published, canonical, `200` URLs.
- [ ] Sitemap is under 50,000 URLs and 50 MB per file.
- [ ] Sitemap index is submitted in Search Console.
- [ ] `robots.txt` references the sitemap.
- [ ] No published page is orphaned.
- [ ] Hub pages link to every published child.
- [ ] Pagination is crawlable.
- [ ] Facets are canonicalized or `noindex` as planned.

### Performance and UX

- [ ] LCP ≤ 2.5 s at p75.
- [ ] INP ≤ 200 ms at p75.
- [ ] CLS ≤ 0.1 at p75.
- [ ] The primary content works without JavaScript.
- [ ] The page is usable on a mid-range mobile device.
- [ ] No intrusive interstitial.
- [ ] Images have width/height and alt text.

### Analytics and legal

- [ ] Conversion events fire correctly.
- [ ] Consent mode is respected.
- [ ] The privacy policy covers the data shown.
- [ ] Regulated topics have a reviewer and disclaimer.
- [ ] No personal data is exposed in URLs or structured data.
- [ ] Terms of the data source are respected.

## 2. Canary launch

Do not publish the full matrix on day one.

| Phase | Pages | Duration | Decision |
| --- | --- | --- | --- |
| Canary | 20–50 | 14 days | Crawl, index, errors, early impressions |
| Cohort 1 | 100–300 | 30 days | Indexed share, impressions per page, CTR |
| Scale | 1,000+ | 60–90 days | Conversion, crawl budget, duplication, pruning |

At each phase, compare against the baseline and the control group.

**Do not scale because pages are indexed.** Indexation is a necessary condition, not proof of value. Scale when the cohort shows impressions, clicks, and a plausible path to conversion.

## 3. Acceptance tests

### HTTP and canonical

```bash
# Published page
curl -sSI https://example.com/fattura/designer/forfettario | head -20

# Invalid page
curl -sSI https://example.com/fattura/not-a-real-entity | head -5

# Canonical in the HTML
curl -s https://example.com/fattura/designer/forfettario \
  | grep -o '<link rel="canonical"[^>]*>'

# Robots meta
curl -s https://example.com/fattura/designer/forfettario \
  | grep -o '<meta name="robots"[^>]*>'
```

Expected:

- published: `HTTP/2 200`, canonical self, no `noindex`
- invalid: `HTTP/2 404`
- retired: `HTTP/2 410` or `301` to a `200`
- no `x-robots-tag: noindex` on published pages

### Sitemap

```bash
curl -s https://example.com/sitemap.xml | head -40
curl -s https://example.com/sitemaps/pseo-1.xml | grep -c '<url>'
```

Check:

- only canonical URLs
- no `noindex` or redirect URLs
- `lastmod` is not in the future
- the count matches the registry
- the index references every chunk

### Structured data

```bash
curl -s https://example.com/fattura/designer/forfettario -o page.html
python3 - <<'PY'
import re
from pathlib import Path

html = Path("page.html").read_text(encoding="utf-8")
blocks = re.findall(
    r'<script type="application/ld\+json">(.*?)</script>',
    html,
    re.S,
)
print("\n\n".join(blocks))
PY
```

Then paste the JSON-LD into the Schema Markup Validator. Check that:

- JSON parses
- `@id` values are unique
- the `WebPage.url` matches the canonical
- breadcrumbs match the visible breadcrumb
- no fake ratings or reviews

### Inventory lint

```bash
python3 scripts/pseo_lint.py examples/invoice-saas/page-inventory.csv
```

Expected: exit `0`, no errors. Use `--json` in CI.

### Rendered page audit

For a sample of 10–20 URLs per family:

- fetch with JavaScript disabled
- confirm H1, answer, data table, and internal links are in the HTML
- confirm the page is not a soft 404
- confirm the title and description are unique
- confirm the page is linked from a hub
- record response time and HTML size

## 4. CI integration

Add these checks to the pipeline:

```yaml
# example: GitHub Actions
- name: Validate pSEO inventory
  run: python3 scripts/pseo_lint.py examples/invoice-saas/page-inventory.csv

- name: Check sitemap eligibility
  run: python3 scripts/check_sitemap.py # optional project script

- name: Test invalid route
  run: |
    status=$(curl -s -o /dev/null -w "%{http_code}" "$PREVIEW_URL/fattura/not-a-real-entity")
    test "$status" = "404"
```

Minimum CI gates:

1. Inventory lint passes.
2. Invalid slug returns `404`.
3. Published slug returns `200`.
4. Canonical is self.
5. Sitemap contains no unpublished URLs.
6. JSON-LD parses.
7. No duplicate titles or content hashes.

## 5. Launch sequence

1. Freeze the data snapshot.
2. Run the inventory lint.
3. Deploy to a preview URL.
4. Run the acceptance tests on the preview.
5. Crawl the preview with a small crawler; check status codes and canonicals.
6. Publish the canary pages.
7. Submit the sitemap index.
8. Notify IndexNow for the canary URLs.
9. Monitor 404s, 5xx, crawl requests, and indexing for 48 hours.
10. Review at 14 days; decide whether to expand.

Do not submit every URL to every provider on day one. The canary is also a test of the indexing pipeline.

## 6. Rollback plan

A pSEO launch can fail in several ways. Have a rollback for each.

| Failure | Rollback |
| --- | --- |
| Bad template deployed | Revert the deploy; purge the cache |
| Wrong data in pages | Restore the previous snapshot; purge affected tags |
| Index bloat | Remove from sitemap, `noindex`, fix internal links, then `410` if permanent |
| Manual action | Stop publishing, audit the family, fix, request reconsideration |
| 5xx under crawler load | Scale origin, add cache, reduce crawl rate if necessary |
| Duplicate canonical | Fix the canonical, purge, resubmit the sitemap |
| Bad redirect map | Revert the redirects; test one hop per URL |

Before launch:

- back up the registry
- back up the redirect map
- know how to purge the CDN by tag
- know how to disable the indexing worker
- know who can approve an emergency rollback

## 7. Incident playbook

### Traffic drop after launch

1. Check for a manual action and security issues.
2. Check `robots.txt`, `noindex`, and canonical changes.
3. Check 5xx and response time.
4. Check whether the sitemap was replaced or emptied.
5. Compare the crawl rate and indexed count.
6. Check whether a deploy changed the template or metadata.
7. If the drop is site-wide, roll back the deploy first, then diagnose.

### Index bloat

1. Identify the URL patterns.
2. Remove them from sitemaps.
3. Fix internal links.
4. `noindex` if they must remain accessible.
5. `410` if they are permanently gone.
6. Confirm the count in Search Console over 2–4 weeks.

### Soft 404s

1. Find `200` pages with "not found" or empty content.
2. Return a real `404`/`410`.
3. Remove them from sitemaps and internal links.
4. Add a regression test.

### Duplicate clusters

1. Group by `content_hash` and near-duplicate score.
2. Keep the strongest URL.
3. Merge unique facts into the survivor.
4. `301` the others.
5. Update internal links and the sitemap.

### Stale data

1. Identify pages whose source changed.
2. Refresh facts and `lastmod`.
3. If the source is unavailable, remove the freshness claim or suppress the page.
4. Do not leave a "last updated today" label on unchanged data.

### Indexing provider failure

1. Check the provider status and response code.
2. Retry `429` and `5xx` with backoff.
3. Do not retry `400`, `403`, or `422` without a fix.
4. Send failed events to a dead-letter queue.
5. Alert the owner.
6. Sitemaps and internal links remain the fallback; a failed ping is not a publishing failure.

## 8. Monitoring cadence

| Frequency | Check |
| --- | --- |
| Daily | 5xx rate, indexing worker failures, deploy changes |
| Weekly | crawl requests, sitemap status, new 404s, indexing progress |
| Monthly | impressions/clicks by family, indexed share, CWV, duplication |
| Quarterly | pruning review, data freshness, family ROI, policy audit |

Keep a decision log:

```text
date | page/family | action | reason | owner | expected outcome | review date
```

## 9. Ownership

At minimum:

- **Data owner** — source accuracy, rights, refresh cadence.
- **Engineering owner** — routes, caching, indexing worker, uptime.
- **SEO owner** — page families, demand, cannibalization, measurement.
- **Editorial/reviewer** — copy, claims, regulated topics.
- **Business owner** — conversion, prioritization, kill decisions.

A pSEO system without an owner for data freshness becomes stale within a quarter.

## 10. Spam-policy audit

Before scaling, audit the family against Google's spam policies:

- **Scaled content abuse:** many pages generated without added value.
- **Doorway abuse:** pages that funnel users to another page without being useful themselves.
- **Thin affiliation:** product pages with copied descriptions and no original value.
- **Site reputation abuse:** third-party content hosted mainly for the host's ranking signals.
- **Keyword stuffing:** lists of cities or terms without substance.
- **Cloaking:** different content for crawlers and users.

If a family depends on one of these patterns, stop and redesign it. Do not scale first and audit later.

## 11. Post-launch review template

```markdown
# pSEO review — [family] — [date]

## Published
- pages:
- families:
- locales:

## Indexed
- indexed:
- not indexed:
- top reasons:

## Performance
- impressions:
- clicks:
- CTR:
- average position:
- conversions:

## Quality
- duplicate clusters:
- stale pages:
- cannibalization:
- CWV:

## Decisions
- keep:
- improve:
- consolidate:
- redirect:
- remove:

## Next review
- date:
- owner:
```
