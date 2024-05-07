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

    # {"player_name": {"1": [tick, tick..]}}
    player_kills_per_round = {}

    # iterate over rounds
    for index, row in df.iterrows():
        attacker_name = row["attacker_name"]
        if attacker_name is None:
            continue
        round_number = row["total_rounds_played"]

        if attacker_name not in player_kills_per_round:
            player_kills_per_round[attacker_name] = {}

        if round_number not in player_kills_per_round[attacker_name]:
            player_kills_per_round[attacker_name][round_number] = [row["tick"]]
        else:
            player_kills_per_round[attacker_name][round_number].append(row["tick"])

    # filter out rounds with less than 2 kills
    for player in player_kills_per_round:
        player_kills_per_round[player] = {round_number: ticks for round_number, ticks in
                                          player_kills_per_round[player].items() if len(ticks) > 1}

    # calculate the difference between the first kill and the last kill in a round
    # {"player_name": {"1": {"time_span": max(ticks) - min(ticks), kills: len(ticks)}}
    player_kills_per_round_sorted = {}
    for player in player_kills_per_round:
        player_kills_per_round_sorted[player] = {}
        for round in player_kills_per_round[player]:
            ticks = player_kills_per_round[player][round]
            player_kills_per_round_sorted[player][round] = {"time_span": max(ticks) - min(ticks), "kills": len(ticks)}

    # {"2ks": [{"round": x, "player": player_name, "time_span"}: time_span], "3ks": [], "4ks": [], "5ks": []}
    interesting_round_kills = {"2ks": [], "3ks": [], "4ks": [], "5ks": []}
    for player in player_kills_per_round_sorted:
        for round in player_kills_per_round_sorted[player]:
            time_span = player_kills_per_round_sorted[player][round]["time_span"]
            kills = player_kills_per_round_sorted[player][round]["kills"]

            if kills == 2:
                interesting_round_kills["2ks"].append({"round": round, "player": player, "time_span": time_span})
            elif kills == 3:
                interesting_round_kills["3ks"].append({"round": round, "player": player, "time_span": time_span})
            elif kills == 4:
                interesting_round_kills["4ks"].append({"round": round, "player": player, "time_span": time_span})
            elif kills == 5:
                interesting_round_kills["5ks"].append({"round": round, "player": player, "time_span": time_span})

    return interesting_round_kills


def main():
    if len(sys.argv) != 2:
        print("Usage: python stats_extractor2.py path_to_demo_folder")
        sys.exit(1)

    demo_folder = sys.argv[1]
    demo_files = list(filter(lambda x: x.endswith(".dem"), os.listdir(demo_folder)))

    print(f"Found {len(demo_files)} demos in {demo_folder}")

    total_interesting_round_kills = {"2ks": [], "3ks": [], "4ks": [], "5ks": []}

    for demo_file in tqdm(demo_files):
        demo_path = os.path.join(demo_folder, demo_file)
        new_rounds = parse_demo(demo_path)

        for key in new_rounds:
            for round in new_rounds[key]:
                total_interesting_round_kills[key].append(
                    {"demo_file": demo_file, "player": round["player"], "round": round["round"],
                     "time_span": round["time_span"]})

    # sort total_interesting_round_kills by time_span
    for key in total_interesting_round_kills:
        total_interesting_round_kills[key] = sorted(total_interesting_round_kills[key], key=lambda x: x["time_span"],
                                                    reverse=False)

    # pretty print json
    print(json.dumps(total_interesting_round_kills, indent=4))

    with open('interesting_round_kills.json', 'w') as f:
        json.dump(total_interesting_round_kills, f)


if __name__ == '__main__':
    main()
