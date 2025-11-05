import struct
from typing import Type, Callable
from udp_layer import UDPLayer, MessageLayer
from player import Player, PlayerMove
from io import BytesIO



def read_stream(stream: BytesIO, format: str):
  size = struct.calcsize(format)
  return struct.unpack(format, stream.read(size))


ID_SPAWN = 0
ID_PLAYER_MOVE = 1

ID_SPAWN_PLAYER = 0

class NetworkManager:
  
  
  def __init__(self, udp_layer: MessageLayer | UDPLayer):
    self.udp_layer = udp_layer
    
    
    self.free_player_id = 0
    self.players: list[Player] = []
    
    self.send_buffer = BytesIO()
  
  
  def initiate_connection(self, optional_server_address = None):
    if optional_server_address:
      return
    self.udp_layer.send(b"connect!")
    #TODO make this reliable
    #TODO handle a failed connection
    
  
  def receive(self):
    
    while True:
      stream = self.udp_layer.recieve()
      if not stream:
        break
      
      while True:
        typebyte = stream.read(1)
        if typebyte == b'':
          break
        type = int.from_bytes(typebyte)
        
        if type == ID_SPAWN:
          #decode the spawn type
          spawntype = int.from_bytes(stream.read(1))
          if spawntype == 0:
            self.remote_spawn_player(stream)
    
  def server_send(self):
    """
    The sever queues up writes and this sends all that is queued
    """
    self.send_buffer.seek(0)
    self.udp_layer.send(self.send_buffer.read())
    self.send_buffer.seek(0)
    self.send_buffer.truncate(0)
  
  #server messages need to contain a header and a payload. The messages may vary in size greaty and the header may vary a little too
  
  def server_spawn_player(self, x, y):
    self.players.append(Player(self.free_player_id, x, y))
    data = struct.pack("!BBBff", ID_SPAWN, ID_SPAWN_PLAYER, self.free_player_id, x, y)
    self.send_buffer.write(data)
    self.free_player_id += 1
  
  def remote_spawn_player(self, stream):
    args = read_stream(stream, "!Bff")
    self.players.append(Player(*args))
  
  def server_player_move(self, id, x, y):
    for player in self.players:
      if id == player.id:
        player.position.x = x
        player.position.y = y
    self.udp_layer.send(struct.pack(b"!BBff", ID_PLAYER_MOVE, id, player.position.x, player.position.y))

  def remote_player_move(self, stream: BytesIO):
    #TODO do the position extrapolaton/interpolation thing
    
    id, x, y = read_stream(stream, "!Bff")
    #TODO There is a chance that there is no player to control at the ID
    for player in self.players:
      if id == player.id:
        player.position.x += x
        player.position.y += y
    



if __name__ == "__main__":
  server = NetworkManager(udp_layer=MessageLayer(True, 0, []))
  
  client = NetworkManager(udp_layer=MessageLayer(False, 1, [0]))
  
  #TODO handle joining in a better way than requires the timing to work out perfectly.
  #this probably means creating some sort of function that gets called when a player connect
  #packet is recieved and sending the current state in some way. This means sending spawn player
  #commands remotely probably.
  
  client.initiate_connection()
  
  server.receive()
  
  server.server_spawn_player(15, 4)
  server.server_spawn_player(83, 32)
  server.server_send()
  
  client.receive()
  
  server.server_player_move(0, 10, 0)
  
  #test that spawning a player remotely works
  