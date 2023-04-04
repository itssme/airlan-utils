create table if not exists "player"
(
    "id"           serial primary key,
    "name"         text        not null,
    "steam_id"     text unique not null,
    "steam_name"   text        not null,
    "profile_url"  text        not null,
    "avatar_url"   text        not null,
    "last_updated" int default 0 -- unix timestamp of the time the steam_name, profile_url and avatar_url were last updated
);

create table if not exists "account"
(
    "username" text primary key,
    "password" text not null, -- stored as hash
    "role"     text not null default 'user'
);

create table if not exists "team"
(
    "id"                    serial primary key,
    "tag"                   text                      not null,
    "name"                  text unique               not null,
    "elo"                   int default 1000,
    "competing"             int default 2,                      -- 0 = competing, 1 = not competing, 2 = completely ignored (even not visible in the leaderboard)
    "paid_registration_fee" int default 0,                      -- 0 = not paid, 1 = paid
    "registration_fee_rnd"  text                      not null, -- random text used for transaction
    "verified"              int default 0,                      -- 0 = not verified, 1 = verified
    "account"               text references "account" not null,
    "locked_changes"        int default 0,                      -- 0 = not locked, 1 = locked (user cannot change team name, tag, or players anymore)
    "locked_changes_time"   int default null,                   -- unix timestamp of the time the team was locked
    "sponsored"             int default 0                       -- 0 = not sponsored, 1 = sponsored
);

create table if not exists "team_assignment"
(
    "team"   integer references "team" on delete cascade,
    "player" integer references "player" on delete cascade,
    primary key ("team", "player")
);

create table if not exists "match"
(
    "id"                   serial primary key,
    "matchid"              text    not null unique,
    "name"                 text    not null,
    "team1"                integer references "team" default null,
    "team2"                integer references "team" default null,
    "best_out_of"          integer not null,
    "number_in_map_series" integer                   default 0,
    "series_score_team1"   integer                   default 0,
    "series_score_team2"   integer                   default 0,
    "finished"             integer                   default -1 -- -1 game is not ready, 0 game is running, 1 game is finished, 2 game is finished and demo is uploaded, 3 failed/ stopped
);

create table if not exists "host"
(
    "ip" text primary key
);

create table if not exists "server"
(
    "id"             serial primary key,
    "ip"             text default 'host.docker.internal' references "host",
    "port"           int  default -1,
    "gslt_token"     text default null,
    "container_name" text default null,
    "match"          integer references "match"
);

create table if not exists "stats"
(
    "id"     serial primary key,
    "match"  integer references "match" on delete cascade,
    "player" integer references "player" on delete cascade default null,
    "type"   integer not null
);

create table if not exists "food_type"
(
    "id"          serial primary key,
    "name"        text  not null,
    "description" text  not null,
    "price"       float not null
);

insert into "food_type" ("name", "description", "price")
values ('Keine Pizza', '', 0)
on conflict do nothing;

insert into "food_type" ("name", "description", "price")
values ('Margherita', 'Vegetarische Pizza', 5)
on conflict do nothing;

insert into "food_type" ("name", "description", "price")
values ('Salami', 'Pizza mit Salami', 5)
on conflict do nothing;

insert into "food_type" ("name", "description", "price")
values ('Provinciale', 'Pizza mit Mais und Speck', 5)
on conflict do nothing;


create table if not exists "food_order"
(
    id     serial primary key,
    player integer references "player" on delete cascade,
    food   integer references "food_type" on delete cascade
);
