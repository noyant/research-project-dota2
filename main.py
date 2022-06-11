import pandas
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from functools import reduce
import time
import random
import ast
import pandas as pd
import numpy as np
import traceback
import requests
import json
import glob
import os
from pprint import pprint

chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory": "/Users/noyantoksoy/Downloads/gather_data_captains_mode"}
chromeOptions.add_experimental_option("prefs", prefs)
PATH = "/Users/noyantoksoy/Downloads/chromedriver"

global driver


# driver = webdriver.Chrome(executable_path=PATH, options=chromeOptions)


def fetch_games(day, month, year, URL, collection_error):
    driver.get(URL)
    try:
        results = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "sc-cJSrbW"))
        )
        csv_link = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "CSV"))
        )
        rows = driver.find_element(by=By.XPATH, value="/html/body/div/div/div[2]/div/div[4]/span[2]")
        collected_games = int(int(rows.text.split(" ")[0]) / 10)
        setAttribute(csv_link, "download", f"data_{collected_games}_{month}_{day}_{year}.csv")
        time.sleep(1.5)
        csv_link.click()
        return collected_games
    except Exception as e:
        collection_error.append([day, month, year])
        return 0


def setAttribute(element, att_name, att_value):
    driver.execute_script("arguments[0].setAttribute(arguments[1], arguments[2]);",
                          element, att_name, att_value)


def merge_csv():
    files = os.path.join("/Users/noyantoksoy/Downloads/gather_data_captains_mode", "data*.csv")
    files = glob.glob(files)
    df = pd.concat(map(pd.read_csv, files), ignore_index=True)
    pre_process_csv(df, "/Users/noyantoksoy/Downloads/data_merged_captains_mode.csv")


def pre_process_csv(df: pandas.DataFrame, file_path):
    print(df.match_id.nunique())

    df.drop_duplicates(keep="first", inplace=True, ignore_index=True)
    # print(len(df.match_id.value_counts()[df.match_id.value_counts() < 10]))
    # for invalid in df.match_id.value_counts()[df.match_id.value_counts() < 10].index.values:
    #     df = df[df.match_id != invalid]
    print(df.match_id.nunique())
    df.to_csv(file_path)
    return df.match_id.nunique()


def fetch_games_api(day_, month_, year_, URL_, all_games_, collection_error_):
    try:
        time.sleep(0.5)
        response_API = requests.get(URL_)
        data = response_API.text
        parse_json = json.loads(data)
        all_games_ += list(parse_json["rows"])
        return int(len(all_games_) / 10)
    except Exception as e:
        collection_error_.append([day_, month_, year_])
        # traceback.print_exc()
        return 0


def get_pudge_win_rate(account_id, collection_error_extra_info):
    try:
        time.sleep(0.2)
        response_API = requests.get(f"https://api.opendota.com/api/players/{account_id}/heroes")
        data = response_API.text
        parse_json = json.loads(data)
        hero_stats = list(filter(lambda hero: hero["hero_id"] == "14", parse_json))[0]
        return np.round(hero_stats["win"] / hero_stats["games"], 4) if hero_stats["games"] > 15 else 0.4787 - (
                hero_stats["games"] - hero_stats["win"]) / 100
    except Exception as e:
        # traceback.print_exc()
        collection_error_extra_info.append(account_id)
        time.sleep(0.2)
        return -1


def get_pudge_kda(account_id, collection_error_extra_info):
    try:
        time.sleep(0.2)
        response_API = requests.get(f"https://api.opendota.com/api/players/{account_id}/totals?hero_id=14")
        data = response_API.text
        parse_json = json.loads(data)
        kda_stat = list(filter(lambda stat: stat["field"] == "kda", parse_json))[0]
        return np.round(kda_stat["sum"] / kda_stat["n"], 4) if kda_stat["n"] > 15 else min(2.2775, np.round(
            kda_stat["sum"] / kda_stat["n"], 4)) if kda_stat["n"] != 0.0 else 2.2775
    except Exception as e:
        # traceback.print_exc()
        collection_error_extra_info.append(account_id)
        time.sleep(0.2)
        return -1


