import os
import sys
import json

from tqdm import tqdm
from demoparser2 import DemoParser


def parse_demo(filename: str):
    print(filename)

    parser = DemoParser(filename)

    df = parser.parse_event("player_death", player=["last_place_name", "team_name"],
                            other=["total_rounds_played", "is_warmup_period"])

    # filter out team-kills and warmup
    df = df[df["attacker_team_name"] != df["user_team_name"]]
    df = df[df["is_warmup_period"] == False]

    # group-by like in sql
    df = df.groupby(["total_rounds_played", "attacker_name"]).size().to_frame(name='total_kills').reset_index()

    interesting_round_kills = {"3ks": [], "4ks": [], "5ks": []}

    for index, row in df.iterrows():
        if row["total_kills"] == 3:
            interesting_round_kills["3ks"].append(row)
        elif row["total_kills"] == 4:
            interesting_round_kills["4ks"].append(row)
        elif row["total_kills"] == 5:
            interesting_round_kills["5ks"].append(row)

    return interesting_round_kills

    #max_tick = parser.parse_event("round_end")["tick"].max()

    #wanted_fields = ["kills_total", "deaths_total", "mvps", "headshot_kills_total", "ace_rounds_total",
    #                 "4k_rounds_total", "3k_rounds_total", "bomb_planted"]
    #df = parser.parse_ticks(wanted_fields, ticks=[max_tick])
    #print(df)

    #df = parser.parse_events(["player_blind", "bomb_defused", "bomb_pickup", "smokegrenade_detonate", "inferno_startburn", "weapon_reload", "player_death", "player_jump", "bomb_planted", "bomb_exploded", "bomb_dropped", "decoy_detonate", "player_footstep"])
    #print(df)

    # df = parser.list_game_events()
    # ['decoy_started', 'hegrenade_detonate', 'round_announce_match_start', 'player_connect', 'player_blind',
    # 'player_team', 'round_officially_ended', 'player_hurt', 'inferno_expire', 'player_disconnect',
    # 'cs_win_panel_match', 'buytime_ended', 'other_death', 'hltv_chase', 'bomb_defused',
    # 'round_announce_last_round_half', 'player_spawn', 'flashbang_detonate', 'begin_new_match',
    # 'round_announce_match_point', 'bomb_pickup', 'cs_round_final_beep', 'item_equip', 'round_prestart',
    # 'cs_pre_restart', 'hltv_versioninfo', 'smokegrenade_expired', 'smokegrenade_detonate', 'cs_round_start_beep',
    # 'player_connect_full', 'announce_phase_end', 'inferno_startburn', 'server_cvar', 'weapon_reload', 'hltv_fixed',
    # 'player_death', 'round_freeze_end', 'player_jump', 'bomb_begindefuse', 'weapon_zoom', 'weapon_fire',
    # 'bomb_beginplant', 'bomb_planted', 'bomb_exploded', 'round_poststart', 'bomb_dropped', 'decoy_detonate',
    # 'player_footstep', 'item_pickup']


def main():
    if len(sys.argv) != 2:
        print("Usage: python stats_extractor2.py path_to_demo_folder")
        sys.exit(1)

    demo_folder = sys.argv[1]
    demo_files = list(filter(lambda x: x.endswith(".dem"), os.listdir(demo_folder)))

    print(f"Found {len(demo_files)} demos in {demo_folder}")

    total_interesting_round_kills = {"3ks": [], "4ks": [], "5ks": []}

    for demo_file in tqdm(demo_files):
        demo_path = os.path.join(demo_folder, demo_file)
        new_rounds = parse_demo(demo_path)

        for key in new_rounds:
            for round in new_rounds[key]:
                total_interesting_round_kills[key].append({"demo_file": demo_file, "player": round["attacker_name"], "round": round["total_rounds_played"]})

    # pretty print json
    print(json.dumps(total_interesting_round_kills, indent=4))


if __name__ == '__main__':
    main()
