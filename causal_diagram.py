import json
import requests
from pprint import pprint
import graphviz as gr

if __name__ == '__main__':
    g = gr.Digraph(format='png', name="causal_diagram")

    g.node("Selection of the Pudge hero")
    g.node("Game outcome")

    g.edge("Opponent’s hero pick", "Counter-pick performance")
    g.edge("Counter-pick performance", "Selection of the Pudge hero")
    g.edge("Counter-pick performance", "Game outcome")

    g.edge("Team diversity", "Selection of the Pudge hero")
    g.edge("Team diversity", "Game outcome")

    g.edge("Knowledge", "Skill level")
    g.edge("Skill level", "MMR")

    g.edge("MMR", "Selection of the Pudge hero")
    g.edge("MMR", "Game outcome")

    g.edge("Past experience with the hero", "Player's win-rate with the hero")
    g.edge("Player's win-rate with the hero", "Selection of the Pudge hero")
    g.edge("Player's win-rate with the hero", "Game outcome")
    g.view()
