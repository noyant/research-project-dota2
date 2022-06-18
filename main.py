import pandas
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
from gather_data import collect_games_api

package_dir = os.path.dirname(os.path.abspath(__file__))
# Configurations for the chromedriver:
chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory": os.path.join(package_dir, "data/gather_data_captains_mode")}
chromeOptions.add_experimental_option("prefs", prefs)
PATH = "path_to_chromedriver"  # The path to the installed chromedriver needs to be placed here

global driver


# To initialize the driver:
# driver = webdriver.Chrome(executable_path=PATH, options=chromeOptions)


def fetch_games(day, month, year, URL, collection_error):
    """
    This function was previously used to retrieve games using selenium webdriver which automates the process of sending
    SQL queries and downloading csv files.
    This funtion is not used in the final version.

    :param day:
    :param month:
    :param year:
    :param URL:
    :param collection_error:
    :return: Number of games collected
    """
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
    """
    Helper function used by the fetch_games method.

    :param element:
    :param att_name:
    :param att_value:
    :return:
    """
    driver.execute_script("arguments[0].setAttribute(arguments[1], arguments[2]);",
                          element, att_name, att_value)


def merge_csv():
    """
    This method merges multiple csv files into a single csv
    """
    files = os.path.join(os.path.join(package_dir, "data/intermediate_saves"),
                         "data*.csv")  # The file path of the folder and the regex to match can be set here
    files = glob.glob(files)
    df = pd.concat(map(pd.read_csv, files), ignore_index=True)
    pre_process_csv(df, os.path.join(package_dir, "data/data_merged_captains_final.csv"))


def pre_process_csv(df: pandas.DataFrame, file_path):
    """
    Drops duplicates in a csv file

    :param df:
    :param file_path: The final merged csv is saved to this path
    :return: Number of unique matches
    """
    print(df.match_id.nunique())

    df.drop_duplicates(keep="first", inplace=True, ignore_index=True)

    print(df.match_id.nunique())
    df.to_csv(file_path)
    return df.match_id.nunique()


def get_pudge_win_rate(account_id, collection_error_extra_info):
    """
    Fetch win rates of a player with the Pudge hero.

    :param account_id:
    :param collection_error_extra_info:
    :return: the win rate
    """
    try:
        time.sleep(0.1)
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
    """
    Fetch KDA info of a player with the Pudge hero.

    :param account_id:
    :param collection_error_extra_info:
    :return: KDA
    """
    try:
        time.sleep(0.1)
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
    """
    Fetch MMR of a player.

    :param account_id:
    :param collection_error_extra_info:
    :return: MMR
    """
    try:
        time.sleep(0.1)
        response_API = requests.get(f"https://api.opendota.com/api/players/{account_id}")
        data = response_API.text
        parse_json = json.loads(data)
        return parse_json["mmr_estimate"]["estimate"] if len(
            parse_json["mmr_estimate"]) != 0 else random.randint(0,
                                                                 153)  # The range of the lowest rank in Dota, Herald 1
    except Exception as e:
        # traceback.print_exc()
        collection_error_extra_info.append(account_id)
        time.sleep(0.2)
        return -1


def get_counter_list(hero_name, hero_id):
    """
    Form the counter-pick list from the Dotabuff website, using selenium chromedriver.

    :param hero_name:
    :param hero_id:
    :return: Counter-pick values of a hero
    """
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
    """
    A wrapper function to go through the list of all heroes and collect their counter-pick information.
    """
    response_API = requests.get("https://api.opendota.com/api/heroes")
    data = response_API.text
    parse_json = json.loads(data)
    counter_pick_list = list(
        map(lambda hero: {hero["localized_name"].lower().replace(" ", "-").replace("'", ""): get_counter_list(
            hero["localized_name"].lower().replace(" ", "-").replace("'", ""),
            hero["id"])}, parse_json))
    with open(os.path.join(package_dir, "data/counter_picks.json"), "w") as fp:
        json.dump(counter_pick_list, fp)


def calculate_counter_pick_performance(current_pick, counter):
    """
    Helper function to return the counter-pick performance value.

    :param current_pick:
    :param counter:
    :return: The counter-pick performance
    """
    try:
        hero_name_current = list(filter(lambda hero: hero["id"] == current_pick, heroes))[0][
            "localized_name"].lower().replace(" ", "-").replace("'", "")
        hero_name_counter = list(filter(lambda hero: hero["id"] == counter, heroes))[0][
            "localized_name"].lower().replace(" ", "-").replace("'", "")
        return data_counters[hero_name_current][hero_name_counter]
    except Exception as e:
        return 0.0


def get_counter_pick_performance(draft_order, prev_draft):
    """
    This function calculates the counter-pick performance for each team, given the current draft ordering and the
    previous one.
    This calculation is made once per team and the score is assigned to all team members.

    :param draft_order:
    :param prev_draft:
    :return: counter-pick performance of the team
    """
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
    """
    Helper method to calculate the balance of a team. The higher the score, the more balanced the team.

    :param team_radiant:
    :return: team balance on a scale of 0 to 1.
    """
    team_radiant_carry_support_measure = list(map(lambda hero_id: carry_support_measures[
        list(filter(lambda hero: hero["id"] == hero_id, heroes))[0]["localized_name"].lower().replace(" ", "-").replace(
            "'", "")], team_radiant))
    mean = np.mean(team_radiant_carry_support_measure)
    return 1 - np.abs(mean - 0.6)


