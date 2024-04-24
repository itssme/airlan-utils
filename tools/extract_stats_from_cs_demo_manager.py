import psycopg2

database_cs_demo = psycopg2.connect(dbname="postgres", user="postgres", password="pass", host="127.0.0.1", port="5432")
database_airlan = psycopg2.connect(dbname="postgres", user="postgres", password="pass", host="10.44.242.123", port="5432")

with database_cs_demo.cursor() as cursor_cs_demo:
    cursor_cs_demo.execute("SELECT * FROM players")
    parsed_player_stats = cursor_cs_demo.fetchall()

print(f"Found {len(parsed_player_stats)} player stats in the database")

players = {}

# index 6 = kill_count
columns = ["kill_count", "death_count", "assist_count", "kill_death_ratio", "headshot_count", "headshot_percentage",
           "damage_health", "damage_armor", "first_kill_count", "first_death_count", "mvp_count",
           "average_damage_per_round", "average_kill_per_round", "average_death_per_round", "utility_damage_per_round",
           "rank_type", "rank", "old_rank", "wins_count", "bomb_planted_count", "bomb_defused_count",
           "hostage_rescued_count", "score", "kast", "hltv_rating", "hltv_rating_2", "utility_damage",
           "trade_kill_count", "trade_death_count", "first_trade_kill_count", "first_trade_death_count",
           "one_kill_count", "two_kill_count", "three_kill_count", "four_kill_count", "five_kill_count",
           "inspect_weapon_count", "color", "crosshair_share_code"]

columns_sum = ["kill_count", "death_count", "assist_count", "headshot_count", "damage_health", "damage_armor",
               "first_kill_count", "first_death_count", "mvp_count", "utility_damage", "trade_kill_count",
               "trade_death_count", "first_trade_kill_count", "first_trade_death_count", "one_kill_count",
               "two_kill_count", "three_kill_count", "four_kill_count", "five_kill_count", "inspect_weapon_count",
               "bomb_planted_count", "bomb_defused_count", "hostage_rescued_count"]
columns_avg = ["kill_death_ratio", "headshot_percentage", "average_damage_per_round", "average_kill_per_round",
               "average_death_per_round", "utility_damage_per_round", "score", "kast"]

ignore = ["rank_type", "rank", "old_rank", "wins_count", "hltv_rating",
          "hltv_rating_2", "color", "crosshair_share_code"]

for player in parsed_player_stats:
    if player[2] not in players:
        players[player[2]] = {columns[i]: [player[i + 6]] for i in range(len(columns))}
        players[player[2]]["name"] = player[5]
    else:
        for i in range(len(columns)):
            players[player[2]][columns[i]].append(player[i + 6])

for player in players:
    for column in columns_sum:
        players[player][column] = sum(players[player][column])

    for column in columns_avg:
        players[player][column] = sum(players[player][column]) / len(players[player][column])

print(players)

insert_statement = "INSERT INTO demo_stats (\"steam_id\", \"player_name\", "
for column in columns:
    if column not in ignore:
        insert_statement += f'"{column}", '

insert_statement = insert_statement[:-2] + ") VALUES (%s, %s, "
for column in columns:
    if column not in ignore:
        insert_statement += "%s, "
insert_statement = insert_statement[:-2] + ")"
print(insert_statement)

with database_airlan.cursor() as cursor_airlan:
    for player in players:
        values = [player, players[player]["name"]]
        for column in columns:
            if column not in ignore:
                values.append(players[player][column])

        print(values)
        print(insert_statement)
        cursor_airlan.execute(insert_statement, values)
    database_airlan.commit()
