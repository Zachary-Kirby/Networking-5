import pygame
from udp_layer import UDPLayer
import sys

PORT = 59277
CONNECTION_TABLE = [[("0.0.0.0", PORT)], []]

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
  
  
  def run(self):
    if not self.udp_layer.is_server:
      self.udp_layer.send(b"hi!") #initiate communication
    
    try:
      while not self.exit_game:
        
        #INPUT
        for event in pygame.event.get():
          if event.type == pygame.QUIT:
            self.exit_game = True
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: self.pos1.x -= 4
        if keys[pygame.K_d]: self.pos1.x += 4
        if keys[pygame.K_w]: self.pos1.y -= 4
        if keys[pygame.K_s]: self.pos1.y += 4
        
        if keys[pygame.K_LEFT]:  self.pos2.x -= 4
        if keys[pygame.K_RIGHT]: self.pos2.x += 4
        if keys[pygame.K_UP]:    self.pos2.y -= 4
        if keys[pygame.K_DOWN]:  self.pos2.y += 4
        
        #SIMULATION
        
        #NETWORK
        
        if self.udp_layer.is_server:
          self.udp_layer.send(b"hello slave!")
        stream = self.udp_layer.recieve()
        if stream:
          print(stream.read(20))
        
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