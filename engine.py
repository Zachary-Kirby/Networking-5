import pygame
from network_manager import NetworkManager
from message_manager import MessageManager
from udp_layer import UDPLayer

PORT = 59277
CONNECTION_TABLE = [[("127.0.0.1", PORT)], []]

class Engine:
  
  
  def __init__(self, is_server = False):
    self.window_size = [640, 640]
    self.window = pygame.display.set_mode(self.window_size)
    if is_server: pygame.display.set_caption("server")
    
    self.exit_game = False
    self.clock = pygame.time.Clock()
    self.fps = 60
    self.message_manager = MessageManager()
    self.network_manager = NetworkManager(udp_layer=UDPLayer(is_server, CONNECTION_TABLE[is_server]))
    
    
  
  
  
  
  def run(self):
    
    #TODO make this a button in a menu with an IP address box
    if not self.network_manager.udp_layer.is_server:
      self.network_manager.initiate_connection()
    
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
          self.network_manager.server_update()
          if keys[pygame.K_f]:
            self.network_manager.server_spawn_red_enemy(*pygame.mouse.get_pos())
        else:
          if self.network_manager.player_id:
            self.network_manager.client_input(self.network_manager.player_id, keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_w], keys[pygame.K_s])
        
        self.network_manager.send()
        
        #GRAPHICS
        self.window.fill((0,0,0))
        
        
        
        for enemy in self.network_manager.enemies:
          #print(enemy.id)
          enemy.draw(self.window)
        
        for i in range(len(self.network_manager.players)):
          self.window.fill((127,127,255), pygame.Rect(self.network_manager.players[i].position, pygame.Vector2(16,16)))
        
        pygame.display.update()
        self.clock.tick(self.fps)
    except KeyboardInterrupt:
      self.exit_game = True
  
  
  def close(self):
    self.network_manager.udp_layer.close()
    pygame.quit()