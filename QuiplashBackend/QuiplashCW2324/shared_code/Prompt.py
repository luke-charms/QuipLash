import requests, uuid
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions

class Prompt:
  client = cosmos.cosmos_client.CosmosClient("https://comp3207-quiplashcw-2324.documents.azure.com:443/", "insert azure keycode")
  db_client = client.get_database_client("quiplash")
  players_container = db_client.get_container_client("player")

  translate_key = "0746a1015c6c496782461051745cbad8"
  translate_endpoint = "https://api.cognitive.microsofttranslator.com"
  location = "uksouth"

  def __init__(self,texts="",username="",detected_lang=""):
    self.texts = texts
    self.username = username
    self.detected_lang = detected_lang

  def to_dict(self):
    """
    Implements a function that converts the Prompt object to a dictionary
    """
    return {
      "username": self.username,
      "texts": self.texts
    }
    
  def check_username(self):
    try:
      player = self.players_container.query_items(
            query = """SELECT * FROM c
                WHERE c.username = @username""",
            parameters=[{"name" : "@username" , "value" : self.username}],
            enable_cross_partition_query=True)
        
      if len(list(player)) == 0:
          return False
    except exceptions.CosmosHttpResponseError:
      return False
    
    return True

  def check_text(self):
    if len(self.texts) < 15 or len(self.texts) > 80:
      return False
    return True
    
  def check_translation(self):
    path = '/detect'
    constructed_url = self.translate_endpoint + path
    
    params = {
      'api-version': '3.0'
    }

    headers = {
      'Ocp-Apim-Subscription-Key': self.translate_key,
      'Ocp-Apim-Subscription-Region': self.location,
      'Content-type': 'application/json',
      'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{
      'text': self.texts
    }]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    translation_detection = request.json()

    if translation_detection[0]['score'] < 0.3 or translation_detection[0]['language'] not in ['en', 'es', 'it', 'sv', 'ru', 'id', 'bg', 'zh-Hans']:
      return False
    
    self.detected_lang = translation_detection[0]['language']

    print(translation_detection[0]['score'])
    print(translation_detection[0]['language'])
    return True


  def translate_text(self):
    
   # location, also known as region.
   # required if you're using a multi-service or regional (not global) resource. It can be found in the Azure portal on the Keys and Endpoint page.

   path = '/translate'
   constructed_url = self.translate_endpoint + path

   params = {
       'api-version': '3.0',
      'from': self.detected_lang,
      'to': ['en', 'es', 'it', 'sv', 'ru', 'id', 'bg', 'zh-Hans']
   }

   headers = {
       'Ocp-Apim-Subscription-Key': self.translate_key,
      # location required if you're using a multi-service or regional (not global) resource.
      'Ocp-Apim-Subscription-Region': self.location,
      'Content-type': 'application/json',
      'X-ClientTraceId': str(uuid.uuid4())
   }

   # You can pass more than one object in body.
   body = [{
      'text': self.texts
   }]

   request = requests.post(constructed_url, params=params, headers=headers, json=body)
   translations = request.json()

   texts = []

   for translation in translations[0]['translations']:
      texts.append({"language": translation['to'], "text": translation['text']})
   
   self.texts = texts
