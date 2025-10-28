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
  
  def process(self):
    for message in self.messages:
      for callback in self.callbacks[type(message)]:
        callback(message)

class Engine:
  
  
  def __init__(self, is_server = False):
    self.window_size = [320, 320]
    self.window = pygame.display.set_mode(self.window_size)
    self.udp_layer = UDPLayer(is_server, CONNECTION_TABLE[is_server])
    self.pos1 = pygame.Vector2(160+80,160)
    self.pos2 = pygame.Vector2(160-80,160)
    self.exit_game = False
    self.clock = pygame.time.Clock()
    self.fps = 60
    self.message_manager = MessageManager()
    self.send_queue = []
    #self.message_manager.register(PlayerMove, )
  
  def run(self):
    if not self.udp_layer.is_server:
      self.udp_layer.send(b"connect!") #initiate communication
    
    try:
      while not self.exit_game:
        
        #INPUT
        for event in pygame.event.get():
          if event.type == pygame.QUIT:
            self.exit_game = True
        
        keys = pygame.key.get_pressed()
        flags = [False,False,False,False,False,False,False,False]
        if keys[pygame.K_a]: self.pos1.x -= 4; flags[0]=True
        if keys[pygame.K_d]: self.pos1.x += 4; flags[1]=True
        if keys[pygame.K_w]: self.pos1.y -= 4; flags[2]=True
        if keys[pygame.K_s]: self.pos1.y += 4; flags[3]=True
        if sum(flags): self.message_manager.emit(PlayerMove(Flags(flags)))
        
        if keys[pygame.K_LEFT]:  self.pos2.x -= 4
        if keys[pygame.K_RIGHT]: self.pos2.x += 4
        if keys[pygame.K_UP]:    self.pos2.y -= 4
        if keys[pygame.K_DOWN]:  self.pos2.y += 4
        
        #SIMULATION
        
        #NETWORK
        
        if self.udp_layer.is_server:
          data = BytesIO()
          #data.write()
          
          #self.udp_layer.send(data)
        
        
        
        while True:
          stream = self.udp_layer.recieve()
          if stream:
            if self.udp_layer.is_server:
              pass
            else:
              x,y = struct.unpack("ff", stream.read(8))
              self.pos1.x = x
              self.pos1.y = y
              
          else:
            break
          
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


# 1.) the port number recieved on the server side can be used to distinguish 