import json
import logging

import azure.functions as func
import azure.cosmos as cosmos

import os 
db_URI = os.environ['db_URI']
db_id = os.environ['db_id']
db_key = os.environ['db_key']
prompts_cont = os.environ['prompts_container']

#local_settings = json.load(open('local.settings.json'))
#db_URI = local_settings['Values']['db_URI']
#db_id = local_settings['Values']['Database']
#db_key = local_settings['Values']['db_key']
#players_cont = local_settings['Values']['PlayerContainer']
#prompts_cont = local_settings['Values']['PromptContainer']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Gathering top prompts by language...')

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key )
    db_client = client.get_database_client(db_id)
    prompts_container = db_client.get_container_client(prompts_cont)

    #INPUT: {"players":  [list of usernames], "language": "langcode"}
    players = req.get_json().get('players')
    language = req.get_json().get('language')
       
    prompts = prompts_container.query_items(
            query = """SELECT * FROM c
                WHERE ARRAY_CONTAINS(@items, c.username)""",
            parameters=[{"name" : "@items" , "value" : players}],     
            enable_cross_partition_query=True)
    
    output = []

    for prompt in prompts:
       texts = prompt['texts']
       for text in texts:
          if text['language'] == language:
            output.append({"id": prompt['id'] , "text" : text['text'] , "username" : prompt['username']})
    
    #list(set(output))

    logging.info(output)
    
    return func.HttpResponse(body=json.dumps(output))
