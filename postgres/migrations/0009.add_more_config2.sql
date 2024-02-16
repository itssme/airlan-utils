insert into "config" ("key", "value")
values ('articles_enabled', '0') on conflict do nothing;

insert into "config" ("key", "value")
values ('oder_table_enabled', '0') on conflict do nothing;
