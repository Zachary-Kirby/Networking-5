import pygame
from network_manager import NetworkManager
from message_manager import MessageManager
from udp_layer import UDPLayer
import time

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
    self.fps = 240
    self.message_manager = MessageManager()
    self.network_manager = NetworkManager(udp_layer=UDPLayer(False, CONNECTION_TABLE[0])) 
    
    
    
    self.hosting = is_server
    self.host_send_interval = 1/20
    if self.hosting:
      self.host_last_sent_timestamp = time.monotonic() - self.host_send_interval
      self.host = NetworkManager(udp_layer=UDPLayer(is_server, CONNECTION_TABLE[is_server]))
    
    #TODO this is actually exploitable, but probably an easy fix
    self.client_send_interval = self.host_send_interval
    self.client_last_sent_timestamp = time.monotonic() - self.client_send_interval
  
  def run(self):
    
    #TODO make this a button in a menu with an IP address box
    self.network_manager.initiate_connection()
    
    try:
      while not self.exit_game:
        self.message_manager.clear()
        #INPUT
        for event in pygame.event.get():
          if event.type == pygame.QUIT:
            self.exit_game = True
        
        keys = pygame.key.get_pressed()
        
        
        
        
        #NETWORK
        
        
        self.network_manager.receive()
        
        if self.hosting and time.monotonic() - self.host_last_sent_timestamp >= self.host_send_interval:
          self.host.receive()
          self.host.server_update()
          # TODO this should be relative to the host player if I want this to continue to exist
          if keys[pygame.K_f]:
            self.host.server_spawn_red_enemy(*pygame.mouse.get_pos())
          
          self.host.send()
          self.host_last_sent_timestamp = time.monotonic()
        
        #Player code (TODO move player code out of the main loop)
        if self.network_manager.player_id != None and time.monotonic() - self.client_last_sent_timestamp >= self.client_send_interval:
          #TODO make this send inputs twice and with a timestamp to let the server not repeat inputs
          #and to give some reliability to inputs
          self.network_manager.client_input(self.network_manager.player_id, keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_w], keys[pygame.K_s])
          player = self.network_manager.players[self.network_manager.player_id]
          self.client_last_sent_timestamp = time.monotonic()
        
        
          self.network_manager.send()
        
        
        
        
        #GRAPHICS 
        self.window.fill((0,0,0))
        
        for enemy in self.network_manager.enemies:
          enemy.draw(self.window, self.host_send_interval)
        
        for i in range(len(self.network_manager.players)):
          player = self.network_manager.players[i]
          interpolated_position = player.previous_position + (player.position - player.previous_position) * (time.monotonic() - player.previous_update_time) / self.host_send_interval
          self.window.fill((127,127,255), pygame.Rect(interpolated_position, pygame.Vector2(16,16)))
        
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