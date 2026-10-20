# Structured data for pSEO pages

Structured data helps search engines and other consumers understand what a page is. It is **not** a ranking factor, a rich-result guarantee, or an AI-citation switch. Mark up what is visible, keep it accurate, and validate the rendered output.

## 1. Choose the type the page actually is

| Page job | Primary type | Supporting types | Notes |
| --- | --- | --- | --- |
| Product detail | `Product` | `Offer`, `BreadcrumbList`, `Organization` | Price and availability must be real and current |
| Software / app | `SoftwareApplication` | `Offer`, `BreadcrumbList` | Use `applicationCategory`, `operatingSystem` |
| Local service | `LocalBusiness` or `Service` | `BreadcrumbList`, `Organization` | Address, area served, hours |
| Directory / category | `CollectionPage` | `ItemList`, `BreadcrumbList` | `ItemList` must match the visible list |
| Comparison / guide | `Article` | `BreadcrumbList`, `Person` | Author and dates matter |
| Calculator / tool | `WebApplication` | `BreadcrumbList` | Do not fake ratings |
| Job board | `JobPosting` | `BreadcrumbList` | This is one of the two valid Google Indexing API cases |
| Event / livestream | `Event` or `BroadcastEvent` | `BreadcrumbList` | `BroadcastEvent` is the other valid Indexing API case |

Do not mark up a comparison page as a `Product`. Do not mark up a category page as a `Product` to chase a snippet. The type must describe the page, not the desired appearance.

`FAQPage` is a valid schema.org type, but Google retired the FAQ rich result in May 2026 and removed the documentation in June 2026. Keep a real FAQ section if it helps readers and answer engines; do not add `FAQPage` markup expecting a Google feature that no longer exists.

## 2. Use one `@graph`

