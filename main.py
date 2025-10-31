import pygame
from udp_layer import UDPLayer
import sys
import struct
import enum
from typing import Callable, Type
from io import BytesIO

PORT = 59277
CONNECTION_TABLE = [[("0.0.0.0", PORT)], []]

class Flags:
  """
  the list orders the bits from least significant to most significant
  """
  def __init__(self, bits = [False,False,False,False, False,False,False,False]):
    self.bits:list[bool] = bits
  
  def get_flag(self, i):
    return self.bits[i]
  
  def from_bytes(self, data: bytes):
    binary = struct.unpack("B", data)[0]
    for i in range(8):
      self.bits[i] = (binary & (1 << i))>0
  
  def to_bytes(self) -> bytes:
    data = 0
    for i,v in enumerate(self.bits):
      data |= v << i
    return struct.pack("B", data)



class Message:
  def __init__(self, data):
    self.data = data
  
  def to_bytes(self) -> bytes:
    return bytes()

class PlayerMove(Message):
  
  def __init__(self, data: Flags):
    self.data = data
    
  def to_bytes(self) -> bytes:
    return self.data.to_bytes()
    

class MessageManager:
  
  def __init__(self):
    self.messages: list[Message] = []
    self.callbacks: dict[Type[Message],list[Callable[[Message], None]]] = {}
  
  def emit(self, data: Message):
    self.messages.append(data)
  
  def register(self, message_type: Type[Message], callback: Callable):
    if message_type not in self.callbacks:
      self.callbacks[message_type] = []
    self.callbacks[message_type].append(callback)
  
  def clear(self):
    self.messages = []
  
  
  def process(self):
    for message in self.messages:
      for callback in self.callbacks[type(message)]:
        callback(message)

class Player:
  def __init__(self, x, y):
    self.position = pygame.Vector2(x, y)
    self.velocity = pygame.Vector2(0, 0)  
  def update(self, engine: "Engine", message_manager: MessageManager):
    inputs = [False]*8
    flags = [False,False,False,False,False,False,False,False]
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]: self.position.x -= 4; flags[0]=True
    if keys[pygame.K_d]: self.position.x += 4; flags[1]=True
    if keys[pygame.K_w]: self.position.y -= 4; flags[2]=True
    if keys[pygame.K_s]: self.position.y += 4; flags[3]=True
    message_manager.emit(PlayerMove(Flags([flags])))

class NetworkManager:
  
  
  def __init__(self):
    self.udp_layer = UDPLayer(is_server, CONNECTION_TABLE[is_server])
    if not self.udp_layer.is_server:
      self.udp_layer.send(b"connect!")
    
    self.players = []
    self.types = [
      {
      "name": "spawn", 
      "types" : {
        0 : self.spawn_player
      }},
      {
      "name" : "playermove",
      "format" : "!ff"
      }]
  
  def recieve(self):
    
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
        
        info["types"][spawntype]
        
  
  def spawn_player(self, *args):
    self.players.append(Player(*args))

class Engine:
  
  
  def __init__(self, is_server = False):
    self.window_size = [320, 320]
    self.window = pygame.display.set_mode(self.window_size)
    
    self.pos1 = pygame.Vector2(160+80,160)
    self.pos2 = pygame.Vector2(160-80,160)
    self.exit_game = False
    self.clock = pygame.time.Clock()
    self.fps = 60
    self.message_manager = MessageManager()
    self.network_manager = NetworkManager()
    
    self.send_queue = []
    #self.message_manager.register(PlayerMove, )
  
  def run(self):
    
    
    try:
      while not self.exit_game:
        self.message_manager.clear()
        #INPUT
        for event in pygame.event.get():
          if event.type == pygame.QUIT:
            self.exit_game = True
        
        keys = pygame.key.get_pressed()
        
        
        if keys[pygame.K_LEFT]:  self.pos2.x -= 4
        if keys[pygame.K_RIGHT]: self.pos2.x += 4
        if keys[pygame.K_UP]:    self.pos2.y -= 4
        if keys[pygame.K_DOWN]:  self.pos2.y += 4
        
        #SIMULATION
        
        #NETWORK
        
        
          
        #GRAPHICS
        self.window.fill((0,0,0))
        self.window.fill((127,127,255), pygame.Rect(self.pos1, pygame.Vector2(16,16)))
        self.window.fill((255,127,127), pygame.Rect(self.pos2, pygame.Vector2(16,16)))
        pygame.display.update()
        self.clock.tick(self.fps)
    except KeyboardInterrupt:
      self.exit_game = True
  
  
  def close(self):
    self.udp_layer.close()
    pygame.quit()

if __name__ == "__main__":
  print(sys.argv)
  if len(sys.argv)>1:
    is_server = True
  else:
    is_server = False
  engine = Engine(is_server=is_server)
  engine.run()
  engine.close()


"""
there different issues

get the data to the network system

I can pass then engine to the objects and they can pass certain communication types that can be converted
convert the data to bytes
convert the data from bytes


get the data to the things that need it



there are certain variable types that need to be communicated fundamentally

types

float
int
string
flags

route id? 


register yourself to get the data for a type and route id?


entity 10 is a type and route number
not float 20 that would be too ambiguous

what about traversing? I could have a table for the sizes of the information, I could encode the size too.

player 0 data
player 1 data
player 2 data
player 3 data

entities 0 2^16-1 data 

"""



# 1.) the port number recieved on the server side can be used to distinguish 