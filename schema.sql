create table if not exists commodity (
  id serial primary key,
  slug text unique not null,
  name text not null
);

create table if not exists price_daily (
  commodity_id int references commodity(id),
  ref_date date not null,
  spec text,
  price_brl numeric(14,4),
  price_usd numeric(14,4),
  source_url text,
  inserted_at timestamptz default now(),
  primary key (commodity_id, ref_date, coalesce(spec,''))
);

drop materialized view if exists price_variations;
create materialized view price_variations as
select
  p.*,
  (price_brl - lag(price_brl) over w) / nullif(lag(price_brl) over w,0)::numeric as var_d1,
  (price_brl - lag(price_brl,30) over w) / nullif(lag(price_brl,30) over w,0)::numeric as var_30d,
  (price_brl - lag(price_brl,180) over w) / nullif(lag(price_brl,180) over w,0)::numeric as var_180d,
  (price_brl - lag(price_brl,360) over w) / nullif(lag(price_brl,360) over w,0)::numeric as var_360d
from price_daily p
window w as (partition by commodity_id, coalesce(spec,'') order by ref_date);
