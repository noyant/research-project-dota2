import json
import requests
from pprint import pprint
import csv
import time
from main import merge_csv

if __name__ == '__main__':
    # merge_csv()
    base_path = "/Users/noyantoksoy/Downloads/gather_data_control_"
    games_collected = 0
    goal = 5*60000000
    pudge_not_picked: list[dict] = []
    match_id = 6584503313
    while games_collected < goal:
        try:
            URL = f"https://api.opendota.com/api/publicMatches?less_than_match_id={match_id}"
            time.sleep(0.5)
            response_API = requests.get(URL)
            data = response_API.text
            parse_json = json.loads(data)
            pudge_not_picked += list(
                filter(lambda x: (x["game_mode"] in [1, 22]) and x["avg_mmr"] is not None and (
                        "14" not in x["dire_team"].split(",") and "14" not in x["radiant_team"].split(",")), parse_json))
            match_id = match_id - 1000 if len(pudge_not_picked) == 0 else pudge_not_picked[-1]["match_id"]
            games_collected += len(pudge_not_picked)
            print(games_collected, "/", 5*60000000)
        except Exception as e:
            print(match_id)
            match_id = match_id - 1000
            continue

    print(len(pudge_not_picked))

    with open(base_path + f"/data_{len(pudge_not_picked)}_{match_id}.csv", "w", newline="") as f:
        header = "match_id,match_seq_num,radiant_win,start_time,duration,avg_mmr,num_mmr,lobby_type,game_mode," \
                 "avg_rank_tier," \
                 "num_rank_tier,cluster,radiant_team,dire_team".split(",")
        cw = csv.DictWriter(f, header)
        cw.writeheader()
        cw.writerows(pudge_not_picked)
    pprint(len(pudge_not_picked))


