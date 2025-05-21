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

from shared_code.Prompt import Prompt

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Registering a Player in progress....')

    #create the proxy object to query the cosmos database
    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)

    #create a proxy object to the quiplash comsos database
    db_client = client.get_database_client(db_id)

    #create a proxy object to the prompt database
    prompts_container = db_client.get_container_client(prompts_cont)

    text = req.get_json().get('text')
    username = req.get_json().get('username')

    input_prompt = Prompt(text, username)
    user_check = input_prompt.check_username()
    text_check = input_prompt.check_text()
    translate_check = input_prompt.check_translation()

    if not translate_check:
        return func.HttpResponse(body=json.dumps({"result": False , "msg": "Unsupported language"  }))
    elif not text_check:
        return func.HttpResponse(body=json.dumps({"result": False , "msg": "Prompt less than 15 characters or more than 80 characters"  }))
    elif not user_check:
        return func.HttpResponse(body=json.dumps({"result": False , "msg": "Player does not exist" }))
    
    input_prompt.translate_text()

    logging.info('Inserting into database....')

    try:
        prompts_container.create_item(input_prompt.to_dict(),enable_automatic_id_generation=True)

        logging.info('DATA INSERTED!')

        return func.HttpResponse(body=json.dumps({"result": True , "msg" : "OK"}))
    except exceptions.CosmosHttpResponseError:
         return func.HttpResponse(body=json.dumps({"result": False , "msg": "Error" }))
