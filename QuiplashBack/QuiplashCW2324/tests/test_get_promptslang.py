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
   PUBLIC_URL="https://comp3207quiplashcw-lah1u21-2324.azurewebsites.net/api/utils/get?code=u5AFGUoO9nnyvxnX_SysYhs-JDITG9t0xmIz_EKBRIL0AzFu1gpK1A=="
   TEST_URL = PUBLIC_URL
   
   def test_find_prompts(self):
      

      payload = {"players" : ["Alice"], 
                 "language": "en"
                 }
      
      answer_reply = [
            {"id": "0c2f7eb8-3d66-457d-b6c1-538fa7d31ab9" , "text" : "Testing just to make sure" , "username" : "Alice"}]

      resp = requests.get(
                self.TEST_URL,
                json = payload)

      response = resp.json()

      self.assertEqual(response, answer_reply)

   def test_find_one_user_prompts(self):

      payload = {"players" : ["Alice", "Michael" , "Samuel"],
                 "language": "sv"
                 }
      
      answer_reply = [{"id": "0c2f7eb8-3d66-457d-b6c1-538fa7d31ab9" , "text" : "Testa bara för att vara säker" , "username" : "Alice"}]

      resp = requests.get(
                self.TEST_URL,
                json = payload)

      response = resp.json()

      self.assertEqual(response, answer_reply)

   def test_find_no_prompts(self):

      payload = {"players" : ["Michael" , "Samuel"],
                 "language": "en"
                 }
      
      answer_reply = []

      resp = requests.get(
                self.TEST_URL,
                json = payload)

      response = resp.json()

      self.assertEqual(response, answer_reply)

if __name__ == '__main__':
    unittest.main()