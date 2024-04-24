create table demo_stats
(
    steam_id                 varchar(255) primary key,
    player_name              varchar(255),
    kill_count               float,
    death_count              float,
    assist_count             float,
    kill_death_ratio         float,
    headshot_count           float,
    headshot_percentage      float,
    damage_health            float,
    damage_armor             float,
    first_kill_count         float,
    first_death_count        float,
    mvp_count                float,
    average_damage_per_round float,
    average_kill_per_round   float,
    average_death_per_round  float,
    utility_damage_per_round float,
    bomb_planted_count       float,
    bomb_defused_count       float,
    hostage_rescued_count    float,
    score                    float,
    kast                     float,
    utility_damage           float,
    trade_kill_count         float,
    trade_death_count        float,
    first_trade_kill_count   float,
    first_trade_death_count  float,
    one_kill_count           float,
    two_kill_count           float,
    three_kill_count         float,
    four_kill_count          float,
    five_kill_count          float,
    inspect_weapon_count     float
);
