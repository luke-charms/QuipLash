import json
import logging

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions

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
    logging.info('Deleting a prompt...')

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key )
    db_client = client.get_database_client(db_id)
    prompts_container = db_client.get_container_client(prompts_cont)

    logging.info("Recieved a username")
    input = req.get_json().get('player')
    username = True

    if input == None:
        logging.info("Nevermind... recieved a word")
        input = req.get_json().get('word')
        username = False

    try:
        if username:
            all_prompts = prompts_container.query_items(
                query = """SELECT * FROM c
                WHERE c.username = @username""",
                parameters=[{"name" : "@username" , "value" : input}],
                enable_cross_partition_query=True)
        else:
            all_prompts = prompts_container.query_items(
                query = """SELECT p.id, p.username,
              ARRAY (SELECT DISTINCT VALUE c.text FROM c IN p.texts WHERE c.language = 'en') AS textPrompts
              FROM products p""",
                enable_cross_partition_query=True)
            
        counter = 0
        if username:
            for prompt in all_prompts:
                prompts_container.delete_item(item=prompt['id'],partition_key=prompt['username'])
                counter += 1
        else:
            for prompt in all_prompts:
                strng = ''.join(prompt['textPrompts'])
                strng = strng.translate(str.maketrans('', '', "?,!\"'"))
                words = strng.split()
                for word in words:
                    if input == word:
                         prompts_container.delete_item(item=prompt['id'],partition_key=prompt['username'])
                         counter += 1
        return func.HttpResponse(body=json.dumps({"result": True, 'msg':(str(counter) + " prompts deleted")}))
    except exceptions.CosmosResourceNotFoundError:
        return func.HttpResponse(body=json.dumps({"result": False , 'msg':'Does not exist'}))