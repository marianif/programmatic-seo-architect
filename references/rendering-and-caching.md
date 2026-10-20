# Rendering, caching, and routing

Read this when the page model is settled and you need the page to be fast, correct, and crawlable.

## 1. Choose the rendering mode

| Page behavior | Recommended mode | Cache | Notes |
| --- | --- | --- | --- |
| Stable data, updated weekly or monthly | SSG / prerender | CDN, long TTL | Build only if build time is predictable |
| Large long tail, acceptable hours of staleness | ISR / on-demand rendering | CDN + origin cache | Prerender the popular subset |
| Prices, inventory, availability | SSR + short cache | `s-maxage=60–600` | Purge on data change |
| User-specific | SSR / client | `private, no-store` | Never share cache entries |
| Real-time collaborative | client + API | no page cache | Not a pSEO page |
| Legal/regulated data | SSR or ISR + short cache | short TTL | Freshness is part of correctness |

Do not use client-side rendering for the primary content. Google can render JavaScript, but it adds latency and risk, and other crawlers and answer engines are less predictable. The H1, the answer, the data table, and the internal links should be in the initial HTML.

## 2. The route contract

Every pSEO route follows the same sequence:

```text
1. Resolve and validate params.
2. Load the page from the registry by path.
3. If status != published -> 404 (or 410 if retired).
4. If canonical_path != path -> 301 to the canonical.
5. Fetch facts and copy.
6. Render HTML + metadata + JSON-LD.
7. Set cache headers and cache tags.
```

Validate **before** rendering the template. Never render a page with empty fields and hope the registry catches it later.

### Status codes

| Situation | Status | Notes |
| --- | --- | --- |
| Published page | `200` | Self-canonical |
| Unknown combination | `404` | No soft 404 |
| Permanently removed page | `410` | Preferred over 404 when the removal is intentional |
| Permanent URL change | `301` | One hop to the final URL |
| Temporary move | `302` or `307` | Do not use for a permanent migration |
| Page exists but is suppressed | `200` + `noindex` | Only when users need it; not in sitemaps |
| Canonical variant | `301` to canonical | Or `200` + canonical + `noindex` if it must be reachable |

Never return `200` with a "not found" message. That is a soft 404 and wastes crawl budget.

## 3. Next.js App Router

### Version check

Run:

```bash
node -p "require('next/package.json').version"
```

Then check whether `cacheComponents` is enabled in `next.config.*`.

### Next.js 16 with Cache Components

Route segment config `revalidate`, `dynamic`, `dynamicParams`, and `fetchCache` are removed when Cache Components is enabled. Use the cache primitives:

```tsx
// lib/pseo.ts
import { cacheLife, cacheTag } from 'next/cache'
import { db } from './db'

export async function getPublishedPage(family: string, entity: string) {
  'use cache'
  cacheLife('days')
  cacheTag(`pseo:${family}`, `pseo:page:${family}:${entity}`)

  return db.pseoPage.findFirst({
    where: {
      path: `/${family}/${entity}`,
      status: 'published',
      indexable: true,
    },
  })
}
```

```tsx
// app/[family]/[entity]/page.tsx
import { notFound } from 'next/navigation'
import { getPublishedPage, getTopPages } from '@/lib/pseo'
import { PseoPage } from '@/components/pseo-page'

type Params = { family: string; entity: string }

export async function generateStaticParams() {
  const top = await getTopPages({ limit: 500 })
  return top.map((p) => ({ family: p.family, entity: p.entity }))
}

export async function generateMetadata({
  params,
}: {
  params: Promise<Params>
}) {
  const { family, entity } = await params
  const page = await getPublishedPage(family, entity)
  if (!page) return {}
  return {
    title: page.title,
    description: page.description,
    alternates: {
      canonical: new URL(page.canonicalPath, process.env.SITE_URL).toString(),
    },
    robots: { index: true, follow: true },
  }
}

export default async function Page({ params }: { params: Promise<Params> }) {
  const { family, entity } = await params
  const page = await getPublishedPage(family, entity)
  if (!page) notFound()
  return <PseoPage page={page} />
}
```

Notes:

- `generateStaticParams` must return at least one param when Cache Components is enabled. Prerender only the top pages; unknown params are served as an App Shell and upgraded in the background.
- `notFound()` in the page produces the 404 status. Do not render a custom "not found" component with 200.
- Tag cached data with `cacheTag()`; on every write path that can change the page, call `revalidateTag()` after the mutation.
- With Partial Prefetching, links to long-tail pages should use `prefetch={true}` if you want the destination upgraded before the click.

