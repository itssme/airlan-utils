insert into "config" ("key", "value")
values ('registration_fee_account_name', 'Verein zur Förderung von Jugendlichen durch Robotikwettbewerbe')
on conflict do nothing;