def get_mmr(account_id, collection_error_extra_info):
    try:
        time.sleep(0.2)
        response_API = requests.get(f"https://api.opendota.com/api/players/{account_id}")
        data = response_API.text
        parse_json = json.loads(data)
        return parse_json["mmr_estimate"]["estimate"]
    except Exception as e:
        # traceback.print_exc()
        collection_error_extra_info.append(account_id)
        time.sleep(0.2)
        return -1


def get_counter_list(hero_name, hero_id):
    # time.sleep(0.1)
    driver.get(f"https://www.dotabuff.com/heroes/{hero_name}/counters")
    try:
        wait = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div[2]/div[2]/div[3]/div[4]/section[3]/article/table/tbody"))
        )
        time.sleep(0.1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        rows = len(driver.find_elements(by=By.XPATH,
                                        value="/html/body/div[2]/div[2]/div[3]/div[4]/section[3]/article/table/tbody/tr"))
        counter_values = []
        for row in range(1, rows):
            hero_name_ = ""
            disadvantage = 0.0
            for col in range(2, 4):
                wait = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located(
                        (By.XPATH,
                         f"/html/body/div[2]/div[2]/div[3]/div[4]/section[3]/article/table/tbody/tr[{str(row)}]/td[{str(col)}]"))
                )
                value = driver.find_element(by=By.XPATH,
                                            value=f"/html/body/div[2]/div[2]/div[3]/div[4]/section[3]/article/table/tbody/tr[{str(row)}]/td[{str(col)}]").text
                if value == "":
                    print(hero_id, hero_name, row, col)
                if col == 2:
                    hero_name_ = value.lower().replace(" ", "-").replace("'", "")
                elif col == 3:
                    if value != "":
                        disadvantage = float(value.split("%")[0])
            counter_values.append({hero_name_: disadvantage})
        return counter_values
    except Exception as e:
        print("Error: ", hero_id, hero_name)
        # traceback.print_exc()
        return []


def form_counter_pick_list():
    response_API = requests.get("https://api.opendota.com/api/heroes")
    data = response_API.text
    parse_json = json.loads(data)
    counter_pick_list = list(
        map(lambda hero: {hero["localized_name"].lower().replace(" ", "-").replace("'", ""): get_counter_list(
            hero["localized_name"].lower().replace(" ", "-").replace("'", ""),
            hero["id"])}, parse_json))
    with open("/Users/noyantoksoy/Documents/research-project-dota2/data/counter_picks.json", "w") as fp:
        json.dump(counter_pick_list, fp)


def calculate_counter_pick_performance(current_pick, counter):
    try:
        hero_name_current = list(filter(lambda hero: hero["id"] == current_pick, heroes))[0][
            "localized_name"].lower().replace(" ", "-").replace("'", "")
        hero_name_counter = list(filter(lambda hero: hero["id"] == counter, heroes))[0][
            "localized_name"].lower().replace(" ", "-").replace("'", "")
        return data_counters[hero_name_current][hero_name_counter]
    except Exception as e:
        return 0.0


def get_counter_pick_performance(draft_order, prev_draft):
    if prev_draft[1] not in [0, 5]:
        prev_draft[1] = (prev_draft[1] + 1) % 10
        return prev_draft[0]
    elif prev_draft[1] == -1:  # Pudge is selected, counter-pick performance won't be updated
        return prev_draft[0]
    else:
        draft_order_list = ast.literal_eval(draft_order)
        draft_order_list = list(filter(lambda x: x["is_pick"] is True, draft_order_list))
        if prev_draft[1] == 0:
            counter_performance_radiant = []
            prev_pick_team = -1
            current_pick = -1
            for pick in draft_order_list:
                # 0 -> radiant
                # 1 -> dire
                if pick["hero_id"] == 14:  # Pudge is selected, the rest of the counter-picks should be discarded
                    prev_draft[1] = -1
                    return prev_draft[0]
                if prev_pick_team == -1:
                    prev_pick_team = int(pick["team"])
                    current_pick = int(pick["hero_id"])
                elif prev_pick_team == pick["team"]:
                    current_pick = int(pick["hero_id"])
                else:
                    counter = int(pick["hero_id"])
                    countered_by = int(pick["team"])
                    if countered_by == 0:
                        counter_performance_radiant.append(calculate_counter_pick_performance(current_pick, counter))
                    prev_pick_team = int(pick["team"])
                    current_pick = int(pick["hero_id"])
            prev_draft[0] = np.round(sum(counter_performance_radiant), 4)
            prev_draft[1] = (prev_draft[1] + 1) % 10
            return prev_draft[0]
        if prev_draft[1] == 5:
            counter_performance_dire = []
            prev_pick_team = -1
            current_pick = -1
            for pick in draft_order_list:
                # 0 -> radiant
                # 1 -> dire
                if pick["hero_id"] == 14:  # Pudge is selected, the rest of the counter-picks should be discarded
                    prev_draft[1] = -1
                    return prev_draft[0]
                if prev_pick_team == -1:
                    prev_pick_team = int(pick["team"])
                    current_pick = int(pick["hero_id"])
                elif prev_pick_team == pick["team"]:
                    current_pick = int(pick["hero_id"])
                else:
                    counter = int(pick["hero_id"])
                    countered_by = int(pick["team"])
                    if countered_by == 1:
                        counter_performance_dire.append(calculate_counter_pick_performance(current_pick, counter))
                    prev_pick_team = int(pick["team"])
                    current_pick = int(pick["hero_id"])
            prev_draft[0] = np.round(sum(counter_performance_dire), 4)
            prev_draft[1] = (prev_draft[1] + 1) % 10
            return prev_draft[0]


