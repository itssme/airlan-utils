import os
import sys

from tqdm import tqdm
from demoparser2 import DemoParser


def parse_demo(filename: str):
    parser = DemoParser(filename)
    max_tick = parser.parse_event("round_end")["tick"].max()

    wanted_fields = ["kills_total", "deaths_total", "mvps", "headshot_kills_total", "ace_rounds_total",
                     "4k_rounds_total", "3k_rounds_total"]
    df = parser.parse_ticks(wanted_fields, ticks=[max_tick])
    print(df)
    print(filename)

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
