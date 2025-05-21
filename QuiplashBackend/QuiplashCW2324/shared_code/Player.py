class Player:
  def __init__(self,username="",password="",games_played=0,total_score=0):
    self.username = username
    self.password = password
    self.games_played = games_played
    self.total_score = total_score
  
  def __str__(self):
    """
    Output: string representation of Player
    """
    return """
    username={}
    password={}
    games played = {}
    total score = {}
    """.format(self.username,self.password,self.games_played,self.total_score)

  def to_dict(self):
    """
    Implements a function that converts the Player object to a dictionary
    """
    return {
      "username": self.username,
      "password": self.password,
      "games_played": self.games_played,
      "total_score": self.total_score
    }
    
  def check_username(self):
    if len(self.username) < 4 or len(self.username) > 14:
      return False
    return True
  
  def check_password(self):
    if len(self.password) < 10 or len(self.password) > 20:
      return False
    return True
    

  def from_dict(self,dict_player):
    """
    Implements a function that takes a dictionary and replace the attributes of this player with its values.
    Raise a ValueError("Input dict is not from a Player") if the input dict_player does not have exactly the five keys that define a player
    """
    temp_dict = {
      'id' : self.id,
      'username' : self.username,
      'password' : self.password,
      'games_played' : self.games_played,
      'total_score' : self.total_score
    }
    
    if all(key in dict_player for key in temp_dict):
      self.id = dict_player['id']
      self.username = dict_player['username']
      self.password = dict_player['password']
      self.games_played = dict_player['games_played']
      self.total_score = dict_player['total_score']
    else:
      raise ValueError("Input dictionary is not from a Player")