def calculate_balance(team_radiant):
    team_radiant_carry_support_measure = list(map(lambda hero_id: carry_support_measures[
        list(filter(lambda hero: hero["id"] == hero_id, heroes))[0]["localized_name"].lower().replace(" ", "-").replace(
            "'", "")], team_radiant))
    mean = np.mean(team_radiant_carry_support_measure)
    return 1 - np.abs(mean - 0.6)


def get_team_balance(draft_order, prev_draft):
    if prev_draft[1] not in [0, 5]:
        prev_draft[1] = (prev_draft[1] + 1) % 10
        return prev_draft[0]
    elif prev_draft[1] == -1:  # Pudge is selected, team balance won't be updated
        return prev_draft[0]
    else:
        draft_order_list = ast.literal_eval(draft_order)
        if prev_draft[1] == 0:
            draft_order_list_radiant = list(filter(lambda x: x["is_pick"] is True and x["team"] == 0, draft_order_list))
            team_radiant = []
            for pick in draft_order_list_radiant:
                # 0 -> radiant
                # 1 -> dire
                if pick["hero_id"] == 14:  # Pudge is selected, the rest of the counter-picks should be discarded
                    prev_draft[1] = -1
                    return prev_draft[0]
                else:
                    team_radiant.append(pick["hero_id"])
            team_balance_radiant = calculate_balance(team_radiant)
            prev_draft[0] = np.round(team_balance_radiant, 4)
            prev_draft[1] = (prev_draft[1] + 1) % 10
            return prev_draft[0]
        if prev_draft[1] == 5:
            draft_order_list_dire = list(filter(lambda x: x["is_pick"] is True and x["team"] == 1, draft_order_list))
            team_dire = []
            for pick in draft_order_list_dire:
                # 0 -> radiant
                # 1 -> dire
                if pick["hero_id"] == 14:  # Pudge is selected, the rest of the counter-picks should be discarded
                    prev_draft[1] = -1
                    return prev_draft[0]
                else:
                    team_dire.append(pick["hero_id"])
            team_balance_radiant = calculate_balance(team_dire)
            prev_draft[0] = np.round(team_balance_radiant, 4)
            prev_draft[1] = (prev_draft[1] + 1) % 10
            return prev_draft[0]


def helper_carry_support_measure(roles):
    if "Carry" in roles and "Support" in roles:
        return 0.5
    elif "Carry" in roles:
        return 1.0
    elif "Support" in roles:
        return 0.0
    else:
        return 0.5


def form_carry_support_measure():
    carry_support_dict = {}
    for hero in heroes:
        carry_support_dict[
            hero["localized_name"].lower().replace(" ", "-").replace("'", "")] = helper_carry_support_measure(
            hero["roles"])
    with open("/Users/noyantoksoy/Documents/research-project-dota2/data/carry_support.json", "w") as fp:
        json.dump(carry_support_dict, fp)


