import unittest
import json
import requests
import time

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
   prompts_container = db_client.get_container_client(prompts_cont)

   PUBLIC_URL="https://comp3207quiplashcw-lah1u21-2324.azurewebsites.net/api/prompt/create?code=ny4I0kjLGyOMcYPQP1hjQqvF4ZiM-Lu8xRwkubW8dkjuAzFutEsALg=="
   TEST_URL = PUBLIC_URL

   def test_add_prompt_correct(self):
      payload = {"text": "This is actually a pretty funny prompt", 
                 "username": "Michael" }

      resp = requests.post(
                self.TEST_URL,
                json = payload)

      try:
        the_prompt_in_the_db = self.prompts_container.query_items(
            query = """SELECT * FROM c
                WHERE c.username = @username""",
            parameters=[{"name" : "@username" , "value" : payload['username']}],
            enable_cross_partition_query=True)
      except Exception as e:
         self.assertFalse()

      self.assertEqual(payload['username'],list(the_prompt_in_the_db)[0]['username'])

      dict_response = resp.json()     

      self.assertTrue(dict_response['result'])
      self.assertEqual(dict_response['msg'],'OK')
   
   def test_add_text_too_short(self):
      payload = {"text": "Error", 
                 "username": "Michael" }

      resp = requests.post(
                self.TEST_URL,
                json = payload)

      dict_response = resp.json()     

      self.assertFalse(dict_response['result'])
      self.assertEqual(dict_response['msg'],"Prompt less than 15 characters or more than 80 characters")
   
   def test_add_player_doesnt_exist(self):
      payload1 = {'username' : "Nobody",
                  'text' : "this is a good prompt"
             }

      resp1 = requests.post(
                self.TEST_URL,
                json = payload1)
    
      dict_response1 = resp1.json()     

      self.assertFalse(dict_response1['result'])
      self.assertEqual(dict_response1['msg'],"Player does not exist")
   
   def test_add_bad_translation(self):
      payload1 = {'username' : "Michael",
                  'text' : "Jeg kommer ikke fra Danmark"
             }

      resp1 = requests.post(
                self.TEST_URL,
                json = payload1)

      dict_response1 = resp1.json()     

      self.assertFalse(dict_response1['result'])
      self.assertEqual(dict_response1['msg'],"Unsupported language")
   
   def test_add_bad_confidence_score(self):
      payload1 = {'username' : "Michael",
                  'text' : "1234"
             }

      resp1 = requests.post(
                self.TEST_URL,
                json = payload1)

      dict_response1 = resp1.json()     

      self.assertFalse(dict_response1['result'])
      self.assertEqual(dict_response1['msg'],"Unsupported language")

if __name__ == '__main__':
   unittest.main()