import struct
from typing import Type, Callable
from udp_layer import UDPLayer, MessageLayer
from player import Player, PlayerMove






ID_SPAWN = 0
ID_PLAYER_MOVE = 1

class NetworkManager:
  
  
  def __init__(self, udp_layer: MessageLayer | UDPLayer):
    self.udp_layer = udp_layer
    if not self.udp_layer.is_server:
      self.udp_layer.send(b"connect!")
    
    self.free_player_id = 0
    self.players = []
    self.types = {
      ID_SPAWN : {
      "name": "spawn", 
      "types" : {
        0 : {"function" : self.spawn_player, "format" : "!Bff"} # create a player that has ID and position
      }},
      ID_PLAYER_MOVE : {
      "name" : "playermove",
      "format" : "!ff"
      }}
  
  def receive(self):
    
    while True:
      stream = self.udp_layer.recieve()
      if not stream:
        break
      
      #loop through the data in the stream
      
      #1. get the type
      #2. get the length of the encoded data
      #if type is spawn then get the spawn type and the spawn info using an architype
      object_type = int.from_bytes(stream.read(1))
      info = self.types[object_type]
      name = info["name"]
      if name == "spawn":
        spawntype = int.from_bytes(stream.read(1))
        
        func = info["types"][spawntype]["function"]
        format = info["types"][spawntype]["format"]
        
        func(struct.unpack(format, stream.read(struct.calcsize(format))))
        
  
  def spawn_player(self, *args):
    if self.udp_layer.is_server:
      self.players.append(Player(*args, id=self.free_player_id))
      #self.udp_layer.send(struct.pack(self.types[ID_SPAWN]["types"]["format"]))
      self.free_player_id += 1
    else:
      self.players.append(Player(*args))
    
    
      
      
      
    
    
#TODO spawn a player remotely

if __name__ == "__main__":
  server = NetworkManager(udp_layer=MessageLayer(True, 0, [1]))
  client = NetworkManager(udp_layer=MessageLayer(False, 1, [0]))
  
  server.spawn_player(15, 4)
  server.spawn_player(32, 6)
  #test that spawning a player remotely works
  