def extra_information_helper(df_all_games, collection_error_win_rate_, collection_error_kda_, collection_error_mmr_):
    df_all_games = df_all_games.assign(
        pudge_win_rate=lambda x: list(
            map(lambda y: get_pudge_win_rate(y, collection_error_win_rate_), list(x["account_id"].values))))

    df_all_games = df_all_games.assign(
        pudge_kda=lambda x: list(
            map(lambda y: get_pudge_kda(y, collection_error_kda_), list(x["account_id"].values))))

    df_all_games = df_all_games.assign(
        mmr_estimate=lambda x: list(
            map(lambda y: get_mmr(y, collection_error_mmr_), list(x["account_id"].values))))

    prev_draft = [0.0, 0]
    df_all_games = df_all_games.assign(
        counter_performance=lambda x: list(
            map(lambda y: get_counter_pick_performance(y, prev_draft), list(x["picks_bans"].values))))

    prev_draft = [0.0, 0]
    df_all_games = df_all_games.assign(
        team_balance=lambda x: list(
            map(lambda y: get_team_balance(y, prev_draft), list(x["picks_bans"].values))))

    return df_all_games


def get_extra_information(df_partial):
    collection_error_win_rate = []
    collection_error_kda = []
    collection_error_mmr = []
    df = extra_information_helper(df_partial, collection_error_win_rate, collection_error_kda,
                                  collection_error_mmr)

    # print("Errors in win-rate: ", len(collection_error_win_rate))
    # print("Errors in kda: ", len(collection_error_kda))
    # print("Errors in mmr: ", len(collection_error_mmr))

    return df


def helper_update_counters(list_counters):
    counter_dict = {}
    for val in list_counters:
        counter_dict[list(val.keys())[0]] = val[list(val.keys())[0]]
    return counter_dict


def fix_missing_values(df, retries):

    missing_win_rate_mask = df.pudge_win_rate.apply(lambda x: -1.0 == x)
    missing_kda_mask = df.pudge_kda.apply(lambda x: -1.0 == x)
    missing_mmr_mask = df.mmr_estimate.apply(lambda x: -1.0 == x)

    df_missing_win_rate = df[missing_win_rate_mask]
    df_missing_kda = df[missing_kda_mask]
    df_missing_mmr = df[missing_mmr_mask]

    if len(df_missing_win_rate) + len(df_missing_kda) + len(df_missing_mmr) == 0:
        return df
    elif retries > 8:
        print("Can't fix certain errors")
        print("Errors in win-rate: ", len(df_missing_win_rate))
        print("Errors in kda: ", len(df_missing_kda))
        print("Errors in mmr: ", len(df_missing_mmr))
        df.drop("picks_bans", inplace=True, axis=1)
        df.to_csv(
            f"/Users/noyantoksoy/Downloads/intermediate_saves/data_error_{len(df)}_with_extra_info_{i}.csv")
        return None
    else:
        collection_error_win_rate = []
        collection_error_kda = []
        collection_error_mmr = []

        df.loc[df_missing_win_rate.index, "pudge_win_rate"] = list(
            map(lambda account: get_pudge_win_rate(account, collection_error_win_rate),
                df_missing_win_rate["account_id"].values))

        df.loc[df_missing_kda.index, "pudge_kda"] = list(
            map(lambda account: get_pudge_kda(account, collection_error_kda),
                df_missing_kda["account_id"].values))

        df.loc[df_missing_mmr.index, "mmr_estimate"] = list(
            map(lambda account: get_mmr(account, collection_error_mmr),
                df_missing_mmr["account_id"].values))

        print("Errors in win-rate: ", len(df_missing_win_rate))
        print("Errors in kda: ", len(df_missing_kda))
        print("Errors in mmr: ", len(df_missing_mmr))
        time.sleep(2)
        retries += 1
        return fix_missing_values(df, retries)


