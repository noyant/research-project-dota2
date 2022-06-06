import json
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


def gather_data(goal):
    games_collected = 0
    all_games: list[dict] = []
    match_id = 6590000000
    no_saved = 1
    not_collected = []
    while games_collected < goal:
        try:
            URL = f"https://api.opendota.com/api/publicMatches?less_than_match_id={match_id}"
            time.sleep(0.5)
            response_API = requests.get(URL)
            data = response_API.text
            parse_json = json.loads(data)
            all_games += list(
                filter(lambda x: (x["game_mode"] in [1, 22]) and (x["num_mmr"] == 10) and check_match(x["match_id"],
                                                                                                      not_collected),
                       parse_json))
            match_id = match_id - 1000 if len(all_games) == 0 else all_games[-1]["match_id"]
            games_collected += len(all_games)
            progress = (100 * games_collected) / goal
            # print("%.3f" % progress, "%")
            if np.abs(progress - (no_saved * 5)) < 1.5:
                print(len(all_games))
                save_data(all_games, match_id)
                no_saved += 1
        except Exception as e:
            not_collected.append(match_id)
            match_id = match_id - 1000
            continue
    print(not_collected)
    print(len(all_games))


def check_match(match_id, not_collected, data_all_player_info, start_time):
    URL = f"https://api.opendota.com/api/matches/{match_id}"
    time.sleep(0.1)
    try:
        response_API = requests.get(URL)
        data = response_API.text
        parse_json = json.loads(data)
        players = parse_json["players"]
        valid_players = len(list(filter(lambda player: player["account_id"] is not None, players)))
        if valid_players == 10:
            data_all_player_info.append(parse_json)
        if len(data_all_player_info) % 20 == 0:
            print(len(data_all_player_info), "/", 300000)
        return valid_players == 10
    except Exception as e:
        time.sleep(0.5)
        not_collected.append(match_id)
        return False


def prune_csv(file_path):
    df = pd.read_csv(file_path)
    not_collected = []
    data_all_player_info = []
    start_time = time.thread_time()
    mask = df.match_id.apply(lambda x: check_match(x, not_collected, data_all_player_info, start_time))
    df = df[mask]
    df_all_player_info = pd.DataFrame(data_all_player_info)
    print(df.match_id.nunique())
    print(len(not_collected), not_collected)
    df.to_csv("/Users/noyantoksoy/Downloads/data_with_player_info.csv")
    df_all_player_info.to_csv("/Users/noyantoksoy/Downloads/data_extended_with_player_info.csv")


if __name__ == '__main__':
    base_path = "/Users/noyantoksoy/Downloads/gather_data_all_player"
    process = 3
    if process == 0:
        gather_data(goal=60000)
    elif process == 1:
        separate_data("/Users/noyantoksoy/Downloads/data_merged_new.csv")
    elif process == 2:
        merge_csv()
    elif process == 3:
        prune_csv("/Users/noyantoksoy/Downloads/data_merged_new.csv")
