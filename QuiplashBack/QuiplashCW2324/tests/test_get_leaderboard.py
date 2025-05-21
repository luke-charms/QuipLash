import unittest
import json
import requests 

local_settings = json.load(open('local.settings.json'))
db_URI = local_settings['Values']['db_URI']
db_id = local_settings['Values']['Database']
db_key = local_settings['Values']['db_key']
players_cont = local_settings['Values']['PlayerContainer']
prompts_cont = local_settings['Values']['PromptContainer']

class TestFunction(unittest.TestCase):
   PUBLIC_URL="https://comp3207quiplashcw-lah1u21-2324.azurewebsites.net/api/utils/leaderboard?code=9Gh0Kvzzl4fLHMJZVaNiRQtzRMqb6v6Um1jrwoMRIp2DAzFu9KfaWA=="
   TEST_URL = PUBLIC_URL
   
   def test_three_players(self):
      payload_3 = {"top" : 3}

      top_3 = [ {"username": "Michael", "games_played": 2, "total_score": 200,},
                  {"username": "Alice", "games_played": 0, "total_score": 0,} ,
                  {"username": "Steven", "games_played": 0, "total_score": 0,}]

      resp1 = requests.get(
                self.TEST_URL,
                json = payload_3)

      response1 = resp1.json()

      self.assertEqual(response1, top_3)

   def test_four_players(self):
      payload_2 = {"top" : 2}

      top_2 = [ {"username": "Michael", "games_played": 2, "total_score": 200,},
                  {"username": "Alice", "games_played": 0, "total_score": 0,}]

      resp2 = requests.get(
                self.TEST_URL,
                json = payload_2)

      response2 = resp2.json()

      self.assertEqual(response2, top_2)

if __name__ == '__main__':
    unittest.main()