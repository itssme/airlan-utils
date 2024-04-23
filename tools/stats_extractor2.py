import os
import sys

from tqdm import tqdm
from demoparser2 import DemoParser


def parse_demo(filename: str):
    print(filename)

    parser = DemoParser(filename)
    #max_tick = parser.parse_event("round_end")["tick"].max()

    #wanted_fields = ["kills_total", "deaths_total", "mvps", "headshot_kills_total", "ace_rounds_total",
    #                 "4k_rounds_total", "3k_rounds_total", "bomb_planted"]
    #df = parser.parse_ticks(wanted_fields, ticks=[max_tick])
    #print(df)

    df = parser.parse_events(["player_blind", "bomb_defused", "bomb_pickup", "smokegrenade_detonate", "inferno_startburn", "weapon_reload", "player_death", "player_jump", "bomb_planted", "bomb_exploded", "bomb_dropped", "decoy_detonate", "player_footstep"])
    print(df)

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

    quit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python stats_extractor2.py path_to_demo_folder")
        sys.exit(1)

    demo_folder = sys.argv[1]
    demo_files = list(filter(lambda x: x.endswith(".dem"), os.listdir(demo_folder)))

    print(f"Found {len(demo_files)} demos in {demo_folder}")

    for demo_file in tqdm(demo_files):
        demo_path = os.path.join(demo_folder, demo_file)
        parse_demo(demo_path)


if __name__ == '__main__':
    main()
