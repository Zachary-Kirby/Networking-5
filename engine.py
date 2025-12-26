import pygame
from network_manager import NetworkManager
from message_manager import MessageManager
from udp_layer import UDPLayer

PORT = 59277
CONNECTION_TABLE = [[("127.0.0.1", PORT)], []]

class Engine:
  
  
  def __init__(self, is_server = False):
    #this should be stuff available to both the client and the server sides of things
    self.window_size = [640, 640]
    self.window = pygame.display.set_mode(self.window_size)
    if is_server: pygame.display.set_caption("server")
    
    self.exit_game = False
    self.clock = pygame.time.Clock()
    self.fps = 60
    self.message_manager = MessageManager()
    # (Change) now server has a client network manager too since it is a client
    self.network_manager = NetworkManager(udp_layer=UDPLayer(False, CONNECTION_TABLE[0])) 
    self.hosting = is_server
    if self.hosting:
      # (Change) now the server has a host network manager with the real objects
      self.host = NetworkManager(udp_layer=UDPLayer(is_server, CONNECTION_TABLE[is_server]))
  
  def run(self):
    
    #TODO make this a button in a menu with an IP address box
    # (Change) this now should always be connecting since even the host is a client to itself
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
        
        # (Change) Always ran for since host will also recieve from itself
        self.network_manager.receive()
        
        
        # (Change) do host logic if a hosting
        if self.hosting:
          self.host.receive()
          # (Change) no longer will the server send inputs directly to itself like this. It will do
          # the same as any other client
          #self.network_manager.server_input(0, keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_w], keys[pygame.K_s])
          self.host.server_update()
          # TODO this should be relitive to the host player if I want this to continue to exist
          if keys[pygame.K_f]:
            self.host.server_spawn_red_enemy(*pygame.mouse.get_pos())
        
        # (Change) Host now is a client of itself so this is always ran as soon as the 'client' recieves the player id
        if self.network_manager.player_id != None:
          
          #TODO make this send inputs twice and with a timestamp to let the server not repeat inputs
          #and to give some reliability to inputs
          self.network_manager.client_input(self.network_manager.player_id, keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_w], keys[pygame.K_s])
        
        self.network_manager.send()
        if self.hosting:
          self.host.send()
        # (Change) if this is a host it needs to send a message too
        
        
        #GRAPHICS 
        self.window.fill((0,0,0))
        
        print(self.host.players)
        
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
    #TODO make this less intrusive on the network managers
    if self.hosting:
      self.host.udp_layer.close()
    self.network_manager.udp_layer.close()
    pygame.quit()