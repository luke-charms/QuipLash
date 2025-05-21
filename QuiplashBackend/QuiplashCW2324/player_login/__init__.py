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

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Logging in Player in progress....')

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)

    username = req.get_json().get('username')
    password = req.get_json().get('password')

    try:
        players = players_container.query_items(
            query = """SELECT * FROM c
                WHERE c.username = @username
                AND c.password = @password""",
            parameters=[{"name" : "@username" , "value" : username}, {"name": "@password", "value": password}],
            enable_cross_partition_query=True)
        if len(list(players)) == 0:
           raise exceptions.CosmosResourceNotFoundError
        return func.HttpResponse(body=json.dumps({"result": True , "msg" : "OK"}))
    except exceptions.CosmosResourceNotFoundError:
        return func.HttpResponse(body=json.dumps({"result": False , "msg": "Username or password incorrect"}))