def get_team_balance(draft_order, prev_draft):
    """
    This function calculates the team balance for each team, given the current draft ordering and the
    previous one.
    This calculation is made once per team and the score is assigned to all team members.

    :param draft_order:
    :param prev_draft:
    :return: team balance measure
    """
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
    """
    Helper method to return the carry-support percentage of a hero.

    :param roles:
    :return: carry-support percentage
    """
    if "Carry" in roles and "Support" in roles:
        return 0.5
    elif "Carry" in roles:
        return 1.0
    elif "Support" in roles:
        return 0.0
    else:
        return 0.5


def form_carry_support_measure():
    """
    Wrapper method to form the list of carry-support measures per hero.
    """
    carry_support_dict = {}
    for hero in heroes:
        carry_support_dict[
            hero["localized_name"].lower().replace(" ", "-").replace("'", "")] = helper_carry_support_measure(
            hero["roles"])
    with open(os.path.join(package_dir, "data/carry_support.json", "w")) as fp:
        json.dump(carry_support_dict, fp)


def extra_information_helper(df_all_games, collection_error_win_rate_, collection_error_kda_, collection_error_mmr_):
    """
    Get all necessary information to form the confounding factor columns via additional API calls.

    :param df_all_games:
    :param collection_error_win_rate_:
    :param collection_error_kda_:
    :param collection_error_mmr_:
    :return: The dataframe with all the necessary information
    """
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
    """
    Wrapper method to from the collection error lists and pass it to the extra_information_helper.

    :param df_partial: Dataframe with missing columns, no confounding factor information
    :return: Dataframe with all necessary information
    """
    collection_error_win_rate = []
    collection_error_kda = []
    collection_error_mmr = []
    df = extra_information_helper(df_partial, collection_error_win_rate, collection_error_kda,
                                  collection_error_mmr)
    return df


def helper_update_counters(list_counters):
    """
    This was a helper method used to fix a problem with the counter-pick list.
    This method is no longer used in the final version because the counter-pick list is already fixed.

    :param list_counters: The faulty counter-pick list
    :return: Fixed counter-pick list
    """
    counter_dict = {}
    for val in list_counters:
        counter_dict[list(val.keys())[0]] = val[list(val.keys())[0]]
    return counter_dict


def fix_missing_values(df, retries, i):
    """
    Method used for recursively fixing the missing information due to collection errors.
    It stops execution and informs the user after 8 retries to avoid an infinite loop.

    :param df: Dataframe with missing values
    :param retries: Number of executions
    :param i: Counter used to identify the correct iteration of data gathering
    :return: Fixed dataframe
    """
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
        if i != -1:
            df.drop("picks_bans", inplace=True, axis=1)
            df.to_csv(
                os.path.join(package_dir, f"data/intermediate_saves/data_error_{len(df)}_with_extra_info_{i}.csv"))
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
        return fix_missing_values(df, retries, i)


def fix_files_collection_error():
    """
    A wrapper function that goes over a folder containing dataframes with missing values and makes calls to
    fix_missing_values.
    """
    files = os.path.join(os.path.join(package_dir, "data/intermediate_saves"), "data_error*.csv")
    files = glob.glob(files)
    print(len(files))
    for file in files:
        df_with_error = pd.read_csv(file)
        df_fixed = fix_missing_values(df_with_error, 0, -1)
        if df_fixed is not None:
            print("Fixed!")
            df_fixed.to_csv(file)
        else:
            print("Still couldn't collect all data, file name: ", file)


def get_additional_info_all_games():
    """
    The function that collects additional information from a dataset with all games collected.
    These information are collected in intervals with intermediary saves because the full collection takes a very
    long time.
    """
    # This csv file with all games are not included in the repository due to its size.
    # It can be downloaded through this link:
    # https://drive.google.com/file/d/1C-dGSLMRMeJqqQFGHYYVDZQXQpvYKGKC/view?usp=sharing
    df_all = pd.read_csv(os.path.join(package_dir, "data/data_new_captains_mode_1_11_2021.csv"))
    interval = 500  # Collect additional information in batches of 500 matches
    left_at = 0  # This variable can be set to the number of intermediary saves collected
    # if the execution is stopped and restarted later
    for i in range(left_at * 500, len(df_all), interval):
        start_time = time.time()
        df_iter = df_all[i:i + interval]
        df_extra_info = fix_missing_values(get_extra_information(df_iter), 0, i)
        if df_extra_info is not None:
            df_extra_info.drop("picks_bans", inplace=True, axis=1)
            df_extra_info.to_csv(
                os.path.join(package_dir, f"intermediate_saves/data_{len(df_iter)}_with_extra_info_{i}.csv"))
        end_time = time.time()
        print("Execution time: ", end_time - start_time)
        time.sleep(2)


if __name__ == '__main__':
    # These two methods can be called to form the counter_pick and carry_support json files:
    # form_counter_pick_list()
    # form_carry_support_measure()

    # This method can be called to recursively fix all the collection errors:
    # fix_files_collection_error()

    with open(os.path.join(package_dir, "data/counter_picks_updated.json"), "rb") as fp:
        data_counters: list[dict] = json.load(fp)

    with open(os.path.join(package_dir, "data/heroes.json"), "rb") as fp:
        heroes = json.load(fp)

    with open(os.path.join(package_dir, "data/carry_support.json"), "rb") as fp:
        carry_support_measures = json.load(fp)

    # This method can be called to get additional information, confounding factor columns:
    # get_additional_info_all_games()

    # This method is to merge multiple CSVs
    # merge_csv()

    # This method can be called to retrieve match information from the API, using SQL queries:
    # collect_games_api()

    # If chromedriver is used:
    # driver.quit()