### Next.js 15 or no Cache Components

```tsx
export const revalidate = 86400
export const dynamicParams = true
```

Data fetch:

```tsx
const res = await fetch(url, {
  next: {
    revalidate: 86400,
    tags: [`pseo:${family}`],
  },
})
```

On-demand revalidation:

```ts
import { revalidateTag } from 'next/cache'

await revalidateTag(`pseo:${family}`)
```

Do not mix `export const revalidate` with `'use cache'` in the same route and expect one model to win. Pick the project's model and follow it.

### Proxy / middleware

Next.js 16 renamed `middleware.ts` to `proxy.ts`. The `proxy` function runs before routes render, on the Node.js runtime by default. The `runtime` route segment config is not available in proxy files.

Use proxy for:

- legacy URL redirects
- locale negotiation
- security headers
- blocking obviously invalid path shapes

Do not use proxy for:

- fetching page data
- rendering content
- bot-specific content (cloaking risk)
- large redirect maps that belong in the router or the database

```ts
// proxy.ts
import { NextResponse, type NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  if (pathname.startsWith('/old-invoice-templates/')) {
    const slug = pathname.slice('/old-invoice-templates/'.length)
    return NextResponse.redirect(
      new URL(`/fattura/${encodeURIComponent(slug)}/forfettario`, request.url),
      301,
    )
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/old-invoice-templates/:path*'],
}
```

Keep the matcher narrow. A proxy that runs on every asset request adds latency and can break caching.

### Next.js sitemap

```ts
// app/sitemap.ts
import type { MetadataRoute } from 'next'
import { getSitemapPages } from '@/lib/pseo'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const pages = await getSitemapPages()
  return pages.map((page) => ({
    url: `${process.env.SITE_URL}${page.path}`,
    lastModified: page.lastmod,
  }))
}
```

For more than 50,000 URLs, use `generateSitemaps()` and return one sitemap per chunk. Do not add `changeFrequency` or `priority` unless the project already uses them; Google ignores both.

## 4. Nuxt 4

Nuxt supports hybrid rendering with `routeRules`.

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  routeRules: {
    '/': { prerender: true },
    '/fattura/**': {
      isr: 86400, // CDN-backed on Netlify/Vercel
      headers: {
        'cache-control': 'public, s-maxage=86400, stale-while-revalidate=604800',
      },
    },
    '/admin/**': { ssr: false },
  },
})
```

- `prerender: true` for the popular subset.
- `isr` for CDN-backed incremental regeneration; `swr` for a Node server with stale-while-revalidate.
- `ssr: false` only for app-like pages that do not need indexing.
- Use `createError({ statusCode: 404, statusMessage: 'Not found' })` in `asyncData` or the page setup when the registry has no published page.

```vue
<script setup lang="ts">
const route = useRoute()
const { data: page } = await useAsyncData(
  `pseo:${route.path}`,
  () =>
    $fetch('/api/pseo/page', { query: { path: route.path } }).catch(
      () => null,
    ),
)

if (!page.value) {
  throw createError({ statusCode: 404, statusMessage: 'Not found' })
}
</script>
```

For a large site, generate the prerender list in a build step and import it:

```ts
// nuxt.config.ts
import topRoutes from './pseo-routes.json'

export default defineNuxtConfig({
  nitro: {
    prerender: {
      routes: topRoutes,
    },
  },
})
```

Do not import a database client into `nuxt.config.ts` if the build environment cannot reach it. Export a JSON list from the build pipeline instead.

## 5. Astro

Astro is static by default. For a long tail:

```astro
---
// src/pages/[family]/[entity].astro
import { getPublishedPage } from '@/lib/pseo'

export const prerender = false

const page = await getPublishedPage(Astro.params.family, Astro.params.entity)
if (!page) {
  return new Response(null, { status: 404, statusText: 'Not found' })
}

Astro.response.headers.set(
  'Cache-Control',
  'public, s-maxage=86400, stale-while-revalidate=604800',
)
---
<h1>{page.h1}</h1>
```

- Use an SSR adapter for `prerender = false`.
- Prerender the top pages by returning `getStaticPaths()` from the registry.
- Astro has no built-in ISR; use the host's CDN cache or a background revalidation job.

## 6. SvelteKit

```ts
// src/routes/[family]/[entity]/+page.server.ts
import { error } from '@sveltejs/kit'
import { getPublishedPage } from '$lib/pseo'

