# Sources and verification notes

The skill was reviewed against official documentation on **2026-10-21**. Search features, framework APIs, quotas, and policies change; re-check the source before relying on a specific number or feature.

## Google Search

- **Spam policies** — scaled content abuse, doorway abuse, thin affiliation, site reputation, keyword stuffing, cloaking.  
  https://developers.google.com/search/docs/essentials/spam-policies
- **Guidance on using generative AI content** — quality, accuracy, disclosure, review. Updated 2026-10-01.  
  https://developers.google.com/search/docs/fundamentals/using-gen-ai-content
- **Optimizing for generative AI features** — Google's current AI-search guidance and mythbusting.  
  https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- **Indexing API quickstart** — explicitly limited to `JobPosting` and `BroadcastEvent` embedded in a `VideoObject`.  
  https://developers.google.com/search/apis/indexing-api/v3/quickstart
- **Build and submit a sitemap** — 50,000 URLs / 50 MB per sitemap, `lastmod` semantics, sitemap index. Updated 2026-07-08.  
  https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- **Structured data general guidelines** — content must be visible, accurate, and representative.  
  https://developers.google.com/search/docs/appearance/structured-data/sd-policies
- **Search Central documentation updates** — FAQ rich result deprecation (May 8, 2026; documentation removed June 15, 2026), Indexing API quota update (October 16, 2026).  
  https://developers.google.com/search/updates
- **Core Web Vitals** — LCP, INP, CLS thresholds and p75 measurement.  
  https://developers.google.com/search/docs/appearance/core-web-vitals
  https://web.dev/articles/vitals
- **Search Console API** — sitemaps and URL Inspection.  
  https://developers.google.com/webmaster-tools/v1/sitemaps  
  https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect

## IndexNow

- **Protocol documentation** — key file, single and batch submission, response codes, 10,000 URLs per POST, shared distribution to participants.  
  https://www.indexnow.org/documentation
- **FAQ and participant list** — Bing, Yandex, Seznam, Naver, Yep, and other participants; Google does not participate.  
  https://www.indexnow.org/faq

## Next.js

- **Route segment config** — `dynamicParams`, `runtime`, and the Next.js 16 removal of `dynamic`, `dynamicParams`, `revalidate`, and `fetchCache` when Cache Components is enabled. Updated 2026-10-01.  
  https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config
- **`generateStaticParams`** — params are async, partial prerender, Cache Components requirements. Updated 2026-10-01.  
  https://nextjs.org/docs/app/api-reference/functions/generate-static-params
- **Caching with Cache Components** — `'use cache'`, `cacheLife`, `cacheTag`, PPR, ISR behavior. Updated 2026-10-06.  
  https://nextjs.org/docs/app/getting-started/caching
- **ISR with Cache Components** — prerender a subset, upgrade unknown params on demand. Updated 2026-10-15.  
  https://nextjs.org/docs/app/guides/incremental-static-regeneration-cache-components
- **Sitemap metadata file** — `generateSitemaps`, 50,000 URL guidance, localized sitemaps. Updated 2026-08-18.  
  https://nextjs.org/docs/app/api-reference/file-conventions/metadata/sitemap
- **Proxy file convention** — `middleware.ts` renamed to `proxy.ts` in Next.js 16, Node.js runtime by default. Updated 2026-09-04.  
  https://nextjs.org/docs/app/api-reference/file-conventions/proxy

## Nuxt

- **Rendering modes** — universal, client, hybrid, route rules, `isr`, `swr`, `prerender`, edge-side rendering.  
  https://nuxt.com/docs/4.x/guide/concepts/rendering
- **Nuxt configuration / route rules** — `routeRules`, `headers`, redirects, proxy.  
  https://nuxt.com/docs/4.x/api/nuxt-config#routerules

## Schema.org

- **Schema.org vocabulary** — types and properties.  
  https://schema.org/
- **Validator** — validate the rendered JSON-LD.  
  https://validator.schema.org/

## Notes on interpretation

- Google's documentation is authoritative for Google Search behavior. Third-party studies and tool vendors are not.
- IndexNow's documentation is authoritative for the protocol. The participant list can change; check it before promising coverage.
- Framework docs are versioned. The snippets in this skill assume the versions named in the section; verify the installed version before copying.
- Search Console data is first-party but can be delayed, sampled, or incomplete. Label it with the export date.
- Keyword-tool volumes are estimates. Never present them as measured traffic.
