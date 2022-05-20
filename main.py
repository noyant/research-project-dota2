import json
import requests
from pprint import pprint
from selenium import webdriver

PATH = "/Users/noyantoksoy/Downloads/chromedriver"

if __name__ == '__main__':
    driver = webdriver.Chrome(PATH)
    driver.get("https://www.opendota.com/explorer")

    # response_API = requests.get('https://api.opendota.com/api/heroes')     # Omniknight
    # # response_API = requests.get('https://api.opendota.com/api/heroes/14/matches')   # Pudge
    # data = response_API.text
    # parse_json = json.loads(data)
    # pprint("")

    # g = gr.Digraph(format='png')
    #
    # g.node("Selection of the Pudge hero")
    # g.node("Game outcome")
    #
    # g.edge("Opponent’s hero pick", "Selection of the Pudge hero")
    # g.edge("Opponent’s hero pick", "Game outcome")
    # g.edge("Opponent’s hero pick", "Team building")
    #
    # g.edge("Team building", "Selection of the Pudge hero")
    # g.edge("Team building", "Game outcome")
    #
    # g.edge("Knowledge", "Skill level")
    # g.edge("Skill level", "MMR")
    #
    # g.edge("MMR", "Selection of the Pudge hero")
    # g.edge("MMR", "Game outcome")
    #
    # g.edge("Strategy of the player", "Selection of the Pudge hero")
    # g.edge("Strategy of the player", "Game outcome")
    #
    # g.edge("Past experience with the hero", "Selection of the Pudge hero")
    # g.edge("Past experience with the hero", "Game outcome")
    # g.view()