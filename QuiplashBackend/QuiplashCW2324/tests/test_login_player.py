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

   PUBLIC_URL="https://comp3207quiplashcw-lah1u21-2324.azurewebsites.net/api/player/login?code=vK9hIubB2rKRN8wHul9p_4jJY8bl18l42Zfr0A7PPhMiAzFunRYN8g=="
   TEST_URL = PUBLIC_URL

   def test_add_player_correct(self):
      payload = {'username' : "Michael",
                    'password' : "longlongpassword"
             }

      resp = requests.get(
                self.TEST_URL,
                json = payload)
      
      dict_response = resp.json()     

      self.assertTrue(dict_response['result'])
      self.assertEqual(dict_response['msg'],'OK')
   
   def test_add_player_fail_username(self):
      payload = {'username' : "not_here",
                    'password' : "popgoestheweasel"
             }

      resp = requests.get(
                self.TEST_URL,
                json = payload)
      
      dict_response = resp.json()     

      self.assertFalse(dict_response['result'])
      self.assertEqual(dict_response['msg'],'Username or password incorrect')
   

   def test_add_player_fail_password(self):
      payload = {'username' : "Samuel",
                    'password' : "notthepassword"
             }

      resp = requests.get(
                self.TEST_URL,
                json = payload)
      
      dict_response = resp.json()     

      self.assertFalse(dict_response['result'])
      self.assertEqual(dict_response['msg'],'Username or password incorrect')

if __name__ == '__main__':
   unittest.main()