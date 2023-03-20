from demoparser import DemoParser
import glob
import multiprocessing as mp
import pandas as pd
import tqdm
import sqlite3


def parse(file):
    parser = DemoParser(file)
    df = pd.DataFrame(parser.parse_events("player_death", rounds=True))
    df = df[df["round"] != 0]  # remove warmup
    df.insert(0, "file", file)
    return df


if __name__ == "__main__":
    files = glob.glob("/home/joel/Documents/airlan/airlan23_winter_demos/*")
    print(files)

    with mp.Pool(processes=12) as pool:
        results = list(tqdm.tqdm(pool.imap_unordered(parse, files), total=len(files)))
    df = pd.concat(results)

    # Creates db if not exists
    con = sqlite3.connect("events.db")
    df.to_sql("player_death", con=con, if_exists='append')
