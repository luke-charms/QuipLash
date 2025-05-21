import unittest
import json
import requests 
import azure.cosmos as cosmos

local_settings = json.load(open('local.settings.json'))
db_URI = local_settings['Values']['db_URI']
db_id = local_settings['Values']['Database']
db_key = local_settings['Values']['db_key']
players_cont = local_settings['Values']['PlayerContainer']
prompts_cont = local_settings['Values']['PromptContainer']

class TestFunction(unittest.TestCase):
   client = cosmos.cosmos_client.CosmosClient(db_URI, db_key )
   db_client = client.get_database_client(db_id)
   players_container = db_client.get_container_client(players_cont)

   PUBLIC_URL="https://comp3207quiplashcw-lah1u21-2324.azurewebsites.net/api/player/update?code=lXT2M0Pt2FlsvcCQP_CMegUtSVK6ecdhQjaKK499sJTwAzFuExPiIQ=="
   TEST_URL = PUBLIC_URL

   def test_add_player_correct(self):
      payload = {"username": "Michael" , 
                 "add_to_games_played": 1 , 
                 "add_to_score" : 100 }
      
      try:
        the_player_in_the_db = list(self.players_container.query_items(
            query = """SELECT * FROM c
                WHERE c.username = @username""",
            parameters=[{"name" : "@username" , "value" : payload['username']}],
            enable_cross_partition_query=True))
        previous_games_played = the_player_in_the_db[0]['games_played']
        previous_total_score = the_player_in_the_db[0]['total_score']
        
      except Exception as e:
         self.assertFalse("Player not found!")

      resp = requests.put(
                self.TEST_URL,
                json = payload)

      try:
        the_player_in_the_db = list(self.players_container.query_items(
            query = """SELECT * FROM c
                WHERE c.username = @username""",
            parameters=[{"name" : "@username" , "value" : payload['username']}],
            enable_cross_partition_query=True))
        new_games_played = the_player_in_the_db[0]['games_played']
        new_total_score = the_player_in_the_db[0]['total_score']

        self.assertEqual(new_games_played, previous_games_played + int(payload['add_to_games_played']))
        self.assertEqual(new_total_score, previous_total_score + int(payload['add_to_score']))

      except Exception as e:
         self.assertFalse("Player not found!")
   
   def test_add_player_fail(self):

      payload = {"username": "Samuel" , 
                 "add_to_games_played": 1 , 
                 "add_to_score" : 100 }

      resp = requests.put(
                self.TEST_URL,
                json = payload)


      response = resp.json()

      self.assertFalse(response['result'])
      self.assertEqual(response['msg'],"Player does not exist")


if __name__ == '__main__':
   unittest.main()