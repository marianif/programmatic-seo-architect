# Indexing, discovery, and measurement

Indexing is not publishing. A page is published when it returns `200`; it is indexed when a search engine chooses to crawl, parse, and include it. Your job is to make discovery easy, the page worth indexing, and the outcome measurable.

## 1. Discovery hierarchy

Use the strongest signal first:

1. **Internal links.** A real `<a href>` from a hub, category, or sibling page.
2. **XML sitemaps.** A complete, canonical list of published pages.
3. **IndexNow.** Push notifications to Bing, Yandex, Seznam, Naver, and other participants.
4. **Search Console.** Sitemap submission, URL Inspection for diagnostics, manual indexing requests for a few important URLs.
5. **Google Indexing API.** Only for `JobPosting` and `BroadcastEvent` pages. Never for general pSEO.
6. **Links from other sites.** Earned, not bought.

No amount of pinging fixes a page that is not linked, not useful, or not unique.

## 2. Sitemaps

### What belongs in a sitemap

Only URLs that:

- return `200`
- are indexable (`index,follow`, no `noindex`)
- are canonical (`canonical_path = path`)
- are published
- have a real `lastmod`

Do not include:

- redirects (`301`, `302`)
- `404` or `410`
- `noindex` pages
- canonicalized duplicates
- draft or `eligible` pages
- paginated duplicates if page 2+ is `noindex`
- URLs blocked by `robots.txt`

### Limits

- 50,000 URLs per sitemap
- 50 MB uncompressed per sitemap
- UTF-8 encoding
- absolute URLs
- one URL per `<url>` entry

If you exceed either limit, create a sitemap index:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemaps/pseo-1.xml</loc>
    <lastmod>2026-10-21</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemaps/pseo-2.xml</loc>
    <lastmod>2026-10-21</lastmod>
  </sitemap>
</sitemapindex>
```

Submit the index, not every chunk, in Search Console. Reference it in `robots.txt`:

```text
Sitemap: https://example.com/sitemap.xml
```

### `lastmod`

Google uses `<lastmod>` when it is consistently and verifiably accurate. Set it to the date of the last significant change:

- main content
- structured data
- internal links
- price or availability
- canonical or redirect

Do not update it for a copyright year, a deploy, or a CSS change. A sitemap full of false `lastmod` values teaches the crawler to ignore the field.

### Sitemap generation query

```sql
select
  path,
  lastmod
from pseo_pages
where status = 'published'
  and indexable = true
  and http_status = 200
  and canonical_path = path
  and path not like '/admin/%'
order by path;
```

The route should not generate a sitemap from the full route space. If a page is not in the registry as published, it is not in the sitemap.

## 3. IndexNow

IndexNow is an open protocol supported by Bing, Yandex, Seznam, Naver, Yep, and other participants. One submission is shared with all participating engines.

### Key file

Host a UTF-8 text file at the root:

```text
https://example.com/<key>.txt
```

The file contains the key. The key must be 8–128 characters from `a–z`, `A–Z`, `0–9`, and dashes. Alternatively, use `keyLocation` to point to a key file in a subdirectory, but root is simpler and recommended.

### Single URL

```text
https://api.indexnow.org/indexnow?url=https%3A%2F%2Fexample.com%2Fpage&key=<key>
```

### Batch

```ts
async function submitIndexNow(urls: string[]) {
  const key = process.env.INDEXNOW_KEY
  if (!key) throw new Error('INDEXNOW_KEY is not set')

  const res = await fetch('https://api.indexnow.org/indexnow', {
    method: 'POST',
    headers: { 'content-type': 'application/json; charset=utf-8' },
    body: JSON.stringify({
      host: 'example.com',
      key,
      keyLocation: `https://example.com/${key}.txt`,
      urlList: urls,
    }),
  })

  if (!res.ok) {
    throw new Error(`IndexNow failed: ${res.status} ${await res.text()}`)
  }
}
```

Rules:

- Up to 10,000 URLs per POST.
- Submit only new, updated, or deleted URLs.
- Do not submit the same unchanged URL repeatedly.
- Handle `200`, `202`, `400`, `403`, `422`, and `429`.
- Back off on `429`; do not retry in a tight loop.
- Log the response and the URL list for audit.

IndexNow does not cover Google. Google does not participate.

## 4. Google Indexing API

The Google Indexing API is officially limited to pages with:

- `JobPosting` structured data
- `BroadcastEvent` embedded in a `VideoObject`

It is **not** a general-purpose indexing API. Using it for other page types does not make Google index them and may violate the API's terms. All submissions undergo spam detection, and abuse can revoke access.

Use it only when the page is genuinely one of those two types:

```ts
import { google } from 'googleapis'

