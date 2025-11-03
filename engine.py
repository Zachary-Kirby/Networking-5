import pygame
from network_manager import NetworkManager
from message_manager import MessageManager
from udp_layer import UDPLayer

PORT = 59277
CONNECTION_TABLE = [[("0.0.0.0", PORT)], []]

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
    self.network_manager = NetworkManager(udp_layer=UDPLayer(is_server, CONNECTION_TABLE[is_server]))
    
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
    self.network_manager.udp_layer.close()
    pygame.quit()