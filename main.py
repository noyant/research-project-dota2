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
prefs = {"download.default_directory": "/Users/noyantoksoy/Downloads/gather_data"}
chromeOptions.add_experimental_option("prefs", prefs)
PATH = "/Users/noyantoksoy/Downloads/chromedriver"

global driver
# driver = webdriver.Chrome(executable_path=PATH, options=chromeOptions)


def fetch_games(day, month, year):
    URL = f"https://www.opendota.com/explorer?sql=SELECT%0Amatches.match_id%2C%0Amatches.start_time%2C%0Amatches.game_mode%2C%0Aplayer_matches.account_id%2C%0Aplayer_matches.hero_id%2C%0Aplayer_matches.kills%2C%0Aplayer_matches.deaths%2C%0Aplayer_matches.assists%2C%0Aplayer_matches.gold_per_min%2C%0Aplayer_matches.xp_per_min%2C%0Aplayer_matches.gold_spent%2C%0Aplayer_matches.hero_damage%2C%0Aplayer_matches.tower_damage%2C%0Aplayer_matches.hero_healing%2C%0Aplayer_matches.level%2C%0Amatches.dire_score%2C%0Amatches.draft_timings%2C%0Amatches.picks_bans%2C%0Amatches.objectives%2C%0Amatches.radiant_gold_adv%2C%0Amatches.radiant_score%2C%0Amatches.radiant_win%2C%0Amatches.radiant_xp_adv%2C%0Aplayer_matches.account_id%2C%0Aplayer_matches.lane_pos%2C%0Aplayer_matches.lane%2C%0Aplayer_matches.lane_role%2C%0Aplayer_matches.net_worth%0AFROM%20matches%0AJOIN%20match_patch%20using(match_id)%0ARIGHT%20JOIN%20player_matches%20using(match_id)%0AWHERE%20TRUE%0AAND%20matches.start_time%20%3E%3D%20extract(epoch%20from%20timestamp%20%27{year}-{month}-{day}T18%3A26%3A47.482Z%27)%0AAND%20matches.game_mode%20%3C%3D%202%0AAND%20player_matches.hero_id%20!%3D%2014%0AORDER%20BY%20matches.match_id%20NULLS%20LAST%0ALIMIT%205000&format="
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
        time.sleep(2)
        file_path = f"/Users/noyantoksoy/Downloads/gather_data/data_500_{month}_{day}_{year}.csv"
        df = pd.read_csv(file_path)
        return pre_process_csv(df, file_path)
    except Exception as e:
        print(e)
        return 0


def setAttribute(element, att_name, att_value):
    driver.execute_script("arguments[0].setAttribute(arguments[1], arguments[2]);",
                          element, att_name, att_value)


def merge_csv():
    files = os.path.join("/Users/noyantoksoy/Downloads/merge", "data*.csv")
    files = glob.glob(files)
    df = pd.concat(map(pd.read_csv, files), ignore_index=True)
    pre_process_csv(df, "/Users/noyantoksoy/Downloads/data_merged_final1.csv")


def pre_process_csv(df: pandas.DataFrame, file_path):
    print(df.match_id.nunique())
    df.drop_duplicates(subset=["match_id", "account_id", "start_time"],
                       keep="first", inplace=True, ignore_index=True)
    print(len(df.match_id.value_counts()[df.match_id.value_counts() < 10]))
    for invalid in df.match_id.value_counts()[df.match_id.value_counts() < 10].index.values:
        df = df[df.match_id != invalid]
    print(df.match_id.nunique())
    df.to_csv(file_path)
    return df.match_id.nunique()


if __name__ == '__main__':
    games_to_collect = 25000
    games_collected = 0
    day = 15
    month = 8
    year = 2021
    merge_csv()
    # while games_collected < games_to_collect:
    #     text_month = ""
    #     if month < 10:
    #         text_month = "0" + str(month)
    #     else:
    #         text_month = "" + str(month)
    #     collected = fetch_games(day, text_month, year)
    #     games_collected += collected
    #     new_day = day - random.randrange(start=1, stop=4)
    #     if new_day > 0:
    #         day = new_day
    #     else:
    #         day = 31
    #         new_month = month - 1
    #         if new_month > 0:
    #             month = new_month
    #         else:
    #             month = 12
    #             year = year - 1
    #     time.sleep(2)
    # driver.quit()