if __name__ == '__main__':
    # form_counter_pick_list()
    # form_carry_support_measure()
    # package_dir = os.path.dirname(os.path.abspath(__file__))
    # print(package_dir)

    with open('/Users/noyantoksoy/Documents/research-project-dota2/data/counter_picks_updated.json', 'rb') as fp:
        data_counters: list[dict] = json.load(fp)

    with open('/Users/noyantoksoy/Documents/research-project-dota2/data/heroes.json', 'rb') as fp:
        heroes = json.load(fp)

    with open('/Users/noyantoksoy/Documents/research-project-dota2/data/carry_support.json', 'rb') as fp:
        carry_support_measures = json.load(fp)

    df_all = pd.read_csv("/Users/noyantoksoy/Downloads/data_new_captains_mode_1_11_2021.csv")
    df_iter = None
    interval = 500
    start_time = time.time()
    for i in range(45*500, len(df_all), interval):
        df_iter = df_all[i:i + interval]
        df_extra_info = fix_missing_values(get_extra_information(df_iter), 0)
        if df_extra_info is not None:
            df_extra_info.drop("picks_bans", inplace=True, axis=1)
            df_extra_info.to_csv(
                f"/Users/noyantoksoy/Downloads/intermediate_saves/data_{len(df_iter)}_with_extra_info_{i}.csv")
        end_time = time.time()
        print("Execution time: ", end_time - start_time)
        time.sleep(5)

    # merge_csv()

    # games_to_collect = 2 * 8000000
    # games_collected = 0
    # day = 13
    # month = 4
    # year = 2022
    # all_games = []
    # collection_error = []
    # while games_collected < games_to_collect:
    #     text_month = ""
    #     if month < 10:
    #         text_month = "0" + str(month)
    #     else:
    #         text_month = "" + str(month)
    #     URL_query = f"https://api.opendota.com/api/explorer?sql=SELECT%0Amatches.match_id%2C%0Amatches.start_time%2C%0Amatches.game_mode%2C%0Amatches.radiant_win%2C%0Aplayer_matches.account_id%2C%0Aplayer_matches.player_slot%2C%0Aplayer_matches.hero_id%2C%0Amatches.picks_bans%0AFROM%20matches%0AJOIN%20match_patch%20using(match_id)%0ARIGHT%20JOIN%20player_matches%20using(match_id)%0AWHERE%20TRUE%0AAND%20matches.start_time%20%3E%3D%20extract(epoch%20from%20timestamp%20%27{year}-{text_month}-{day}T18%3A26%3A47.482Z%27)%0AAND%20matches.game_mode%20IN%20(2%2C%2022)%0AORDER%20BY%20matches.match_id%20NULLS%20LAST%0ALIMIT%2012000"
    #     collected = fetch_games_api(day, text_month, year, URL_query, all_games, collection_error)
    #     games_collected += collected
    #     new_day = day - random.randrange(start=1, stop=2)
    #     if new_day > 0:
    #         day = new_day
    #     else:
    #         day = 31
    #         new_month = month - 1
    #         if new_month > 0:
    #             if new_month == 2:
    #                 day = 28
    #             month = new_month
    #         else:
    #             month = 12
    #             year = year - 1
    #     time.sleep(1)
    # new_collection_error = []
    # fixed_collection_errors = map(lambda date: fetch_games_api(date[0], date[1], date[2], f"https://api.opendota.com/api/explorer?sql=SELECT%0Amatches.match_id%2C%0Amatches.start_time%2C%0Amatches.game_mode%2C%0Amatches.radiant_win%2C%0Aplayer_matches.account_id%2C%0Aplayer_matches.player_slot%2C%0Aplayer_matches.hero_id%2C%0Amatches.picks_bans%0AFROM%20matches%0AJOIN%20match_patch%20using(match_id)%0ARIGHT%20JOIN%20player_matches%20using(match_id)%0AWHERE%20TRUE%0AAND%20matches.start_time%20%3E%3D%20extract(epoch%20from%20timestamp%20%27{date[2]}-{date[1]}-{date[0]}T18%3A26%3A47.482Z%27)%0AAND%20matches.game_mode%20IN%20(2%2C%2022)%0AORDER%20BY%20matches.match_id%20NULLS%20LAST%0ALIMIT%2012000", all_games, new_collection_error), collection_error)
    # print(len(new_collection_error), new_collection_error)
    # df = pd.DataFrame(all_games)
    # df.drop_duplicates(subset=["match_id", "start_time", "account_id"], keep="first", inplace=True, ignore_index=True)
    # print(df.match_id.nunique())
    # df.to_csv(f"/Users/noyantoksoy/Downloads/data_new_captains_mode_{day}_{month}_{year}.csv")
    # driver.quit()
