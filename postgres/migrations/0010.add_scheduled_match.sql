create table "map"
(
    "id"          serial primary key,
    "name"        varchar(255) not null,
    "description" text default '',
    "image"       varchar(255) not null
);

insert into "map" ("name", "description", "image")
values ('de_inferno',
        'Inferno ist eine düstere und enge Karte, die auf dem italienischen Land spielt. Die engen Gassen und Durchgänge bieten viele Möglichkeiten für Nahkämpfe, während die zahlreichen Winkel und Ecken den CTs Vorteile beim Verteidigen bieten. Inferno ist eine der ältesten Karten in CS:GO und wird immer noch häufig in Turnieren gespielt.',
        '/static/images/maps/inferno.webp');

insert into "map" ("name", "description", "image")
values ('de_mirage',
        'Mirage ist eine Karte, die in Marokko spielt. Sie ist eine sehr ausgeglichene Karte, die sowohl für T als auch für CT viele Möglichkeiten bietet. Die Karte ist relativ offen, was sie für Scharfschützen und AWP-Spieler attraktiv macht. Die zahlreichen Rauch- und Blitzplätze machen die Karte jedoch auch für taktische Spielzüge attraktiv.',
        '/static/images/maps/mirage.webp');

insert into "map" ("name", "description", "image")
values ('cs_office',
        'Office ist eine Karte, die in einem modernen Bürogebäude spielt. Die engen Korridore und Räume bieten viele Möglichkeiten für Nahkämpfe, während die zahlreichen Büros und Flure den Ts Vorteile beim Verteidigen bieten. Die Karte ist relativ klein, was schnelle Entscheidungen und schnelles Handeln erfordert.',
        '/static/images/maps/office.webp');

insert into "map" ("name", "description", "image")
values ('de_ancient',
        'Ancient ist eine Karte, die in einem alten Tempel spielt. Die Karte ist relativ groß und bietet viele Möglichkeiten für Scharfschützen und AWP-Spieler. Die zahlreichen Wege und Durchgänge erfordern jedoch auch taktisches Denken und schnelle Entscheidungen. Ancient ist eine sehr beliebte Karte bei CS2-Spielern.',
        '/static/images/maps/ancient.webp');

insert into "map" ("name", "description", "image")
values ('de_overpass',
        'Overpass ist eine Karte, die in einem Kanalisationssystem spielt. Die zahlreichen Rohre und Durchgänge bieten viele Möglichkeiten für Nahkämpfe, während die zahlreichen Winkel und Ecken den CTs Vorteile beim Verteidigen bieten. Overpass erfordert schnelle Entscheidungen und schnelles Handeln, da die Karte relativ klein ist.',
        '/static/images/maps/overpass.webp');

insert into "map" ("name", "description", "image")
values ('de_vertigo',
        'Vertigo ist eine Karte, die auf einem Wolkenkratzer spielt. Die Karte ist sehr ungewöhnlich, da sie auf verschiedenen Ebenen spielt und es viele Möglichkeiten gibt, um sich zu verstecken. Die zahlreichen Abgründe erfordern jedoch auch taktisches Denken und schnelle Entscheidungen. Vertigo ist eine sehr beliebte Karte bei CS:GO-Spielern.',
        '/static/images/maps/vertigo.webp');

insert into "map" ("name", "description", "image")
values ('de_anubis',
        'Anubis ist eine Karte, die in einem antiken Tempel in Ägypten spielt. Die Karte bietet viele Möglichkeiten für Nahkämpfe, während die zahlreichen Wege und Durchgänge den Spielern taktische Optionen bieten. Die Karte ist relativ neu in CS2 und hat sich schnell zu einer beliebten Wahl für Wettkämpfe entwickelt.',
        '/static/images/maps/anubis.webp');

create table beo1_vote
(
    "id"     serial primary key,
    "ban_1"  integer references "map" ("id") default null,
    "ban_2"  integer references "map" ("id") default null,
    "ban_3"  integer references "map" ("id") default null,
    "ban_4"  integer references "map" ("id") default null,
    "ban_5"  integer references "map" ("id") default null,
    "pick_6" integer references "map" ("id") default null
);

create table beo3_vote
(
    "id"     serial primary key,
    "ban_1"  integer references "map" ("id") default null,
    "ban_2"  integer references "map" ("id") default null,
    "pick_3" integer references "map" ("id") default null,
    "pick_4" integer references "map" ("id") default null,
    "ban_5"  integer references "map" ("id") default null,
    "ban_6"  integer references "map" ("id") default null,
    "pick_7" integer references "map" ("id") default null
);

create table "scheduled_match"
(
    "id"          serial primary key,
    "team1"       integer references "team" ("id") not null,
    "team2"       integer references "team" ("id") not null,
    "best_out_of" integer                          not null,
    "description" text                                default '',
    "match_group" integer                             default null,        -- these matches will be queued when 'live_matches' is set to the map group
    "status"      varchar(255)                        default 'scheduled', -- 'scheduled', 'voting', 'in_progress', 'finished'
    "match"       integer references "match" ("id")   default null,
    "beo1_vote"   integer references beo1_vote ("id") default null,
    "beo3_vote"   integer references beo3_vote ("id") default null
);

-- 'live_matches' is used to set the map group for the next scheduled match (default 0 means no matches are being queued)
insert into "config" ("key", "value")
values ('live_matches', '0');
