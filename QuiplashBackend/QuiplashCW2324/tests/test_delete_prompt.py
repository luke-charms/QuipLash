import unittest
import json
import requests 

import azure.functions as func
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

   PUBLIC_URL="https://comp3207quiplashcw-lah1u21-2324.azurewebsites.net/api/prompt/delete?code=sjkJJQToPMC8Pdh6jb4hhkv8RXiA2n6yUdeL7Qii9Si_AzFuRc6-3A=="
   TEST_URL = PUBLIC_URL

   def test_delete_prompt_username(self):
      

      payload = {'player' : "Michael"}

      resp = requests.post(
                self.TEST_URL,
                json = payload)
      
      response = resp.json()     

      self.assertTrue(response['result'])
      self.assertEqual(response['msg'],"0 prompts deleted")
   

   def test_delete_prompt_word(self):
      payload = {'word' : "To"}

      resp = requests.post(
                self.TEST_URL,
                json = payload)
      
      response = resp.json()     

      self.assertTrue(response['result'])
      self.assertEqual(response['msg'],"1 prompts deleted")


   def test_delete_prompt_invalid_word(self):

      payload = {'word' : "Pruebas"}

      resp = requests.post(
                self.TEST_URL,
                json = payload)
      
      response = resp.json()     

      self.assertTrue(response['result'])
      self.assertEqual(response['msg'],"0 prompts deleted")



if __name__ == '__main__':
   unittest.main()