export async function notifyJobPosting(
  url: string,
  type: 'URL_UPDATED' | 'URL_DELETED' = 'URL_UPDATED',
) {
  const auth = new google.auth.JWT({
    email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
    key: process.env.GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY?.replace(/\\n/g, '\n'),
    scopes: ['https://www.googleapis.com/auth/indexing'],
  })

  const indexing = google.indexing({ version: 'v3', auth })
  const response = await indexing.urlNotifications.publish({
    requestBody: { url, type },
  })

  return response.data
}
```

For general pSEO pages, the correct Google actions are:

- internal links
- XML sitemaps
- Search Console sitemap submission
- Search Console URL Inspection for diagnostics
- patience

## 5. Search Console

Use the Search Console API for:

- sitemap submission and status
- URL Inspection (index status, canonical, crawl, rich results)
- search analytics (queries, pages, countries, devices)
- crawl stats (if available for the property)

Do not use the URL Inspection API as a bulk submission tool. It has quotas and is designed for diagnostics.

A practical monthly check:

1. Sitemaps: submitted, last read, errors, discovered URLs.
2. Pages: indexed vs not indexed, reasons.
3. Performance: impressions, clicks, CTR, position by page family.
4. Crawl: requests, response codes, file types.
5. Manual actions and security issues.

## 6. Indexing event pipeline

Do not call providers inline in the publish request. A slow or failed provider should not block publishing, and a retry should not create duplicate events.

```text
publish/update/delete
        ↓
transactional outbox (same DB transaction)
        ↓
queue / worker
        ↓
provider adapter (sitemap ping, IndexNow, Google API)
        ↓
response log + retry policy
        ↓
