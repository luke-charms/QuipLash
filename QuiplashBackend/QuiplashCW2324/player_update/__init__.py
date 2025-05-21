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
    logging.info('Updating Player in progress....')

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)

    username = req.get_json().get('username')
    add_to_games_played = int(req.get_json().get('add_to_games_played'))
    add_to_score = int(req.get_json().get('add_to_score'))

    
    try:
        found_player = list(players_container.query_items(
            query = """SELECT * FROM c
                WHERE c.username = @username""",
            parameters=[{"name" : "@username" , "value" : username}],
            enable_cross_partition_query=True))
        
        if len(found_player) == 0:
            return func.HttpResponse(body=json.dumps({"result": False , "msg": "Player does not exist" }))

        for player in found_player:
            print(player)
            initial_games_played = int(player['games_played'])
            inital_total_score = int(player['total_score'])
            password = player['password']
            id = player['id']

        new_games_played = initial_games_played + add_to_games_played
        new_total_score = inital_total_score + add_to_score

        print(new_games_played, new_total_score)

        payload = {"username": username,
                   "password": password,
                   "games_played": new_games_played,
                   "total_score": new_total_score,
                   "id": id
                   }
        
        print(payload)
        
        players_container.upsert_item(body=payload,pre_trigger_include = None,post_trigger_include= None)

        return func.HttpResponse(body=json.dumps({"result": True , "msg" : "OK"}))
    except exceptions.CosmosResourceNotFoundError:
        return func.HttpResponse(body=json.dumps({"result": False , "msg": "Player does not exist" }))