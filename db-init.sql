--
-- initialize gkh database
--

\set ON_ERROR_STOP on

drop table if exists regions cascade;
create table regions(
  region text primary key,
  code text,
  official_name_ru text,
  official_name_en text
);

drop table if exists attrvals_all cascade;
create table attrvals_all(
  region text references regions(region) on delete cascade on update cascade,
  house_id text,
  attr_name text,
  found_name text,
  ed_dist INTEGER,
  "value" text,
  ts timestamp default now(),
  primary key (region, house_id, ts, attr_name)
);

drop view if exists attrvals;
create view attrvals as
select distinct on (region, house_id, attr_name)
  region,
  house_id,
  attr_name,
  found_name,
  ed_dist,
  "value",
  ts
from attrvals_all
order by region, house_id, attr_name, ts desc
;