dead letter + alert
```

### Event table

```sql
create table pseo_indexing_events (
  id uuid primary key default gen_random_uuid(),
  page_id uuid not null references pseo_pages(id),
  url text not null,
  provider text not null,
  event_type text not null check (event_type in ('created', 'updated', 'deleted')),
  idempotency_key text not null,
  status text not null default 'pending'
    check (status in ('pending', 'sent', 'failed', 'dead')),
  attempts int not null default 0,
  response_status int,
  response_body text,
  next_retry_at timestamptz,
  created_at timestamptz not null default now(),
  completed_at timestamptz,
  unique (provider, idempotency_key)
);
```

Idempotency key:

```text
sha256(url + event_type + content_hash + provider)
```

Retry policy:

- exponential backoff with jitter
- max 5–8 attempts
- dead-letter after the max
- alert on dead-letter count
- never retry `400`, `403`, or `422` without a fix

### What triggers an event

- page status changes to `published`
- page content hash changes materially
- canonical changes
- page is retired or redirected
- price/availability changes beyond a threshold

Do not trigger on:

- deploy with no content change
- template CSS change
- navigation change
- `lastmod` refresh only

## 7. Quotas and rate limits

Quotas change. Check the provider's current documentation before hardcoding limits.

General rules:

- Batch where the provider supports it.
- Respect `429` and `Retry-After`.
- Keep a daily cap per provider.
- Separate interactive (single URL) from bulk (sitemap/IndexNow) paths.
- Monitor error rate, not only success count.
- Do not create multiple accounts to bypass quotas.

## 8. Measurement

### Baseline before launch

Record:

- indexed pages by family
- impressions, clicks, CTR, average position
- crawl requests and response codes
- conversions or leads
- page count and publish dates

### Cohorts

Measure by:

- page family
- publish month
- data quality tier
- template version
- locale

A blended site-wide number hides the fact that one family works and another does not.

### Leading and lagging indicators

| Stage | Indicator | What it tells you |
| --- | --- | --- |
| Discovery | crawl requests, sitemap discovered URLs | Are crawlers finding the pages? |
| Indexing | indexed share, "Crawled – currently not indexed" | Are pages worth indexing? |
| Appearance | impressions, average position | Are pages eligible and relevant? |
| Clicks | CTR, clicks | Is the snippet compelling? |
| Business | conversions, leads, revenue | Is the page worth maintaining? |
| Health | CWV, errors, duplicate clusters | Is the system sustainable? |

### Indexing math

Do not expect 100% indexation. A realistic target for a healthy pSEO family is:

- 70–90% of published pages indexed within 4–8 weeks
- the remainder either lower-demand long tail or pages Google chooses not to index

If indexation is below 50% after 8 weeks, investigate:

- thin or duplicate content
- crawl budget
- internal linking
- canonical errors
- sitemap errors
- server errors or slow responses
- robots/noindex mistakes

## 9. Crawl budget

Crawl budget matters when:

- the site has tens of thousands of URLs
- many URLs are low-value or duplicate
- the server is slow
- the site changes frequently

Reduce waste:

- remove `noindex` URLs from sitemaps
- fix soft 404s
- canonicalize parameter variants
- block infinite filter combinations with `robots.txt` or `noindex`
- keep response times low
- avoid redirect chains
- link only to published pages

Do not use `robots.txt` to hide pages you want indexed. `robots.txt` blocks crawling, not indexing; a blocked URL can still be indexed if linked.

## 10. Pruning

Pruning is a first-class pSEO operation.

Review every cohort at 30, 60, and 90 days.

| Signal | Action |
| --- | --- |
| No impressions after 90 days | Improve the page, consolidate it, or retire it |
| Impressions but no clicks after 180 days | Rewrite the title/description or fix intent |
| Cannibalization | Merge, differentiate, or canonicalize |
| Stale data | Refresh or remove the freshness claim |
| Duplicate cluster | Keep the strongest URL; `301` the rest |
| Crawl waste | Remove from sitemap and internal links; `410` if permanent |
| Manual action | Stop publishing, audit the family, fix, request reconsideration |

Order of preference:

1. Improve the page.
2. Consolidate into a stronger page.
3. `301` to the stronger page.
4. `410` if the page is permanently gone.
5. `noindex` only if the page must exist for users.

After any pruning action:

- update the registry
- remove the URL from sitemaps
- remove internal links
- invalidate the cache
- log the decision and the reason

## 11. Monitoring dashboard

Minimum metrics:

- published pages, indexable pages, sitemap URLs
- indexed pages (Search Console)
- crawl requests by status code
- impressions, clicks, CTR by family
- conversions by family
- pages with zero impressions (90+ days)
- duplicate content clusters
- indexing event failures
- p75 LCP, INP, CLS
- 5xx rate and origin latency

Alert on:

- sitemap fetch failure
- sudden drop in indexed pages
- spike in 5xx
- manual action
- indexing provider error rate
- a family with zero impressions after 30 days

## 12. Reporting

A useful pSEO report answers:

1. What did we publish this period?
2. What got indexed?
3. What earned impressions and clicks?
4. What converted?
5. What is stale, duplicate, or wasteful?
6. What will we publish, improve, or prune next?

Do not report page count as the headline. Report **useful indexed pages** and **business outcomes**.
