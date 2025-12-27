import pygame
from typing import Optional
import time

class RedEnemy:
  def __init__(self, id, x, y):
    self.id = id
    self.previous_update_time = time.monotonic()
    self.position = pygame.Vector2(x, y)
    self.previous_position = self.position.copy()
    self.last_tick_position = self.position.copy()
    self.velocity = pygame.Vector2(0, 0)
    self.target: Optional[pygame.Vector2] = None
    self.enemies: Optional[list["RedEnemy"]] = None
    self.dash_timer = 0
    self.dash_time = 50
  
  def update(self, delta = 1/20):
    if self.velocity.length_squared() < 5*5 * delta * delta:
      self.dash_timer += 1 * delta
    
    if self.velocity.length_squared() > 0:
      self.position += self.velocity.normalize() * min(self.velocity.length(), 10*3)
    if self.enemies:
      for enemy in self.enemies:
        dif = (enemy.position - self.position)
        l = dif.dot(dif)
        if l != 0:
          self.velocity -= dif / l * 16
    if self.target:
      dif = (self.target - self.position)
      l = dif.dot(dif)
      self.velocity += dif * 0.1
      if l != 0 and self.dash_timer <= self.dash_time:
        self.velocity -= (self.target - self.position) / l * 1000
      if l < 16*16:
        self.dash_timer = 0
    self.velocity *= pow(0.02, delta)
  
  def draw(self, window: pygame.Surface, server_update_interval): #TODO what about dropped packets?
    interpolated_position = self.previous_position + (self.position - self.previous_position) * (time.monotonic() - self.previous_update_time) / server_update_interval
    draw_rect = pygame.Rect(interpolated_position.x-2, interpolated_position.y-2, 4, 4)
    pygame.draw.rect(window, (0xff,0x44,0x44), draw_rect)