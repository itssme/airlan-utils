insert into "account" ("username", "password", "role", "verified", "verification_code")
values ('api', '', 'admin', 1, '')
on conflict do nothing;