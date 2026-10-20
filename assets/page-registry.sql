-- Programmatic SEO page registry
-- PostgreSQL 13+
-- Adapt names and types to the project; keep the constraints.

create table if not exists pseo_families (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  route_pattern text not null,
  intent text not null,
  template_version text not null default 'v1',
  min_unique_facts integer not null default 5 check (min_unique_facts >= 0),
  status text not null default 'active'
    check (status in ('draft', 'active', 'paused', 'retired')),
  owner text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists pseo_sources (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  base_url text,
  license text,
  rights_note text,
  update_cadence text,
  last_fetched_at timestamptz,
  reliability text check (reliability in ('high', 'medium', 'low', 'unknown'))
    default 'unknown',
  created_at timestamptz not null default now()
);

create table if not exists pseo_entities (
  id uuid primary key default gen_random_uuid(),
  family_id uuid not null references pseo_families(id) on delete cascade,
  slug text not null,
  name text not null,
  data jsonb not null default '{}'::jsonb,
  source_id uuid references pseo_sources(id),
  source_url text,
  retrieved_at timestamptz,
  confidence numeric(3, 2) check (confidence is null or confidence between 0 and 1),
  created_at timestamptz not null default now(),
  unique (family_id, slug)
);

create table if not exists pseo_pages (
  id uuid primary key default gen_random_uuid(),
  family_id uuid not null references pseo_families(id),
  entity_id uuid references pseo_entities(id),
  path text not null unique,
  canonical_path text not null,
  status text not null default 'candidate'
    check (status in ('candidate', 'eligible', 'published', 'suppressed', 'retired')),
  indexable boolean not null default false,
  http_status integer not null default 200
    check (http_status in (200, 301, 302, 404, 410)),
  redirect_to text,
  title text,
  meta_description text,
  h1 text,
  primary_query text,
  demand_score smallint check (demand_score between 0 and 5),
  data_score smallint check (data_score between 0 and 5),
  quality_score smallint check (quality_score between 0 and 5),
  priority_score numeric(5, 2),
  unique_facts integer not null default 0 check (unique_facts >= 0),
  content_hash text,
  template_version text,
  source_updated_at timestamptz,
  published_at timestamptz,
  last_reviewed_at timestamptz,
  lastmod timestamptz,
  retired_at timestamptz,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  -- A published page is indexable, live, and self-canonical.
  constraint pseo_pages_published_consistent check (
    status <> 'published'
    or (indexable = true and http_status = 200 and canonical_path = path)
  ),
  -- Non-published pages are never indexable.
  constraint pseo_pages_nonpublished_not_indexable check (
    status = 'published' or indexable = false
  ),
  -- Retired pages resolve to a redirect or a gone status.
  constraint pseo_pages_retired_resolution check (
    status <> 'retired'
    or http_status in (404, 410)
    or (http_status in (301, 302) and redirect_to is not null)
  ),
  -- Redirects must not point to themselves.
  constraint pseo_pages_no_self_redirect check (
    redirect_to is null or redirect_to <> path
  ),
  -- lastmod cannot predate publication.
  constraint pseo_pages_lastmod_after_publish check (
    published_at is null or lastmod is null or lastmod >= published_at
  )
);

create index if not exists pseo_pages_family_idx
  on pseo_pages (family_id);

create index if not exists pseo_pages_status_idx
  on pseo_pages (status, indexable, http_status);

create index if not exists pseo_pages_lastmod_idx
  on pseo_pages (lastmod desc);

create index if not exists pseo_pages_primary_query_idx
  on pseo_pages (primary_query);

create index if not exists pseo_pages_content_hash_idx
  on pseo_pages (content_hash);

create index if not exists pseo_pages_canonical_idx
  on pseo_pages (canonical_path);

create table if not exists pseo_facts (
  id bigserial primary key,
  entity_id uuid references pseo_entities(id) on delete cascade,
  page_id uuid references pseo_pages(id) on delete cascade,
  key text not null,
  value jsonb not null,
  source_id uuid references pseo_sources(id),
  source_url text,
  retrieved_at timestamptz not null default now(),
  confidence numeric(3, 2) check (confidence is null or confidence between 0 and 1),
  constraint pseo_facts_owner check (entity_id is not null or page_id is not null),
  unique (page_id, key)
);

create index if not exists pseo_facts_entity_idx
  on pseo_facts (entity_id, key);

create unique index if not exists pseo_facts_entity_key_uidx
  on pseo_facts (entity_id, key)
  where entity_id is not null and page_id is null;

create table if not exists pseo_indexing_events (
  id uuid primary key default gen_random_uuid(),
  page_id uuid not null references pseo_pages(id) on delete cascade,
  url text not null,
  provider text not null check (provider in ('indexnow', 'google_indexing_api', 'sitemap', 'search_console')),
  event_type text not null check (event_type in ('created', 'updated', 'deleted')),
  idempotency_key text not null,
  status text not null default 'pending'
    check (status in ('pending', 'sent', 'failed', 'dead')),
  attempts integer not null default 0 check (attempts >= 0),
  response_status integer,
  response_body text,
  next_retry_at timestamptz,
  created_at timestamptz not null default now(),
  completed_at timestamptz,
  unique (provider, idempotency_key)
);

create index if not exists pseo_indexing_events_pending_idx
  on pseo_indexing_events (status, next_retry_at)
  where status in ('pending', 'failed');

create table if not exists pseo_reviews (
  id bigserial primary key,
  page_id uuid references pseo_pages(id) on delete set null,
  family_id uuid references pseo_families(id) on delete set null,
  action text not null
    check (action in ('keep', 'improve', 'consolidate', 'redirect', 'remove', 'refresh')),
  reason text not null,
  owner text,
  expected_outcome text,
  review_at date,
  created_at timestamptz not null default now()
);

-- Optional: keep updated_at accurate.
create or replace function pseo_touch_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists pseo_pages_touch on pseo_pages;
create trigger pseo_pages_touch
before update on pseo_pages
for each row execute function pseo_touch_updated_at();

drop trigger if exists pseo_families_touch on pseo_families;
create trigger pseo_families_touch
before update on pseo_families
for each row execute function pseo_touch_updated_at();

-- Sitemap source of truth.
create or replace view pseo_sitemap_pages as
select path, lastmod
from pseo_pages
where status = 'published'
  and indexable = true
  and http_status = 200
  and canonical_path = path
  and lastmod is not null;