export async function load({ params, setHeaders }) {
  const page = await getPublishedPage(params.family, params.entity)
  if (!page) throw error(404, 'Not found')

  setHeaders({
    'cache-control': 'public, s-maxage=86400, stale-while-revalidate=604800',
  })

  return { page }
}
```

- `export const prerender = true` for the popular subset.
- Use an adapter and the host's cache for the long tail.
- SvelteKit has no built-in ISR; schedule revalidation or rely on short CDN TTLs.

## 7. Cache headers

A practical default for stable pSEO pages:

```http
Cache-Control: public, s-maxage=86400, stale-while-revalidate=604800
```

For fresher data:

```http
Cache-Control: public, s-maxage=600, stale-while-revalidate=3600
```

For 404s, cache briefly to protect the origin:

```http
Cache-Control: public, s-maxage=60, stale-while-revalidate=300
```

For personalized pages:

```http
Cache-Control: private, no-store
```

Rules:

- `s-maxage` applies to shared caches; `max-age` applies to browsers.
- `stale-while-revalidate` lets the CDN serve a stale copy while it refreshes. It is not a substitute for correct data.
- `Vary` on `Accept-Encoding` is normal. Do not `Vary: User-Agent` to serve different content to crawlers; that is cloaking.
- Do not cache responses that set cookies or contain user-specific data.
- Purge by cache tag or surrogate key on publish, update, unpublish, and redirect changes.
- If the CDN supports it, use `CDN-Cache-Control` for CDN-specific TTLs and `Cache-Control` for browsers.

## 8. Build strategy

Build time grows with the number of pages and the cost of data fetching. Do not prerender 100,000 pages because you can.

Recommended split:

| Segment | Build strategy |
| --- | --- |
| Top 100–1,000 by demand | Prerender at build |
| Next 10,000 | On-demand ISR / SSR + cache |
| Long tail | On-demand only; no build cost until visited |
| Removed pages | `410` or `301`; remove from sitemap |

Measure:

- build minutes per 1,000 pages
- average data-fetch time per page
- cache hit rate
- origin requests per 1,000 visits
- p75 LCP and INP

If build time exceeds the deploy budget, reduce the prerender set, not the quality gates.

## 9. Invalidation

Invalidate on meaningful events:

- page published
- page unpublished or retired
- fact changed (price, rule, availability)
- template changed
- canonical or redirect changed

Use cache tags:

```text
pseo:family:{family}
pseo:page:{family}:{entity}
pseo:entity:{entity_id}
```

On a fact update, invalidate the affected pages, not the whole site. On a template deploy, invalidate the family or the whole pSEO namespace.

Do not invalidate on every deploy if the content did not change. It destroys the cache hit rate and makes crawl behavior unstable.

## 10. International routing

Choose one pattern and keep it:

```text
/{locale}/{family}/{entity}
```

Avoid `?lang={locale}` for indexable content: it creates parameter variants and canonical ambiguity. The path pattern is better for crawling and sharing. Requirements:

- `hreflang` on every version, including `x-default`.
- Self-canonical for each locale.
- Localized metadata, not just translated labels.
- A locale switcher that links to the equivalent page, not the home page.
- A sitemap with `alternates.languages` for each URL.
- No automatic redirect based on IP that hides the canonical version from crawlers.

## 11. Security and correctness

- Validate slugs against a strict allowlist before using them in a query or a file path.
- Parameterize database queries; never interpolate a slug into SQL.
- Escape JSON-LD before injecting it into a `<script>` tag:

```ts
const json = JSON.stringify(data).replace(/</g, '\\u003c')
```

- Do not expose internal IDs, draft pages, or admin routes in the sitemap.
- Rate-limit any public endpoint that triggers indexing or revalidation.
- Keep service-account keys and IndexNow keys in environment variables.
- Log indexing provider responses with the URL and event type, but do not log secrets.
- Add a regression test for `404` on an invalid slug and `200` on a published slug.

## 12. Performance checklist

- LCP image is optimized, sized, and not lazy-loaded above the fold.
- Fonts are subset and use `font-display: swap`.
- The data table is HTML, not a client-side grid that renders after hydration.
- JavaScript for filters is progressive; the core content works without it.
- INP stays under 200 ms at p75; avoid heavy hydration on long lists.
- CLS stays under 0.1; reserve space for images, ads, and embeds.
- The page works with JavaScript disabled for the primary content.
- Test on a mid-range mobile device, not only on a fast desktop.
