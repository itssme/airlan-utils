insert into "config" ("key", "value")
values ('airlan_date', '20.04.2024') on conflict do nothing;

insert into "config" ("key", "value")
values ('airlan_date_start_hour', '10') on conflict do nothing;

insert into "config" ("key", "value")
values ('airlan_date_end_hour', '20') on conflict do nothing;

insert into "config" ("key", "value")
values ('pizza_enabled', '0') on conflict do nothing;
