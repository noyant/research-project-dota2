import pandas
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import pandas as pd
import glob
import os


chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory": "/Users/noyantoksoy/Downloads/gather_data_treatment"}
chromeOptions.add_experimental_option("prefs", prefs)
PATH = "/Users/noyantoksoy/Downloads/chromedriver"

global driver
driver = webdriver.Chrome(executable_path=PATH, options=chromeOptions)


def fetch_games(day, month, year, URL):
    driver.get(URL)
    try:
        results = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "sc-cJSrbW"))
        )
        csv_link = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "CSV"))
        )
        setAttribute(csv_link, "download", f"data_500_{month}_{day}_{year}.csv")
        csv_link.click()
        time.sleep(0.5)
        rows = driver.find_element(by=By.XPATH, value="/html/body/div/div/div[2]/div/div[4]/span[2]")
        return int(rows.text.split(" ")[0])/10
    except Exception as e:
        print(e)
        return 0


def setAttribute(element, att_name, att_value):
    driver.execute_script("arguments[0].setAttribute(arguments[1], arguments[2]);",
                          element, att_name, att_value)


def merge_csv():
    files = os.path.join("/Users/noyantoksoy/Downloads/gather_data_treatment", "data*.csv")
    files = glob.glob(files)
    df = pd.concat(map(pd.read_csv, files), ignore_index=True)
    pre_process_csv(df, "/Users/noyantoksoy/Downloads/data_merged_treatment.csv")


def pre_process_csv_treatment(df: pandas.DataFrame):
    df.drop_duplicates(subset=["match_id", "start_time"],
                       keep="first", inplace=True, ignore_index=True)
    matches_found = 0
    for match_id in df["match_id"].tolist():
        URL = f"https://www.opendota.com/explorer?sql=SELECT%0Amatches.match_id%0AFROM%20matches%0ARIGHT%20JOIN%20player_matches%20using(match_id)%0AWHERE%20TRUE%0AAND%20matches.match_id%20%3D%20{match_id}%0AAND%20player_matches.hero_id%20%3D%2014%0AORDER%20BY%20matches.match_id%20NULLS%20LAST%0ALIMIT%20100&format="
        driver.get(URL)
        try:
            results = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "sc-cJSrbW"))
            )
            csv_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "CSV"))
            )
            rows = driver.find_element(by=By.XPATH, value="/html/body/div/div/div[2]/div/div[4]/span[2]")
            collect_match = True if int(rows.text.split(" ")[0]) == 1 else False
            if collect_match:
                time.sleep(0.5)
                MATCH_URL = f"https://www.opendota.com/explorer?sql=SELECT%0Amatches.match_id%2C%0Amatches.start_time%2C%0Amatches.game_mode%2C%0Aplayer_matches.account_id%2C%0Aplayer_matches.hero_id%2C%0Aplayer_matches.kills%2C%0Aplayer_matches.deaths%2C%0Aplayer_matches.assists%2C%0Aplayer_matches.gold_per_min%2C%0Aplayer_matches.xp_per_min%2C%0Aplayer_matches.gold_spent%2C%0Aplayer_matches.hero_damage%2C%0Aplayer_matches.tower_damage%2C%0Aplayer_matches.hero_healing%2C%0Aplayer_matches.level%2C%0Amatches.dire_score%2C%0Amatches.draft_timings%2C%0Amatches.picks_bans%2C%0Amatches.objectives%2C%0Amatches.radiant_gold_adv%2C%0Amatches.radiant_score%2C%0Amatches.radiant_win%2C%0Amatches.radiant_xp_adv%2C%0Aplayer_matches.account_id%2C%0Aplayer_matches.lane_pos%2C%0Aplayer_matches.lane%2C%0Aplayer_matches.lane_role%2C%0Aplayer_matches.net_worth%0AFROM%20matches%0AJOIN%20match_patch%20using(match_id)%0ARIGHT%20JOIN%20player_matches%20using(match_id)%0AWHERE%20TRUE%0AAND%20matches.match_id%20%3D%20{match_id}%0AORDER%20BY%20matches.match_id%20NULLS%20LAST%0ALIMIT%20100&format="
                driver.get(MATCH_URL)
                try:
                    results = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, "sc-cJSrbW"))
                    )
                    csv_link = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.LINK_TEXT, "CSV"))
                    )
                    setAttribute(csv_link, "download", f"data_{match_id}_{month}_{day}_{year}.csv")
                    time.sleep(0.5)
                    csv_link.click()
                    matches_found += 1
                except Exception as e:
                    print(e)
                    continue
            else:
                continue
        except Exception as e:
            print(e)
            continue

    return matches_found