Combine nodes in a single JSON-LD block with stable `@id` values. This is easier to maintain and easier for consumers to connect.

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.com/#organization",
      "name": "Example",
      "url": "https://example.com",
      "logo": "https://example.com/logo.png"
    },
    {
      "@type": "WebSite",
      "@id": "https://example.com/#website",
      "url": "https://example.com",
      "name": "Example",
      "publisher": { "@id": "https://example.com/#organization" }
    },
    {
      "@type": "WebPage",
      "@id": "https://example.com/fattura/designer/forfettario#webpage",
      "url": "https://example.com/fattura/designer/forfettario",
      "name": "Fattura per designer in regime forfettario",
      "description": "Calcolo, regole e modello di fattura per designer forfettari.",
      "isPartOf": { "@id": "https://example.com/#website" },
      "breadcrumb": {
        "@id": "https://example.com/fattura/designer/forfettario#breadcrumb"
      }
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://example.com/fattura/designer/forfettario#breadcrumb",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Fattura",
          "item": "https://example.com/fattura"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Designer",
          "item": "https://example.com/fattura/designer"
        },
        {
          "@type": "ListItem",
          "position": 3,
          "name": "Forfettario"
        }
      ]
    },
    {
      "@type": "SoftwareApplication",
      "@id": "https://example.com/fattura/designer/forfettario#app",
      "name": "Fatturazione per designer forfettari",
      "applicationCategory": "BusinessApplication",
      "operatingSystem": "Web",
      "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "EUR",
        "availability": "https://schema.org/InStock"
      }
    }
  ]
}
```

Rules:

- `@id` values are absolute and stable.
- The `WebPage` node describes the page; the page-type node describes the thing.
- The `BreadcrumbList` mirrors the visible breadcrumb, not the sitemap.
- The last breadcrumb item usually has no `item` because it is the current page.
- Do not include nodes for content that is not on the page.

## 3. Page-type notes

### Product

Required/recommended by Google's product documentation:

- `name`
- `image`
- `description`
- `offers` with `price`, `priceCurrency`, and `availability`
- `brand` or `manufacturer`
- `sku` / `gtin` where applicable

Do not invent a price or availability. If the page is a comparison or a category, use `ItemList` or `Article`, not `Product`.

### SoftwareApplication

- `name`
- `applicationCategory`
- `operatingSystem`
- `offers` if there is a real price, including `price: "0"` for a free tier
- `aggregateRating` or `review` only if genuine, visible, and collected from real users

Fake ratings are a manual-action risk and a trust failure. Do not generate them from a template.

### LocalBusiness

- `name`
- `address` (`PostalAddress`)
- `telephone` or `url`
- `areaServed`
- `openingHoursSpecification` if the hours are real
- `geo` if the coordinates are exact

A location page with no local address, local phone, local proof, or local service area is a doorway page, not a local business page. Schema will not fix that.

### Article

- `headline`
- `author` (`Person` with `sameAs` where possible)
- `datePublished`
- `dateModified`
- `publisher` (`Organization`)
- `image`

Use the real author and the real review date. Do not invent an expert reviewer.

### CollectionPage + ItemList

- `CollectionPage` describes the category or hub.
- `ItemList` lists the visible items in the same order.
- `itemListElement` can be `ListItem` with `url` or a nested `Product`.
- Do not include items that are not visible without interaction.

### WebApplication

Use for a calculator or interactive tool. Include `name`, `applicationCategory`, `operatingSystem`, and a real `offers` node if there is a price. Do not use `SoftwareApplication` for a page that is just a form with no working tool.

## 4. Dates, authors, and trust

For informational or comparison pages:

- `datePublished` and `dateModified` must be real. Do not update `dateModified` on every deploy.
- The author should be a real person or a real editorial team, with a profile page if possible.
- The reviewer should be real and qualified where the topic requires it (medical, legal, financial).
- `sameAs` links should point to canonical profiles, not to unrelated social accounts.

For regulated topics, the page needs more than schema: a named reviewer, a review date, sources, and a clear disclaimer.

## 5. Validation

Validate the **rendered HTML**, not the template source:

1. Fetch the page with JavaScript disabled.
2. Extract every `<script type="application/ld+json">` block.
3. Parse each block as JSON.
4. Validate with the [Schema Markup Validator](https://validator.schema.org/) and, where a Google feature still exists, the [Rich Results Test](https://search.google.com/test/rich-results).
5. Compare the marked-up content with what a user sees.

Automated checks worth adding to CI:

- JSON parses.
- `@context` is present.
- Every `@id` is unique within the page.
- `BreadcrumbList` positions are sequential.
- No `aggregateRating` unless the page has visible reviews.
- No `FAQPage` unless the page has visible questions and answers.
- No placeholder strings (`{`, `}`, `undefined`, `null`).
- The canonical in `WebPage.url` matches the page's `<link rel="canonical">`.

## 6. Common errors

| Error | Why it hurts |
| --- | --- |
| Marking up content that is not visible | Violates Google's structured data guidelines |
| Fake `aggregateRating` or `review` | Manual action and trust risk |
| Using `Product` for a category or comparison | Wrong type; no eligibility, possible confusion |
| `FAQPage` for a retired rich result | Wasted effort; no Google feature |
| Missing `offers` on a product page | Ineligible for product snippets |
| Price in schema differs from the visible price | Misleading |
| `dateModified` updated daily without changes | Erodes trust; may be ignored |
| Multiple conflicting `@context` blocks | Hard to parse; use one `@graph` |
| `BreadcrumbList` that does not match the UI | Misleading |
| JSON-LD injected without escaping `<` | XSS risk |

## 7. Injection safety

In React/Next.js:

```tsx
const json = JSON.stringify(data).replace(/</g, '\\u003c')

return (
  <script
    type="application/ld+json"
    dangerouslySetInnerHTML={{ __html: json }}
  />
)
```

In Vue/Nuxt:

```vue
<script setup lang="ts">
const json = computed(() =>
  JSON.stringify(data).replace(/</g, '\\u003c'),
)
</script>

<template>
  <component :is="'script'" type="application/ld+json" v-html="json" />
</template>
```

In Astro:

```astro
---
const json = JSON.stringify(data).replace(/</g, '\\u003c')
---
<script type="application/ld+json" set:html={json} />
```

Never interpolate raw user data into a script tag without escaping. A product name containing `</script>` can break the page.

## 8. What schema does not do

- It does not guarantee a rich result.
- It does not guarantee indexing.
- It does not make a thin page useful.
- It does not replace internal links, sitemaps, or content quality.
- It does not make a page eligible for an AI answer.

Use it as accurate metadata for a page that already deserves to exist.
