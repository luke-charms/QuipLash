import json, requests, logging
import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions

local_settings = json.load(open('local.settings.json'))
db_URI = local_settings['Values']['db_URI']
db_id = local_settings['Values']['Database']
db_key = local_settings['Values']['db_key']
players_cont = local_settings['Values']['PlayerContainer']
prompts_cont = local_settings['Values']['PromptContainer']

if __name__ == '__main__':
   client = cosmos.cosmos_client.CosmosClient(db_URI, db_key )
   db_client = client.get_database_client(db_id)
   prompts_container = db_client.get_container_client(prompts_cont)

   PUBLIC_URL="https://comp3207quiplashcw-lah1u21-2324.azurewebsites.net/api/prompt/create?code=ny4I0kjLGyOMcYPQP1hjQqvF4ZiM-Lu8xRwkubW8dkjuAzFutEsALg=="
   TEST_URL = PUBLIC_URL

   payload = {"text": "One two three four five", 
                 "username": "Michael" }

   resp = requests.post(
                TEST_URL,
                json = payload)

   try:
        the_prompt_in_the_db = prompts_container.query_items(
            query = """SELECT * FROM c
                WHERE c.username = @username""",
            parameters=[{"name" : "@username" , "value" : payload['username']}],
            enable_cross_partition_query=True)
   except Exception as e:
      print("FAIL")