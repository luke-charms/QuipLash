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
   players_container = db_client.get_container_client(players_cont)

   PUBLIC_URL="https://comp3207quiplashcw-lah1u21-2324.azurewebsites.net/api/player/register?code=T_5NoYvXt-n6s7kPBKjBoNmROaR2RfNR1A1EmRfBDecZAzFuuqZX7Q=="
   TEST_URL = PUBLIC_URL

   def test_add_player_correct(self):
      #get size of database before insert
      size_before_insert = list(self.players_container.read_all_items())

      payload = {'username' : "Steven",
                  'password' : "longlongpassword"
             }

      resp = requests.post(
                self.TEST_URL,
                json = payload)
      
      size_after_insert = list(self.players_container.read_all_items())

      self.assertEqual(len(size_before_insert) + 1,len(size_after_insert))

      try:
        the_player_in_the_db = list(self.players_container.query_items(
            query = """SELECT * FROM c
                WHERE c.username = @username
                AND c.password = @password""",
            parameters=[{"name" : "@username" , "value" : payload['username']}, {"name": "@password", "value": payload['password']}],
            enable_cross_partition_query=True))
      except Exception as e:
         self.assertFalse()

      self.assertEqual(payload['username'],the_player_in_the_db[0]['username'])
      self.assertEqual(payload['password'],the_player_in_the_db[0]['password'])
      self.assertEqual(0,the_player_in_the_db[0]['games_played'])
      self.assertEqual(0,the_player_in_the_db[0]['total_score'])

      dict_response = resp.json()     

      self.assertTrue(dict_response['result'])
      self.assertEqual(dict_response['msg'],'OK')
   
   def test_add_player_fail_already_exists(self):
      payload = {'username' : "Michael",
                  'password' : "anotherlongpwd"
             }

      resp = requests.post(
                self.TEST_URL,
                json = payload)

      dict_response = resp.json()     

      self.assertFalse(dict_response['result'])
      self.assertEqual(dict_response['msg'],"Username already exists")
   
   def test_add_player_fail_username(self):
      payload1 = {'username' : "Sam",
                  'password' : "anotherlongpassword"
             }
      payload2 = {'username' : "SamueltheFirst1",
                  'password' : "anotherlongpassword"
             }

      resp1 = requests.post(
                self.TEST_URL,
                json = payload1)
      
      time.sleep(2)

      resp2 = requests.post(
                self.TEST_URL,
                json = payload2)

      dict_response1 = resp1.json()     
      dict_response2 = resp2.json()     

      self.assertFalse(dict_response1['result'])
      self.assertEqual(dict_response1['msg'],"Username less than 4 characters or more than 14 characters")
      self.assertFalse(dict_response2['result'])
      self.assertEqual(dict_response2['msg'],"Username less than 4 characters or more than 14 characters")
   
   def test_add_player_fail_password(self):
      payload1 = {'username' : "Samuel2",
                  'password' : "apass"
             }
      payload2 = {'username' : "Samuel2",
                  'password' : "thisisaverylongpasswordthatdoesntwork"
             }

      resp1 = requests.post(
                self.TEST_URL,
                json = payload1)
      
      time.sleep(2)


      resp2 = requests.post(
                self.TEST_URL,
                json = payload2)

      dict_response1 = resp1.json()     
      dict_response2 = resp2.json()     

      self.assertFalse(dict_response1['result'])
      self.assertEqual(dict_response1['msg'],"Password less than 10 characters or more than 20 characters")
      self.assertFalse(dict_response2['result'])
      self.assertEqual(dict_response2['msg'],"Password less than 10 characters or more than 20 characters")

if __name__ == '__main__':
   unittest.main()