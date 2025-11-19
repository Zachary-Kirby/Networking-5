import pygame
from typing import Optional

class RedEnemy:
  def __init__(self, id, x, y):
    self.id = id
    self.position = pygame.Vector2(x, y)
    self.last_tick_position = self.position.copy()
    self.velocity = pygame.Vector2(0, 0)
    self.target: Optional[pygame.Vector2] = None
    self.enemies: Optional[list["RedEnemy"]] = None
    self.dash_timer = 0
    self.dash_time = 240
  
  def update(self):
    if self.velocity.length_squared() < 5*5:
      self.dash_timer += 1
    
    if self.velocity.length_squared() > 0:
      self.position += self.velocity.normalize() * min(self.velocity.length(), 10)
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
    self.velocity *= 0.9
  
  def draw(self, window: pygame.Surface):
    draw_rect = pygame.Rect(self.position.x-2, self.position.y-2, 4, 4)
    pygame.draw.rect(window, (0xff,0x44,0x44), draw_rect)