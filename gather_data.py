import os
import random
import time
import pandas as pd
import requests
import json

from main import package_dir


def fetch_games_api(day_, month_, year_, URL_, all_games_, collection_error_):
    """
    Fetch the games older or equal to the specified dates and the SQL query embedded in the URL.

    :param day_:
    :param month_:
    :param year_:
    :param URL_: URL with the SQL query embedded in it
    :param all_games_: List of all games collected so far
    :param collection_error_:
    :return: Number of games collected
    """
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


def collect_games_api():
    """
    This funtion starts with a specified date and goes back in time in the specified intervals to make calls to the API
    and get a new set of games.
    """
    games_to_collect = 2 * 8000000  # This number is usually very large because there are a lot of duplicate games
    # returned by the API
    games_collected = 0
    day = 13
    month = 4
    year = 2022
    all_games = []
    collection_error = []
    while games_collected < games_to_collect:
        text_month = ""
        if month < 10:
            text_month = "0" + str(month)
        else:
            text_month = "" + str(month)
        URL_query = f"https://api.opendota.com/api/explorer?sql=SELECT%0Amatches.match_id%2C%0Amatches.start_time%2C%0Amatches.game_mode%2C%0Amatches.radiant_win%2C%0Aplayer_matches.account_id%2C%0Aplayer_matches.player_slot%2C%0Aplayer_matches.hero_id%2C%0Amatches.picks_bans%0AFROM%20matches%0AJOIN%20match_patch%20using(match_id)%0ARIGHT%20JOIN%20player_matches%20using(match_id)%0AWHERE%20TRUE%0AAND%20matches.start_time%20%3E%3D%20extract(epoch%20from%20timestamp%20%27{year}-{text_month}-{day}T18%3A26%3A47.482Z%27)%0AAND%20matches.game_mode%20IN%20(2%2C%2022)%0AORDER%20BY%20matches.match_id%20NULLS%20LAST%0ALIMIT%2012000"
        collected = fetch_games_api(day, text_month, year, URL_query, all_games, collection_error)
        games_collected += collected
        new_day = day - random.randrange(start=1, stop=2)
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
        time.sleep(1)
    new_collection_error = []
    fixed_collection_errors = map(lambda date: fetch_games_api(date[0], date[1], date[2],
                                                               f"https://api.opendota.com/api/explorer?sql=SELECT%0Amatches.match_id%2C%0Amatches.start_time%2C%0Amatches.game_mode%2C%0Amatches.radiant_win%2C%0Aplayer_matches.account_id%2C%0Aplayer_matches.player_slot%2C%0Aplayer_matches.hero_id%2C%0Amatches.picks_bans%0AFROM%20matches%0AJOIN%20match_patch%20using(match_id)%0ARIGHT%20JOIN%20player_matches%20using(match_id)%0AWHERE%20TRUE%0AAND%20matches.start_time%20%3E%3D%20extract(epoch%20from%20timestamp%20%27{date[2]}-{date[1]}-{date[0]}T18%3A26%3A47.482Z%27)%0AAND%20matches.game_mode%20IN%20(2%2C%2022)%0AORDER%20BY%20matches.match_id%20NULLS%20LAST%0ALIMIT%2012000",
                                                               all_games, new_collection_error), collection_error)
    print(len(new_collection_error), new_collection_error)
    df = pd.DataFrame(all_games)
    df.drop_duplicates(subset=["match_id", "start_time", "account_id"], keep="first", inplace=True, ignore_index=True)
    print(df.match_id.nunique())
    df.to_csv(os.path.join(package_dir, f"data_new_captains_mode_{day}_{month}_{year}.csv"))
