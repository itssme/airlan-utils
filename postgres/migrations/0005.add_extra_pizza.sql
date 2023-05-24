insert into "food_type" ("name", "description", "price")
values ('Thunfisch', 'Pizza mit Thunfisch', 5)
on conflict do nothing;