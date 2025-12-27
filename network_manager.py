import struct
from typing import Type, Callable
from udp_layer import UDPLayer, MessageLayer, PORT
from player import Player
from enemy import RedEnemy
from io import BytesIO
import time


def read_stream(stream: BytesIO, format: str):
  size = struct.calcsize(format)
  return struct.unpack(format, stream.read(size))




ID_SPAWN = 0
ID_PLAYER_MOVE = 1
ID_INPUT = 2
ID_PLAYER_ASSIGNMENT = 3
ID_ENEMY_MOVE = 4
ID_ENEMY_POSITION = 5

ID_JOIN = 99

ID_SPAWN_PLAYER = 0
ID_SPAWN_RED_ENEMY = 1

class NetworkManager:
  
  
  def __init__(self, udp_layer: UDPLayer | MessageLayer):
    self.udp_layer = udp_layer
    
    
    self.player_id: None | int = None
    # (Change) no longer will a player be automatic since even the host is a client
    #if self.udp_layer.is_server: self.player_id = 0
    self.free_player_id = 0
    self.players: list[Player] = []
    self.assigned_players: list[int] = []
    
    self.enemies: list[RedEnemy] = []
    self.free_enemy_id = 0
    self.refresh_enemy = 0
    
    self.send_buffer = BytesIO()
    self.private_send_buffers: dict[tuple[str, int], BytesIO] = {}
    self.tick_rate = 1/30
    self.last_tick = time.monotonic()
    
    # (Change) no longer will a player be automatic since even the host is a client
    #if self.udp_layer.is_server:
    #  self.server_spawn_player(0, 0)
  
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
          if spawntype == ID_SPAWN_PLAYER:
            self.remote_spawn_player(stream)
          if spawntype == ID_SPAWN_RED_ENEMY:
            self.remote_spawn_red_enemy(stream)
        
        if type_byte == ID_PLAYER_MOVE:
          self.remote_player_move(stream)
        
        if type_byte == ID_INPUT:
          self.remote_input(stream)
        
        if type_byte == ID_PLAYER_ASSIGNMENT:
          self.player_id = read_stream(stream, "!B")[0]
          print("assigned ID", self.player_id)
        
        if type_byte == ID_ENEMY_MOVE:
          self.remote_enemy_move(stream)
        
        if type_byte == ID_ENEMY_POSITION:
          self.remote_enemy_set_position(stream)
        
        if type_byte == ID_JOIN:
          stream.read(len("onnect!"))
          player_id = self.free_player_id
          self.server_spawn_player(160, 160)
          #TODO fix this so that the player id is not sent to all but only to the one that connected!
          if isinstance(source, tuple):
            if source not in self.private_send_buffers:
              self.private_send_buffers[source] = BytesIO()
            self.private_send_buffers[source].write(struct.pack(b"!BB", ID_PLAYER_ASSIGNMENT, player_id))
            
            #TODO move this into a proper syncing function
            #TODO packet splitting absolutely neccassary 
            for player in self.players:
              self.private_send_buffers[source].write(struct.pack("!BBBff", ID_SPAWN, ID_SPAWN_PLAYER, player.id, player.position.x, player.position.y))
            for enemy in self.enemies:
              self.private_send_buffers[source].write(struct.pack("!BBBhh", ID_SPAWN, ID_SPAWN_RED_ENEMY, enemy.id, int(enemy.position.x), int(enemy.position.y)))
  
  
  
  def send(self):
    #if self.udp_layer.is_server:
    #  if time.monotonic() > self.last_tick + self.tick_rate:
    #    self.last_tick = time.monotonic()
    #  else:
    #    return
    """
    The sever queues up writes and this sends all that is queued
    """
    self.send_buffer.seek(0)
    data = self.send_buffer.read()
    
    print(len(data))
    
    self.udp_layer.send(data)
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
  
  
  def server_spawn_red_enemy(self, x, y):
    self.enemies.append(RedEnemy(self.free_enemy_id, x, y))
    self.enemies[-1].enemies = self.enemies
    data = struct.pack("!BBBhh", ID_SPAWN, ID_SPAWN_RED_ENEMY, self.free_enemy_id, int(x), int(y))
    self.send_buffer.write(data)
    self.free_enemy_id += 1
  
  
  def remote_spawn_player(self, stream):
    args = read_stream(stream, "!Bff")
    self.players.append(Player(*args))
  
  
  def remote_spawn_red_enemy(self, stream):
    args = read_stream(stream, "!Bhh")
    self.enemies.append(RedEnemy(*args))
    self.enemies[-1].enemies = self.enemies
    
  
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
        player.previous_position = player.position.copy()
        player.position.x = x
        player.position.y = y
        player.previous_update_time = time.monotonic()
  
  
  def remote_enemy_move(self, stream: BytesIO):
    id, x, y = read_stream(stream, "!Bbb")
    for enemy in self.enemies:
      if enemy.id == id:
        enemy.previous_position = enemy.position.copy()
        enemy.position.x += x / 10 * 3
        enemy.position.y += y / 10 * 3
        enemy.previous_update_time = time.monotonic()
  
  def remote_enemy_set_position(self, stream: BytesIO):
    id, x, y = read_stream(stream, "!Bhh")
    for enemy in self.enemies:
      if enemy.id == id:
        enemy.position.x = x
        enemy.position.y = y
  
  
  def client_input(self, id, left, right, up, down):
    binary = left | (right << 1) | (up << 2) | (down << 3)
    self.send_buffer.write(struct.pack("!BBB", ID_INPUT, id, binary))
  
  def player_move(self, player: Player, binary: int):
    """
    Docstring for player_move
    
    :param player: player object to move
    :param binary: left right up down bits for control
    """
    player.velocity.x -= (binary >> 0 & 0b0001) * player.SPEED
    player.velocity.x += (binary >> 1 & 0b0001) * player.SPEED
    player.velocity.y -= (binary >> 2 & 0b0001) * player.SPEED
    player.velocity.y += (binary >> 3 & 0b0001) * player.SPEED
  
  def player_update(self, player: Player, delta = 1/20):
    player.position += player.velocity * delta
    player.velocity *= pow(0.002, delta)
  
  def remote_input(self, stream):
    #Move the player based on 
    id, binary = read_stream(stream, "!BB")
    for player in self.players:
      if player.id == id:
        self.player_move(player, binary)
        
        self.send_buffer.write(struct.pack("!BBff", ID_PLAYER_MOVE, id, player.position.x, player.position.y))
  
  #TODO remove this since the host is a client now I think
  def server_input(self, id, left, right, up ,down):
    #Move the player and send result to everyone
    binary = left | (right << 1) | (up << 2) | (down << 3)
    for player in self.players:
      if player.id == id:
        self.player_move(player, binary)
  
  
  def server_update(self):
    
    #TODO move to Player code
    for player in self.players:
      self.player_update(player)
      self.send_buffer.write(struct.pack("!BBff", ID_PLAYER_MOVE, player.id, player.position.x, player.position.y))
      for player2 in self.players:
        if player is player2: continue
        difference = (player2.position - player.position)
        l2 = difference.dot(difference)
        if l2 < 15*15:
          l = l2**0.5
          if l != 0:
            player2.position += difference / l * (15-l)
    
    #TODO move to enemy code
    for enemy in self.enemies:
      closest_position = None
      closest_distance = -1
      for player in self.players:
        if closest_position == None:
          closest_position = player.position
          closest_distance = (enemy.position - player.position).length_squared()
          continue
        dist = (enemy.position - player.position).length_squared()
        if dist < closest_distance:
          closest_distance = dist
          closest_position = player.position
      enemy.target = closest_position
      previous_position = enemy.position.copy()
      enemy.update()
      delta_position = enemy.position - previous_position
      
      #TODO move delta code such that it is based on the message send interval
      #this means setting the previous enemy position around the time of sending too
      self.send_buffer.write(struct.pack("!BBbb", ID_ENEMY_MOVE, enemy.id, int(delta_position.x*10/3), int(delta_position.y*10/3)))
    
    
    
    if len(self.enemies):
      self.refresh_enemy = (self.refresh_enemy + 1) % len(self.enemies)
      refresh_enemy = self.enemies[self.refresh_enemy]
      self.send_buffer.write(struct.pack("!BBhh", ID_ENEMY_POSITION, refresh_enemy.id, int(refresh_enemy.position.x), int(refresh_enemy.position.y)))

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
  
  
  