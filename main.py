import json
import requests
from pprint import pprint

if __name__ == '__main__':
    response_API = requests.get('https://api.opendota.com/api/proPlayers')
    data = response_API.text
    parse_json = json.loads(data)
    pprint(parse_json)
