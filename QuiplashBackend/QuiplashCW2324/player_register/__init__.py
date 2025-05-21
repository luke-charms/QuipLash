import json
import logging

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions

import os 
db_URI = os.environ['db_URI']
db_id = os.environ['db_id']
db_key = os.environ['db_key']
players_cont = os.environ['players_container']

#local_settings = json.load(open('local.settings.json'))
#db_URI = local_settings['Values']['db_URI']
#db_id = local_settings['Values']['Database']
#db_key = local_settings['Values']['db_key']
#players_cont = local_settings['Values']['PlayerContainer']
#prompts_cont = local_settings['Values']['PromptContainer']

from shared_code.Player import Player

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Registering a Player in progress....')

    #create the proxy object to query the cosmos database
    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)

    #create a proxy object to the quiplash comsos database
    db_client = client.get_database_client(db_id)

    #create a proxy object to the players database
    players_container = db_client.get_container_client(players_cont)

    username = req.get_json().get('username')
    password = req.get_json().get('password')

    input_player = Player(username, password)
    response_user = input_player.check_username()
    response_pass = input_player.check_password()

    if not response_user:
        return func.HttpResponse(body=json.dumps({"result": False , "msg": "Username less than 4 characters or more than 14 characters"  }))
    elif not response_pass:
        return func.HttpResponse(body=json.dumps({"result": False , "msg": "Password less than 10 characters or more than 20 characters"  }))

    logging.info('Inserting into database....')

    # Read the documentation of the create_item method and tree
    # https://learn.microsoft.com/en-us/python/api/azure-cosmos/azure.cosmos.containerproxy?view=azure-python#azure-cosmos-containerproxy-create-item
    # Reference on Python exception handling: https://docs.python.org/3.9/tutorial/errors.html
    
    try:
        player = players_container.query_items(
            query = """SELECT * FROM c
                WHERE c.username = @username""",
            parameters=[{"name" : "@username" , "value" : username}],
            enable_cross_partition_query=True)
        
        if len(list(player)) > 0:
           raise exceptions.CosmosHttpResponseError
        
        players_container.create_item(input_player.to_dict(),enable_automatic_id_generation=True)

        logging.info('DATA INSERTED!')

        return func.HttpResponse(body=json.dumps({"result": True , "msg" : "OK"}))
    except exceptions.CosmosHttpResponseError:
         return func.HttpResponse(body=json.dumps({"result": False , "msg": "Username already exists" }))
        
    # An alternative to the try-except approach is to query for the item before inserting ????