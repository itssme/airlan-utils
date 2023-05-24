insert into "config" ("key", "value")
values ('elo_k_factor', '60') on conflict do nothing;
