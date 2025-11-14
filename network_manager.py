import struct
from typing import Type, Callable
from udp_layer import UDPLayer, MessageLayer, PORT
from player import Player
from io import BytesIO



def read_stream(stream: BytesIO, format: str):
  size = struct.calcsize(format)
  return struct.unpack(format, stream.read(size))




ID_SPAWN = 0
ID_PLAYER_MOVE = 1
ID_INPUT = 2
ID_PLAYER_ASSIGNMENT = 3

ID_JOIN = 99

ID_SPAWN_PLAYER = 0

class NetworkManager:
  
  
  def __init__(self, udp_layer: UDPLayer | MessageLayer):
    self.udp_layer = udp_layer
    
    
    self.player_id: None | int = None
    if self.udp_layer.is_server: self.player_id = 0
    self.free_player_id = 0
    self.players: list[Player] = []
    self.assigned_players: list[int] = []
    
    self.send_buffer = BytesIO()
    self.private_send_buffers: dict[tuple[str, int], BytesIO] = {}
    
    if self.udp_layer.is_server:
      self.server_spawn_player(0, 0)
  
  def initiate_connection(self, optional_server_address = None):
    if optional_server_address:
      return
    self.udp_layer.send(b"connect!")
    #TODO make this reliable
    #TODO handle a failed connection
    
  
  def receive(self):
    
    while True:
      stream, source = self.udp_layer.recieve()
      if not stream:
        break
      
      while True:
        typebyte = stream.read(1)
        if typebyte == b'':
          break
        type_byte = int.from_bytes(typebyte)
        
        #TODO ensure that a server doesn't care about some of these message types so the clients
        #don't have infinite power
        
        #TODO break this out into a dispatch table instead of a long list of if statements
        
        if type_byte == ID_SPAWN:
          #decode the spawn type
          spawntype = int.from_bytes(stream.read(1))
          if spawntype == 0:
            self.remote_spawn_player(stream)
        
        if type_byte == ID_PLAYER_MOVE:
          self.remote_player_move(stream)
        
        if type_byte == ID_INPUT:
          self.remote_input(stream)
        
        if type_byte == ID_PLAYER_ASSIGNMENT:
          self.player_id = read_stream(stream, "!B")[0]
          print("assigned ID", self.player_id)
        
        if type_byte == ID_JOIN:
          stream.read(len("onnect!"))
          player_id = self.free_player_id
          self.server_spawn_player(160, 160)
          #TODO fix this so that the player id is not sent to all but only to the one that connected!
          if isinstance(source, tuple):
            if source not in self.private_send_buffers:
              self.private_send_buffers[source] = BytesIO()
            self.private_send_buffers[source].write(struct.pack(b"!BB", ID_PLAYER_ASSIGNMENT, player_id))
  
  
  
  def send(self):
    """
    The sever queues up writes and this sends all that is queued
    """
    self.send_buffer.seek(0)
    self.udp_layer.send(self.send_buffer.read())
    self.send_buffer.seek(0)
    self.send_buffer.truncate(0)
    
    for destination, stream in self.private_send_buffers.items():
      stream.seek(0)
      self.udp_layer.send_to(stream.read(), destination)
      stream.seek(0)
      stream.truncate(0)
  
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
        break

  def remote_player_move(self, stream: BytesIO):
    #TODO do the position extrapolaton/interpolation thing
    
    id, x, y = read_stream(stream, "!Bff")
    #TODO There is a chance that there is no player to control at the ID
    for player in self.players:
      if id == player.id:
        player.position.x = x
        player.position.y = y
  
  def client_input(self, id, left, right, up, down):
    binary = left | (right << 1) | (up << 2) | (down << 3)
    self.send_buffer.write(struct.pack("!BBB", ID_INPUT, id, binary))
  
  def remote_input(self, stream):
    id, binary = read_stream(stream, "!BB")
    for player in self.players:
      if player.id == id:
        player.position.x -= binary >> 0 & 0b0001
        player.position.x += binary >> 1 & 0b0001
        player.position.y -= binary >> 2 & 0b0001
        player.position.y += binary >> 3 & 0b0001
        self.send_buffer.write(struct.pack("!BBff", ID_PLAYER_MOVE, id, player.position.x, player.position.y))
  #TODO these are basically the same get the movement code to be separate as it should basically do exactly the same
  def server_input(self, id, left, right, up ,down):
    binary = left | (right << 1) | (up << 2) | (down << 3)
    for player in self.players:
      if player.id == id:
        player.position.x -= binary >> 0 & 0b0001
        player.position.x += binary >> 1 & 0b0001
        player.position.y -= binary >> 2 & 0b0001
        player.position.y += binary >> 3 & 0b0001
        self.send_buffer.write(struct.pack("!BBff", ID_PLAYER_MOVE, id, player.position.x, player.position.y))


if __name__ == "__main__":
  #server = NetworkManager(udp_layer=MessageLayer(True, 0, []))
  
  #client = NetworkManager(udp_layer=MessageLayer(False, 1, [0]))
  
  server = NetworkManager(udp_layer=UDPLayer(True, []))
  client = NetworkManager(udp_layer=UDPLayer(False, [("127.0.0.1", PORT)]))
  
  
  #TODO handle joining in a better way than requires the timing to work out perfectly.
  #this probably means creating some sort of function that gets called when a player connect
  #packet is recieved and sending the current state in some way. This means sending spawn player
  #commands remotely probably.
  
  
  client.initiate_connection()
  
  server.receive()
  
  
  
  server.send()
  
  client.receive()
  
  server.server_player_move(0, 10, 0)
  
  client.receive()
  
  client.client_input(1, 0, 1, 0, 0)
  client.client_input(1, 0, 1, 0, 0)
  client.client_input(1, 0, 1, 0, 0)
  client.client_input(1, 0, 1, 0, 0)
  
  client.send()
  
  server.receive()
  
  server.send()
  
  client.receive()
  
  print(server.players)
  print(client.players)
  
  server.udp_layer.close()
  client.udp_layer.close()
  pass
  #test that spawning a player remotely works
  
  
  #initiate connection with reliable message
  
  #if connection then send all current state using spawn commands and state commands
  #DIRECTLY TO THAT CLIENT ONLY
  
  #server can spawn new things on clients remotely
  
  #server can control things remotely
  
  #client can send server specific action commands that control the server in specific ways
  
  
  #command types
  #spawn
  #server move player
  #client input
  
  
  #problems
  #how do I want to handle client syncing?
  #   Easiest way is to not initialize the server game state before all players agree they are ready
  #how do I want to handle client latency?
  #easiest way to just not, let there be latency! at 30fps 20ms of input latency might not even be detectable
  
  
  