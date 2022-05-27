import json

import pandas
import requests
from pprint import pprint
import csv
import time
import numpy as np
from main import merge_csv
import pandas as pd


def save_data(games, last_match_id):
    with open(base_path + f"/data_{len(games)}_{last_match_id}.csv", "w", newline="") as f:
        header = "match_id,match_seq_num,radiant_win,start_time,duration,avg_mmr,num_mmr,lobby_type,game_mode," \
                 "avg_rank_tier," \
                 "num_rank_tier,cluster,radiant_team,dire_team".split(",")
        cw = csv.DictWriter(f, header)
        cw.writeheader()
        cw.writerows(games)
    pprint(len(games))


def separate_data(file_path):
    df = pd.read_csv(file_path)

    mask_treatment1 = df.radiant_team.apply(lambda x: "14" in x.split(","))
    mask_treatment2 = df.dire_team.apply(lambda x: "14" in x.split(","))
    data_treatment = df[mask_treatment1 | mask_treatment2]
    mask_control1 = df.radiant_team.apply(lambda x: "14" not in x.split(","))
    mask_control2 = df.dire_team.apply(lambda x: "14" not in x.split(","))
    data_control = df[mask_control1 & mask_control2]

    data_control.to_csv("/Users/noyantoksoy/Downloads/data_control_new.csv")
    data_treatment.to_csv("/Users/noyantoksoy/Downloads/data_treatment_new.csv")
    print("Control: ", data_control.match_id.nunique())
    print("Treatment: ", data_treatment.match_id.nunique())


if __name__ == '__main__':
    # merge_csv()
    base_path = "/Users/noyantoksoy/Downloads/gather_data_new"
    separate_data("/Users/noyantoksoy/Downloads/data_merged_new.csv")
    # games_collected = 0
    # goal = 5 * 6000000
    # pudge_not_picked: list[dict] = []
    # match_id = 6579918509
    # no_saved = 1
    # while games_collected < goal:
    #     try:
    #         URL = f"https://api.opendota.com/api/publicMatches?less_than_match_id={match_id}"
    #         time.sleep(0.5)
    #         response_API = requests.get(URL)
    #         data = response_API.text
    #         parse_json = json.loads(data)
    #         pudge_not_picked += list(
    #             filter(lambda x: (x["game_mode"] in [1, 22]) and x["avg_mmr"] is not None, parse_json))
    #         match_id = match_id - 1000 if len(pudge_not_picked) == 0 else pudge_not_picked[-1]["match_id"]
    #         games_collected += len(pudge_not_picked)
    #         progress = (100 * games_collected) / goal
    #         print("%.3f" % progress, "%")
    #         if np.abs(progress - (no_saved * 10)) < 0.2:
    #             save_data(pudge_not_picked, match_id)
    #             no_saved += 1
    #     except Exception as e:
    #         print(match_id)
    #         match_id = match_id - 1000
    #         continue
    #
    # print(len(pudge_not_picked))
