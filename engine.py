import pygame
from network_manager import NetworkManager
from message_manager import MessageManager
from udp_layer import UDPLayer

PORT = 59277
CONNECTION_TABLE = [[("127.0.0.1", PORT)], []]

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
  
  def pre_start(self):
    """
    For now there needs to be a portion waiting for all players so that syncing the data can be hardcoded and once
    """
    while True:
      self.network_manager.receive()
      
      
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.exit_game = True
          return
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_ESCAPE:
            return
      
  
  def run(self):
    
    if not self.network_manager.udp_layer.is_server:
      self.network_manager.initiate_connection()
    else:
      self.pre_start()
      
      #The initial sync
      for x in range(len(self.network_manager.udp_layer.connections)+1):
        self.network_manager.server_spawn_player(x*20+160-20*1, 160)
    
    try:
      while not self.exit_game:
        self.message_manager.clear()
        #INPUT
        for event in pygame.event.get():
          if event.type == pygame.QUIT:
            self.exit_game = True
        
        keys = pygame.key.get_pressed()
        
        
        
        #SIMULATION
        
        #NETWORK
        
        self.network_manager.receive()
        
        if self.network_manager.udp_layer.is_server:
          self.network_manager.server_input(0, keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_w], keys[pygame.K_s])
        else:
          self.network_manager.client_input(1, keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_w], keys[pygame.K_s])
        
        self.network_manager.send()
        
        #GRAPHICS
        self.window.fill((0,0,0))
        
        for i in range(len(self.network_manager.players)):
          self.window.fill((127,127,255), pygame.Rect(self.network_manager.players[i].position, pygame.Vector2(16,16)))
        pygame.display.update()
        self.clock.tick(self.fps)
    except KeyboardInterrupt:
      self.exit_game = True
  
  
  def close(self):
    self.network_manager.udp_layer.close()
    pygame.quit()