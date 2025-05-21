import logging
import json

import azure.functions as func
import azure.cosmos as cosmos

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
    logging.info('Getting top leaderboard...')

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key )
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)

    #INPUT: {{"top" : 5}} + 1 to search one extra player
    number = int(req.get_json().get('top')) + 1

    players = list(players_container.query_items(
            query = """SELECT c.username, c.games_played, c.total_score FROM c 
            WHERE c.total_score != '0' 
            ORDER BY c.total_score DESC 
            OFFSET 0 LIMIT @num""",
            parameters=[{"name" : "@num" , "value" : number}],     
            enable_cross_partition_query=True))
    
    bool_list = False
    counter = 0

    while not bool_list:
        if counter == 10:
            bool_list = True
        if (players[-1]['total_score']) != (players[-2]['total_score']):
            bool_list = True
        else:
            number += 1
            counter += 1
            players = list(players_container.query_items(
                query = """SELECT c.username, c.games_played, c.total_score FROM c 
                WHERE c.total_score != '0' 
                ORDER BY c.total_score DESC 
                OFFSET 0 LIMIT @num""",
                parameters=[{"name" : "@num" , "value" : number}],     
                enable_cross_partition_query=True))
    
    logging.info("out of loop")

    sorted_list = sorted(players, key=lambda x: (10000000000000 - x['total_score'], x['games_played'], x['username']), reverse=False)

    while len(sorted_list) != int(req.get_json().get('top')):
        sorted_list.pop()

    return func.HttpResponse(body=json.dumps(sorted_list))