def pre_process_csv(df: pandas.DataFrame, file_path):
    df.drop_duplicates(subset=["match_id", "account_id", "start_time"],
                       keep="first", inplace=True, ignore_index=True)
    # print(len(df.match_id.value_counts()[df.match_id.value_counts() < 10]))
    # for invalid in df.match_id.value_counts()[df.match_id.value_counts() < 10].index.values:
    #     df = df[df.match_id != invalid]
    print(df.match_id.nunique())
    df.to_csv(file_path)
    return df.match_id.nunique()


if __name__ == '__main__':
    games_to_collect = 25000
    games_collected = 0
    day = 21
    month = 5
    year = 2022
    # merge_csv()
    while games_collected < games_to_collect:
        text_month = ""
        if month < 10:
            text_month = "0" + str(month)
        else:
            text_month = "" + str(month)
        URL_treatment = f"https://www.opendota.com/explorer?sql=SELECT%0Amatches.match_id%2C%0Amatches.start_time%2C%0Amatches.game_mode%2C%0Aplayer_matches.account_id%2C%0Aplayer_matches.hero_id%2C%0Aplayer_matches.kills%2C%0Aplayer_matches.deaths%2C%0Aplayer_matches.assists%2C%0Aplayer_matches.gold_per_min%2C%0Aplayer_matches.xp_per_min%2C%0Aplayer_matches.gold_spent%2C%0Aplayer_matches.hero_damage%2C%0Aplayer_matches.tower_damage%2C%0Aplayer_matches.hero_healing%2C%0Aplayer_matches.level%2C%0Amatches.dire_score%2C%0Amatches.draft_timings%2C%0Amatches.picks_bans%2C%0Amatches.objectives%2C%0Amatches.radiant_gold_adv%2C%0Amatches.radiant_score%2C%0Amatches.radiant_win%2C%0Amatches.radiant_xp_adv%2C%0Aplayer_matches.account_id%2C%0Aplayer_matches.lane_pos%2C%0Aplayer_matches.lane%2C%0Aplayer_matches.lane_role%2C%0Aplayer_matches.net_worth%0AFROM%20matches%0ARIGHT%20JOIN%20player_matches%20using(match_id)%0AWHERE%20match_id%20IN%20(%0A%20%20%20%20SELECT%0A%20%20%20%20matches.match_id%0A%20%20%20%20FROM%20matches%0A%20%20%20%20RIGHT%20JOIN%20player_matches%20using(match_id)%0A%20%20%20%20WHERE%20TRUE%0A%20%20%20%20AND%20matches.start_time%20%3E%3D%20extract(epoch%20from%20timestamp%20%27{year}-{month}-{day}T15%3A21%3A53.222Z%27)%0A%20%20%20%20AND%20player_matches.hero_id%20%3D%2014%0A%20%20%20%20AND%20matches.game_mode%20%3C%3D%202%0A%20%20%20%20ORDER%20BY%20matches.match_id%20NULLS%20LAST%0A%20%20%20%20LIMIT%202000%0A)%0AAND%20matches.start_time%20%3E%3D%20extract(epoch%20from%20timestamp%20%27{year}-{month}-{day}T18%3A26%3A47.482Z%27)%0AAND%20matches.game_mode%20%3C%3D%202%0AORDER%20BY%20matches.match_id%20NULLS%20LAST%0ALIMIT%206000&format="
        collected = fetch_games(day, text_month, year, URL_treatment)
        games_collected += collected
        new_day = day - random.randrange(start=8, stop=20)
        if new_day > 0:
            day = new_day
        else:
            day = 31
            new_month = month - 1
            if new_month > 0:
                if new_month == 2:
                    day = 28
                month = new_month
            else:
                month = 12
                year = year - 1
        time.sleep(2)
    driver.quit()
