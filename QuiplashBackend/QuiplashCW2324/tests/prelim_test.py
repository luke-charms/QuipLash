import json, requests
import azure.cosmos as cosmos

local_settings = json.load(open('local.settings.json'))
db_URI = local_settings['Values']['db_URI']
db_id = local_settings['Values']['Database']
db_key = local_settings['Values']['db_key']
players_cont = local_settings['Values']['PlayerContainer']
prompts_cont = local_settings['Values']['PromptContainer']


if __name__ == '__main__':

   PUBLIC_URL="https://comp3207quiplashcw-lah1u21-2324.azurewebsites.net/api/player/login?code=vK9hIubB2rKRN8wHul9p_4jJY8bl18l42Zfr0A7PPhMiAzFunRYN8g=="
   TEST_URL = PUBLIC_URL
   
   payload = {'username' : "Michael",
                    'password' : "longlongpassword"
    }
   
   print(requests.get(TEST_URL,json = payload))
      